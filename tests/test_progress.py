import http.client
import json
import os
import signal
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import app


def message(payload, reason="stop", role="assistant"):
    return {"type": "message_end", "message": {"role": role, "stopReason": reason, "content": [
        {"type": "thinking", "thinking": "PRIVATE REASONING"},
        {"type": "text", "text": json.dumps(payload)},
    ]}}


def progress(step="lodging", state="working", following="budget"):
    return {"type": "tool_execution_start", "toolName": "bash", "args": {
        "command": '# wanderplan-progress: ' + json.dumps({"step": step, "state": state, "next": following}) + '\nPRIVATE COMMAND BODY',
    }}


class ProgressTest(unittest.TestCase):
    def setUp(self):
        with app.JOBS_LOCK:
            app.JOBS.clear()
            app.ACTIVE_JOB = None

    def start_paused_job(self):
        with patch.object(app.threading.Thread, "start"):
            return app.launch_job({"prompt": "A travel request"})

    def test_only_allowlisted_public_updates_reach_snapshot(self):
        job_id = self.start_paused_job()
        app.update_progress(job_id, {"type": "message_update", "assistantMessageEvent": {"type": "thinking_delta", "delta": "PRIVATE THOUGHT"}})
        app.update_progress(job_id, {"type": "tool_execution_end", "result": {"secret": "PRIVATE TOOL OUTPUT"}})
        app.update_progress(job_id, message({"progress": {"step": "lodging", "state": "working", "next": "budget"}}, role="toolResult"))
        app.update_progress(job_id, message({"progress": {"step": "lodging", "state": "working", "next": "budget", "message": "SECRET"}}))
        rejected = progress()
        rejected['args']['command'] = '# wanderplan-progress: {"step":"lodging","state":"working","next":"budget","message":"SECRET"}\nPRIVATE'
        app.update_progress(job_id, rejected)
        rejected['args']['command'] = '\n' + progress()['args']['command']
        app.update_progress(job_id, rejected)
        self.assertEqual(app.JOBS[job_id]["history"], [])
        self.assertEqual(app.JOBS[job_id]["current"]["title"], "Working on your request")
        app.update_progress(job_id, progress())
        app.update_progress(job_id, progress())
        with app.JOBS_LOCK:
            snapshot = app.progress_snapshot(app.JOBS[job_id])
        self.assertEqual(snapshot["title"], "Checking hotel options")
        self.assertEqual(snapshot["next"], "Building the budget")
        self.assertEqual(len(snapshot["history"]), 1)
        self.assertIsNotNone(snapshot["quiet_seconds"])
        self.assertNotIn("PRIVATE", json.dumps(snapshot))
        self.assertNotIn("SECRET", json.dumps(snapshot))

    def test_history_is_bounded_and_silence_is_not_a_heartbeat(self):
        job_id = self.start_paused_job()
        started = app.JOBS[job_id]["started"]
        with patch.object(app.time, "monotonic", return_value=started + 10):
            for index in range(20):
                app.update_progress(job_id, progress(state="blocked" if index % 2 else "working"))
        with patch.object(app.time, "monotonic", return_value=started + 80):
            snapshot = app.progress_snapshot(app.JOBS[job_id])
        self.assertEqual(len(snapshot["history"]), 6)
        self.assertEqual(snapshot["quiet_seconds"], 70)
        self.assertEqual(snapshot["elapsed_seconds"], 80)
        self.assertEqual(snapshot["title"], "Continuing research")
        self.assertIsNone(snapshot["next"])
        self.assertIn("Checking hotel options", snapshot["history"][-1]["title"])
        app.update_progress(job_id, {"type": "auto_retry_start", "errorMessage": "PRIVATE PROVIDER DETAILS"})
        self.assertEqual(app.progress_snapshot(app.JOBS[job_id])["activity"], "retry")

    def test_poll_observes_progress_before_plan_finishes(self):
        announced, release = threading.Event(), threading.Event()
        def work(request, on_event):
            on_event(progress())
            announced.set()
            release.wait(3)
            return {"question": "Which dates?"}
        server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        worker = threading.Thread(target=server.handle_request)
        try:
            with patch.object(app, "plan", side_effect=work):
                job_id = app.launch_job({"prompt": "A travel request"})
                self.assertTrue(announced.wait(2))
                worker.start()
                connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
                connection.request("GET", f"/api/plan/{job_id}")
                response = connection.getresponse()
                payload = json.loads(response.read())
                connection.close()
                self.assertEqual(response.status, 202)
                self.assertEqual(payload["progress"]["title"], "Checking hotel options")
                self.assertIsNone(app.JOBS[job_id]["result"])
        finally:
            release.set()
            worker.join(timeout=2)
            server.server_close()
            for _ in range(100):
                if app.ACTIVE_JOB is None:
                    break
                time.sleep(0.01)
        self.assertEqual(app.JOBS[job_id]["status"], "complete")
        final = app.progress_snapshot(app.JOBS[job_id])
        with patch.object(app.time, "monotonic", return_value=time.monotonic() + 100):
            self.assertEqual(app.progress_snapshot(app.JOBS[job_id]), final)

    def test_timeout_keeps_history_and_releases_job(self):
        job_id = self.start_paused_job()
        app.update_progress(job_id, progress())
        with patch.object(app, "plan", side_effect=TimeoutError):
            app.run_job(job_id, {"prompt": "A travel request"})
        self.assertEqual(app.JOBS[job_id]["status"], "failed")
        self.assertIn("time limit", app.JOBS[job_id]["error"])
        self.assertEqual(len(app.JOBS[job_id]["history"]), 1)
        self.assertIsNone(app.ACTIVE_JOB)

    def test_failed_last_message_does_not_reuse_earlier_result(self):
        with tempfile.TemporaryDirectory() as folder:
            key = Path(folder) / "key"
            key.write_text("test-key")
            for reason in ("error", "aborted", "length", "toolUse"):
                events = [message({"question": "Earlier response"}), message({}, reason)]
                with patch.dict(app.os.environ, {"OPENROUTER_KEY_FILE": str(key)}), \
                     patch.object(app, "pi_events", return_value=iter(events)), \
                     self.assertRaisesRegex(RuntimeError, "stopped before finishing"):
                    app.plan({"prompt": "A travel request"})

    def test_pure_json_fence_is_allowed_but_prose_is_not(self):
        for text in ('{"question":"Which dates?"}', '```json\n{"question":"Which dates?"}\n```'):
            self.assertEqual(app.message_json({"content": [{"type": "text", "text": text}]}),
                             {"question": "Which dates?"})
        for text in ('Here is the answer: {"question":"Which dates?"}',
                     '```json\n{"question":"Which dates?"}\n```\nExtra prose'):
            with self.assertRaises(ValueError):
                app.message_json({"content": [{"type": "text", "text": text}]})

    def test_progress_is_not_a_final_result(self):
        with tempfile.TemporaryDirectory() as folder:
            key = Path(folder) / "key"
            key.write_text("test-key")
            with patch.dict(app.os.environ, {"OPENROUTER_KEY_FILE": str(key)}), \
                 patch.object(app, "pi_events", return_value=iter([message({"progress": {"step": "lodging"}})])), \
                 self.assertRaisesRegex(RuntimeError, "incomplete itinerary"):
                app.plan({"prompt": "A travel request"})


class StreamTest(unittest.TestCase):
    def stream(self, code, timeout=3):
        return app.pi_events([sys.executable, "-u", "-c", code], env=os.environ.copy(), timeout=timeout)

    def test_streams_before_exit_and_keeps_unicode_separators_inside_json(self):
        code = "import json,time; print(json.dumps({'type':'first','text':'a\\u2028b'}, ensure_ascii=False),flush=True); time.sleep(.1); print('{\"type\":\"last\"}')"
        events = self.stream(code)
        self.assertEqual(next(events), {"type": "first", "text": "a\u2028b"})
        self.assertEqual(list(events), [{"type": "last"}])

    def test_stderr_does_not_deadlock_or_enter_events(self):
        events = list(self.stream("import os; os.write(2,b'PRIVATE'*100000); print('{\"type\":\"safe\"}')"))
        self.assertEqual(events, [{"type": "safe"}])

    def test_incomplete_stream_and_nonzero_exit_fail(self):
        for code in ("print('{',end='',flush=True)", "import sys; print('{}'); sys.exit(1)"):
            with self.assertRaises(RuntimeError):
                list(self.stream(code))

    def test_silent_timeout_terminates_the_process_group(self):
        with patch.object(app.os, "killpg", wraps=os.killpg) as killpg:
            with self.assertRaises(TimeoutError):
                list(self.stream("import time; time.sleep(10)", timeout=0.15))
        self.assertEqual(killpg.call_args.args[1], signal.SIGKILL)
        with self.assertRaises(ProcessLookupError):
            os.kill(killpg.call_args.args[0], 0)


if __name__ == "__main__":
    unittest.main()
