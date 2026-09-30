import json
import http.client
import copy
import tempfile
import threading
import time
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import app
from scripts import prepare_agent


def itinerary(days=3, start=date(2027, 4, 5)):
    return {
        "status": "complete",
        "title": "Los Angeles",
        "summary": "Two adults; displayed prices require rechecking.",
        "planning_state": {"confirmed": ["Los Angeles"], "assumptions": ["Two adults"], "unresolved": []},
        "limitations": ["Prices require rechecking"],
        "sources": [{"title": "Hotel", "url": "https://example.com/hotel", "checked_at": "2026-01-01T00:00:00Z", "confidence": "high", "notes": "Fixture only"}],
        "reservations": [],
        "budget": {
            "currency": "USD", "items": [{"category": "lodging", "description": "Two nights, one shared room", "quantity": 2, "unit_cost": 100, "total": 200, "price_status": "estimate", "source_url": ""}],
            "subtotal": 200, "contingency": 30, "total": 230, "target": 250,
            "savings": {"current_savings": 50, "contributions": 4, "monthly": 50},
            "variants": [], "notes": "Fixture, not a complete real-trip budget",
        },
        "flights": [{
            "id": "outbound", "selected": True, "origin": "SFO", "destination": "LAX",
            "date": start.isoformat(), "airline": "Example Air", "departure": "09:00",
            "arrival": "10:30", "duration": "1 hr 30 min", "stops": "Nonstop",
            "price": "$200 round trip", "price_status": "exact",
            "source_url": "https://example.com/flight", "checked_at": "2026-09-30T00:00:00Z",
            "notes": "Baggage extra",
        }],
        "lodging": [{
            "id": "hotel", "selected": True, "name": "Example Hotel", "city": "Los Angeles",
            "check_in": start.isoformat(), "check_out": (start + timedelta(days=days)).isoformat(),
            "price": "$600 total", "price_status": "exact", "source_url": "https://example.com/hotel",
            "checked_at": "2026-09-30T00:00:00Z", "notes": "Taxes included",
        }],
        "days": [{
            "date": (start + timedelta(days=index)).isoformat(), "city": "Los Angeles",
            "lodging_id": "hotel", "local_note": "Keep valuables secure.",
            "activities": [{"time": "09:00", "title": "Activity", "notes": "Plan", "url": "https://example.com"}],
        } for index in range(days)],
    }


class PlannerTest(unittest.TestCase):
    def setUp(self):
        with app.JOBS_LOCK:
            app.JOBS.clear()
            app.ACTIVE_JOB = None

    def test_api_validation_errors_are_json(self):
        server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        thread = threading.Thread(target=server.handle_request)
        thread.start()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
            connection.request("POST", "/api/plan", "{}", {"Content-Type": "text/plain"})
            response = connection.getresponse()
            data = json.loads(response.read())
            connection.close()
        finally:
            thread.join(timeout=2)
            server.server_close()

        self.assertEqual(response.status, 415)
        self.assertIn("application/json", response.getheader("Content-Type"))
        self.assertIn("application/json", data["error"])

    def test_background_job_completes(self):
        result = itinerary()
        with patch.object(app, "plan", return_value=result):
            job_id = app.launch_job({"prompt": "Los Angeles April 5–7, 2027"})
            for _ in range(100):
                with app.JOBS_LOCK:
                    job = app.JOBS[job_id]
                if job["status"] == "complete":
                    break
                time.sleep(0.01)

        self.assertEqual(job["result"], result)
        self.assertIsNone(app.ACTIVE_JOB)

    def test_calendar_polls_agent_and_renders_selected_travel(self):
        calendar = (app.ROOT / "docs/trip-calendar.html").read_text()
        self.assertIn("/api/plan/${encodeURIComponent(job.job_id)}", calendar)
        self.assertIn("item.id === day.lodging_id", calendar)
        self.assertIn("filter(item => item.selected)", calendar)
        self.assertIn("openBookings", calendar)
        self.assertIn("Browsing current flights, stays and destination sources", calendar)

    def test_plan_preloads_prepared_contract_and_separates_user_data(self):
        result = itinerary()
        completed = SimpleNamespace(returncode=0, stdout=json.dumps(result), stderr="")

        with tempfile.TemporaryDirectory() as folder:
            key = Path(folder) / "key"
            key.write_text("test-key")
            with patch.dict(app.os.environ, {"OPENROUTER_KEY_FILE": str(key)}), \
                 patch.object(app.subprocess, "run", return_value=completed) as runner:
                self.assertEqual(app.plan({"prompt": "Los Angeles April 5–7, 2027"}), result)

        command = runner.call_args.args[0]
        prompt = json.loads(command[-1])
        self.assertEqual(prompt["request"], "Los Angeles April 5–7, 2027")
        self.assertIsNone(prompt["previous_plan"])
        received = datetime.fromisoformat(prompt["request_received_at"])
        self.assertEqual(datetime.fromisoformat(prompt["research_deadline"]) - received, timedelta(seconds=330))
        self.assertEqual(datetime.fromisoformat(prompt["response_deadline"]) - received, timedelta(seconds=420))
        self.assertEqual(command[command.index("--system-prompt") + 1], str(app.SYSTEM_PROMPT))
        self.assertEqual(app.SYSTEM_PROMPT.read_text(), prepare_agent.build_prompt())
        self.assertNotIn("<spec", command[-1])
        self.assertIn("read,bash", command)
        self.assertNotIn("--mode", command)
        self.assertEqual(runner.call_args.kwargs["env"]["OPENROUTER_API_KEY"], "test-key")
        self.assertEqual(runner.call_args.kwargs["timeout"], 420)

    def test_multiple_revisions_use_latest_plan(self):
        first = itinerary()
        second = itinerary()
        second["summary"] = "More museums"
        replies = [
            SimpleNamespace(returncode=0, stdout=json.dumps(first), stderr=""),
            SimpleNamespace(returncode=0, stdout=json.dumps(second), stderr=""),
        ]
        with tempfile.TemporaryDirectory() as folder:
            key = Path(folder) / "key"
            key.write_text("test-key")
            with patch.dict(app.os.environ, {"OPENROUTER_KEY_FILE": str(key)}), \
                 patch.object(app.subprocess, "run", side_effect=replies) as runner:
                current = app.plan({"prompt": "Los Angeles April 5–7, 2027"})
                app.plan({"prompt": "Add more museums", "previous": current})

        prompt = json.loads(runner.call_args.args[0][-1])
        self.assertEqual(prompt["request"], "Add more museums")
        self.assertEqual(prompt["previous_plan"], first)
        self.assertEqual(prompt["previous_plan"]["planning_state"]["assumptions"], ["Two adults"])

    def test_prepared_browser_sources_are_complete_and_offline(self):
        snapshot = (app.ROOT / "agent/browser-nodes.md").read_text()
        for node_id in prepare_agent.NODES:
            self.assertEqual(snapshot.count(f"Node: `{node_id}`"), 1)
        self.assertEqual(snapshot.count("Updated: `"), len(prepare_agent.NODES))
        prompt = app.SYSTEM_PROMPT.read_text()
        self.assertLess(prompt.index("# Wanderbot"), prompt.index("# Browser Runtime Compatibility"))
        self.assertLess(prompt.index("# Browser Runtime Compatibility"), prompt.index("# Browser reference snapshots"))
        self.assertEqual(prompt, prepare_agent.build_prompt())
        with self.assertRaises(ValueError):
            prepare_agent.render_nodes([])

    def test_exploration_and_partial_do_not_need_fabricated_dates(self):
        for status in ("exploring", "partial"):
            result = itinerary()
            result.update(status=status, days=[], flights=[], lodging=[], budget=None)
            result["planning_state"]["unresolved"] = ["Choose a destination"]
            self.assertEqual(app.validate_result(result), result)
        result["status"] = "complete"
        with self.assertRaises(ValueError):
            app.validate_result(result)

    def test_budget_arithmetic_unknowns_and_savings(self):
        baseline = itinerary()
        for field, value in (("subtotal", 199), ("total", 999), ("target", 100)):
            result = copy.deepcopy(baseline)
            result["budget"][field] = value
            with self.assertRaises(ValueError):
                app.validate_result(result)
        result = copy.deepcopy(baseline)
        result["budget"]["savings"]["monthly"] = 10
        with self.assertRaises(ValueError):
            app.validate_result(result)
        result = copy.deepcopy(baseline)
        result["budget"]["items"][0].update(unit_cost=None, total=None, price_status="unavailable")
        with self.assertRaises(ValueError):
            app.validate_result(result)
        result["status"] = "partial"
        result["budget"].update(subtotal=None, total=None, target=None, savings=None)
        self.assertEqual(app.validate_result(result), result)
        result["budget"]["items"][0]["quantity"] = None
        result["budget"]["contingency"] = None
        self.assertEqual(app.validate_result(result), result)
        result["budget"]["items"][0]["price_status"] = "estimate"
        with self.assertRaises(ValueError):
            app.validate_result(result)

    def test_lodging_checkout_is_not_a_paid_night(self):
        result = itinerary()
        result["lodging"][0]["check_out"] = result["days"][-1]["date"]
        with self.assertRaisesRegex(ValueError, "lodging reference"):
            app.validate_result(result)
        result["days"][-1]["lodging_id"] = ""
        self.assertEqual(app.validate_result(result), result)

    def test_rejects_malformed_evidence_and_request(self):
        for request in ([], None, "trip"):
            with self.assertRaises(ValueError):
                app.validate_request(request)
        for key, value in (("url", "javascript:alert(1)"), ("confidence", "certain"), ("checked_at", "2099-01-01T00:00:00Z")):
            result = itinerary()
            result["sources"][0][key] = value
            with self.assertRaises(ValueError):
                app.validate_result(result)

    def test_accepts_thirty_consecutive_days(self):
        self.assertEqual(len(app.validate_result(itinerary(30))["days"]), 30)

    def test_rejects_more_than_thirty_days(self):
        with self.assertRaisesRegex(ValueError, "Invalid itinerary"):
            app.validate_result(itinerary(31))

    def test_rejects_untrusted_source_url(self):
        result = itinerary()
        result["flights"][0]["source_url"] = "javascript:alert(1)"
        with self.assertRaisesRegex(ValueError, "Invalid flight"):
            app.validate_result(result)

    def test_clarification_passes_without_travel_arrays(self):
        self.assertEqual(app.validate_result({"question": "What dates are you traveling?"}),
                         {"question": "What dates are you traveling?"})


if __name__ == "__main__":
    unittest.main()
