import json
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
