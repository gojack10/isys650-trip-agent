import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import app


class PlannerTest(unittest.TestCase):
    def test_plan_and_global_limit(self):
        itinerary = {"title": "Rome", "summary": "Estimates only", "days": [
            {"date": f"2027-04-0{i}", "city": "Rome", "activities": []} for i in range(5, 8)
        ]}
        response = {"choices": [{"message": {"content": json.dumps(itinerary)}}]}

        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self, *_): return json.dumps(response).encode()

        with tempfile.TemporaryDirectory() as folder:
            key = Path(folder) / "key"
            key.write_text("test-key")
            with patch.object(app, "QUOTA", Path(folder) / "quota.json"), \
                 patch.object(app, "LIMIT", 1), \
                 patch.dict(app.os.environ, {"OPENROUTER_KEY_FILE": str(key)}), \
                 patch.object(app, "urlopen", return_value=FakeResponse()) as upstream:
                self.assertEqual(app.plan({"prompt": "Rome April 5–7, 2027"}), itinerary)
                payload = json.loads(upstream.call_args.args[0].data)
                self.assertEqual(payload["model"], "deepseek/deepseek-v4.1-flash")
                self.assertEqual(payload["reasoning"]["effort"], "high")
                self.assertNotIn("max_tokens", payload)
                self.assertEqual(payload["plugins"][0]["max_results"], 10)
                with self.assertRaisesRegex(ValueError, "limit"):
                    app.plan({"prompt": "Another trip request"})
                self.assertEqual(upstream.call_count, 1)

    def test_multiple_revisions_use_latest_plan(self):
        itinerary = {"title": "Rome", "summary": "Estimates only", "days": [
            {"date": f"2027-04-0{i}", "city": "Rome", "activities": []} for i in range(5, 8)
        ]}
        response = {"choices": [{"message": {"content": json.dumps(itinerary)}}]}

        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self, *_): return json.dumps(response).encode()

        with tempfile.TemporaryDirectory() as folder:
            key = Path(folder) / "key"
            key.write_text("test-key")
            with patch.object(app, "QUOTA", Path(folder) / "quota.json"), \
                 patch.object(app, "LIMIT", 3), \
                 patch.dict(app.os.environ, {"OPENROUTER_KEY_FILE": str(key)}), \
                 patch.object(app, "urlopen", return_value=FakeResponse()) as upstream:
                first = app.plan({"prompt": "Rome April 5–7, 2027"})
                second = app.plan({"prompt": "Add more museums", "previous": first})
                app.plan({"prompt": "Make day two less busy", "previous": second})

                self.assertEqual(upstream.call_count, 3)
                last_payload = json.loads(upstream.call_args.args[0].data)
                last_prompt = last_payload["messages"][1]["content"]
                self.assertIn("Previous itinerary:", last_prompt)
                self.assertIn("Revision requested: Make day two less busy", last_prompt)

    def test_accepts_every_day_in_a_fifteen_day_trip(self):
        start = date(2027, 4, 5)
        itinerary = {"title": "Italy", "summary": "15-day draft", "days": [
            {"date": (start + timedelta(days=index)).isoformat(), "city": "Rome", "activities": []}
            for index in range(15)
        ]}
        response = {"choices": [{"message": {"content": json.dumps(itinerary)}}]}

        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self, *_): return json.dumps(response).encode()

        with tempfile.TemporaryDirectory() as folder:
            key = Path(folder) / "key"
            key.write_text("test-key")
            with patch.object(app, "QUOTA", Path(folder) / "quota.json"), \
                 patch.dict(app.os.environ, {"OPENROUTER_KEY_FILE": str(key)}), \
                 patch.object(app, "urlopen", return_value=FakeResponse()):
                result = app.plan({"prompt": "Plan Rome from April 5 through April 19, 2027"})

        self.assertEqual(len(result["days"]), 15)
        self.assertEqual(result["days"][0]["date"], "2027-04-05")
        self.assertEqual(result["days"][-1]["date"], "2027-04-19")


if __name__ == "__main__":
    unittest.main()
