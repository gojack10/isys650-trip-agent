"""Opt-in live-provider trial, never run by unittest discovery.

Inside the test image: uv run --no-project python /tmp/agent_trial.py /tmp/evidence
Saves real Pi JSONL events and validated results. Requires the server's test key.
"""
import json
import subprocess
import sys
from pathlib import Path

import app


def main():
    output = Path(sys.argv[1])
    output.mkdir(parents=True, exist_ok=True)
    native_run = subprocess.run
    scenario = ""
    events = []

    def recorded_run(command, **kwargs):
        # Same app.plan path and prepared prompt; JSON mode is trial instrumentation only.
        command = [*command[:-1], "--mode", "json", command[-1]]
        (output / f"{scenario}.request.json").write_text(command[-1])
        kwargs.pop("capture_output")
        trace = output / f"{scenario}.jsonl"
        errors = output / f"{scenario}.stderr"
        # Stream to files so a timeout still leaves the actual partial evidence.
        with trace.open("w") as stdout, errors.open("w") as stderr:
            completed = native_run(command, stdout=stdout, stderr=stderr, **kwargs)
        events[:] = [json.loads(line) for line in trace.read_text().splitlines() if line.strip()]
        messages = [event["message"] for event in events if event.get("type") == "message_end"
                    and event.get("message", {}).get("role") == "assistant"]
        if not messages or messages[-1].get("stopReason") in {"error", "aborted"}:
            raise RuntimeError("Live agent did not finish successfully; inspect saved events")
        text = "\n".join(part["text"] for part in messages[-1]["content"] if part["type"] == "text")
        return subprocess.CompletedProcess(command, completed.returncode, text, errors.read_text())

    app.subprocess.run = recorded_run
    previous = None
    cases = [
        ("clarification", "Help me plan a trip."),
        ("budget-first", "Two adults sharing a room, leaving San Francisco, USD 2500 total for four days sometime next spring. We are flexible about destination and dates. Suggest two realistic destinations and tradeoffs; keep dates open, no dated calendar or claimed dated availability."),
        ("dated-trip", "Plan for two adults sharing a midrange room, SFO to Los Angeles October 15-17, 2026, returning to SFO. Budget USD 2500 for everything. Research flight and hotel choices, realistic activities and local transit, including one hidden gem. We have USD 300 saved and two contributions remaining; calculate monthly savings. Include sources and disclose unavailable prices."),
        ("revision", "Change this trip: no flights. We will drive our own car, prefer free activities, and still want Los Angeles, the same dates, two adults and the USD 2500 ceiling. Recalculate transport, schedule and the savings plan; preserve the hotel unless it no longer fits."),
        ("uncertainty", "Do not browse on this turn. Correct the prior draft using only its recorded evidence. Remove flights, preserve confirmed dates and party, and show a useful estimated plan. Do not treat an unknown hotel price unit as a verified nightly rate."),
    ]
    for scenario, request in cases:
        if len(sys.argv) > 2 and scenario not in sys.argv[2:]:
            continue
        if scenario == "revision" and previous is None:
            previous = json.loads((output / "dated-trip.result.json").read_text())
        state = previous if scenario == "revision" else None
        if scenario == "uncertainty":
            state = {
                "title": "Incomplete LA draft",
                "planning_state": {"confirmed": ["Two adults", "Los Angeles October 15–17, 2026", "USD 2500 ceiling"], "assumptions": [], "unresolved": []},
                "lodging": [{"name": "Example Hotel", "price": "USD 158 displayed", "notes": "No source retained; nightly vs whole-stay unit, traveler count, dates and taxes were never verified."}],
                "summary": "No other live evidence is available. Any costs are planning assumptions, not verified quotes.",
            }
        result = app.plan({"prompt": request, "previous": state})
        (output / f"{scenario}.result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        commands = [event.get("args", {}).get("command", "") for event in events if event.get("type") == "tool_execution_start"]
        browsing = sum("browser-harness" in command for command in commands)
        if scenario == "clarification":
            assert result.get("question") and not browsing, "Clarification must not browse"
        elif scenario == "budget-first":
            assert result["status"] == "exploring" and not result["days"], "Flexible dates must not become an invented calendar"
            assert result["planning_state"]["unresolved"], "Exploration must expose the next choice"
        elif scenario == "dated-trip":
            assert browsing and result["sources"], "Need observed browser work and evidence"
            assert [day["date"] for day in result["days"]] == ["2026-10-15", "2026-10-16", "2026-10-17"]
            assert result["budget"] and result["budget"]["savings"], "Need budget and savings"
            previous = result
        elif scenario == "uncertainty":
            assert not browsing and result["status"] == "partial", "Unknown required evidence must not become complete"
            prices = [item["price_status"] for item in result["lodging"]]
            if result["budget"]:
                prices += [item["price_status"] for item in result["budget"]["items"] if item["category"] == "lodging"]
            assert "exact" not in prices, "Unknown units must not become exact prices"
        else:
            assert not any(flight["selected"] for flight in result["flights"]), "No-flights override must propagate"
            assert [day["date"] for day in result["days"]] == [day["date"] for day in previous["days"]]
            assert result["budget"] and result["budget"]["savings"], "Revised budget and savings required"
        print(json.dumps({"scenario": scenario, "status": result.get("status", "question"), "browser_calls": browsing,
                          "summary": result.get("summary", result.get("question"))}), flush=True)


if __name__ == "__main__":
    main()
