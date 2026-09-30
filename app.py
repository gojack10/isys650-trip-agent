"""Small public trip-planning demo; the API key never reaches the browser."""
import json
import math
import os
import secrets
import selectors
import signal
import subprocess
import sys
import threading
import time
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
MODEL = "deepseek/deepseek-v4.1-flash"
SYSTEM_PROMPT = ROOT / "agent/prompt.md"
JOBS = {}
JOBS_LOCK = threading.Lock()
ACTIVE_JOB = None
PROGRESS_STEPS = {
    "understanding": "Reviewing your request",
    "exploring": "Comparing trip options",
    "transport": "Checking transport options",
    "lodging": "Checking hotel options",
    "activities": "Researching activities and local advice",
    "budget": "Building the budget",
    "review": "Checking the itinerary",
}


def validate_request(request):
    if not isinstance(request, dict):
        raise ValueError("Send a trip request object.")
    prompt = request.get("prompt")
    previous = request.get("previous")
    if not isinstance(prompt, str) or not 4 <= len(prompt.strip()) <= 1200:
        raise ValueError("Describe the trip in 4–1200 characters.")
    if previous is not None and (not isinstance(previous, dict) or len(json.dumps(previous)) > 100000):
        raise ValueError("Invalid previous itinerary.")
    return {"prompt": prompt.strip(), "previous": previous}


def agent_prompt(request, timeout=420):
    now = datetime.now(timezone.utc)
    return json.dumps({
        "request": request["prompt"],
        "previous_plan": request["previous"],
        "request_received_at": now.isoformat(),
        "research_deadline": (now + timedelta(seconds=max(0, timeout - 90))).isoformat(),
        "response_deadline": (now + timedelta(seconds=timeout)).isoformat(),
    }, ensure_ascii=False)


def valid_url(value):
    parsed = urlparse(value)
    return value == "" or (parsed.scheme in {"http", "https"} and bool(parsed.netloc))


def strings(value):
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def amount(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def validate_context(result):
    state = result.get("planning_state")
    if not isinstance(state, dict) or not all(strings(state.get(key)) for key in ("confirmed", "assumptions", "unresolved")):
        raise ValueError("Invalid planning state")
    if not strings(result.get("limitations")):
        raise ValueError("Invalid limitations")
    for name, fields in (("sources", ("title", "url", "checked_at", "confidence", "notes")),
                         ("reservations", ("title", "notes", "url"))):
        rows = result.get(name)
        if not isinstance(rows, list) or len(rows) > 150:
            raise ValueError(f"Invalid {name}")
        for row in rows:
            if not isinstance(row, dict) or not all(isinstance(row.get(key), str) for key in fields) or not valid_url(row["url"]):
                raise ValueError(f"Invalid {name}")
            if name == "sources":
                if row["confidence"] not in {"high", "medium", "low"}:
                    raise ValueError("Invalid source confidence")
                if row["checked_at"]:
                    stamp = datetime.fromisoformat(row["checked_at"].replace("Z", "+00:00"))
                    if stamp.tzinfo is None or stamp > datetime.now(timezone.utc) + timedelta(minutes=1):
                        raise ValueError("Invalid source timestamp")
    if "budget" not in result:
        raise ValueError("Missing budget")
    budget = result["budget"]
    if budget is None:
        return
    if not isinstance(budget, dict) or not isinstance(budget.get("currency"), str) or len(budget["currency"]) != 3:
        raise ValueError("Invalid budget currency")
    if not isinstance(budget.get("notes"), str) or not strings(budget.get("variants")):
        raise ValueError("Invalid budget notes")
    items = budget.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        raise ValueError("Invalid budget items")
    unknown = False
    for item in items:
        if not isinstance(item, dict) or not all(isinstance(item.get(key), str) for key in ("category", "description", "price_status", "source_url")):
            raise ValueError("Invalid budget item")
        if not valid_url(item["source_url"]):
            raise ValueError("Invalid budget item")
        if not amount(item.get("quantity")) and not (item["price_status"] == "unavailable" and item.get("quantity") is None):
            raise ValueError("Invalid budget quantity")
        if item["price_status"] == "unavailable":
            if item.get("unit_cost") is not None or item.get("total") is not None:
                raise ValueError("Unavailable costs must not be invented")
            unknown = True
            continue
        if item["price_status"] not in {"exact", "from", "range", "estimate", "free"}:
            raise ValueError("Invalid price status")
        if not amount(item.get("unit_cost")) or not amount(item.get("total")) or abs(item["quantity"] * item["unit_cost"] - item["total"]) > 0.02:
            raise ValueError("Budget line does not reconcile")
    if not amount(budget.get("contingency")) and not (unknown and budget.get("contingency") is None):
        raise ValueError("Invalid contingency")
    if unknown:
        if any(budget.get(key) is not None for key in ("subtotal", "total", "target", "savings")):
            raise ValueError("Unknown costs cannot produce a complete budget")
        return
    if not all(amount(budget.get(key)) for key in ("subtotal", "total", "target")):
        raise ValueError("Invalid budget totals")
    if (abs(sum(item["total"] for item in items) - budget["subtotal"]) > 0.02
            or abs(budget["subtotal"] + budget["contingency"] - budget["total"]) > 0.02
            or budget["target"] < budget["total"]):
        raise ValueError("Budget totals do not reconcile")
    savings = budget.get("savings")
    if savings is not None:
        if (not isinstance(savings, dict) or not amount(savings.get("current_savings"))
                or type(savings.get("contributions")) is not int or savings["contributions"] <= 0
                or not amount(savings.get("monthly"))):
            raise ValueError("Invalid savings inputs")
        expected = max(0, budget["target"] - savings["current_savings"]) / savings["contributions"]
        if not -0.000001 <= savings["monthly"] - expected <= 0.010001:
            raise ValueError("Savings do not reconcile")


def validate_result(result):
    if not isinstance(result, dict):
        raise ValueError("Invalid planner result")
    if "question" in result:
        if not isinstance(result["question"], str):
            raise ValueError("Invalid clarification")
        return {"question": result["question"][:400]}
    if not isinstance(result.get("title"), str) or not isinstance(result.get("summary"), str):
        raise ValueError("Invalid itinerary")
    days = result.get("days")
    flights = result.get("flights")
    lodging = result.get("lodging")
    status = result.get("status")
    if status not in {"complete", "partial", "exploring"}:
        raise ValueError("Invalid planning status")
    if not isinstance(days, list) or not (1 if status == "complete" else 0) <= len(days) <= 30:
        raise ValueError("Invalid itinerary")
    validate_context(result)
    if not isinstance(flights, list) or len(flights) > 30 or not isinstance(lodging, list) or len(lodging) > 20:
        raise ValueError("Invalid travel options")

    statuses = {"exact", "from", "range", "estimate", "free", "unavailable"}
    ids = set()
    flight_fields = (
        "id", "origin", "destination", "date", "airline", "departure", "arrival", "duration",
        "stops", "price", "price_status", "source_url", "checked_at", "notes",
    )
    for flight in flights:
        if not isinstance(flight, dict) or not isinstance(flight.get("selected"), bool):
            raise ValueError("Invalid flight")
        if not all(isinstance(flight.get(field), str) for field in flight_fields):
            raise ValueError("Invalid flight")
        date.fromisoformat(flight["date"])
        if flight["id"] in ids or flight["price_status"] not in statuses or not valid_url(flight["source_url"]):
            raise ValueError("Invalid flight")
        ids.add(flight["id"])

    lodging_ids = set()
    lodging_fields = (
        "id", "name", "city", "check_in", "check_out", "price", "price_status", "source_url",
        "checked_at", "notes",
    )
    for stay in lodging:
        if not isinstance(stay, dict) or not isinstance(stay.get("selected"), bool):
            raise ValueError("Invalid lodging")
        if not all(isinstance(stay.get(field), str) for field in lodging_fields):
            raise ValueError("Invalid lodging")
        date.fromisoformat(stay["check_in"])
        date.fromisoformat(stay["check_out"])
        if (stay["check_out"] <= stay["check_in"] or stay["id"] in lodging_ids
                or stay["price_status"] not in statuses or not valid_url(stay["source_url"])):
            raise ValueError("Invalid lodging")
        lodging_ids.add(stay["id"])

    itinerary_dates = []
    for day in days:
        if not isinstance(day, dict):
            raise ValueError("Invalid day")
        itinerary_dates.append(date.fromisoformat(day["date"]))
        if not all(isinstance(day.get(field), str) for field in ("city", "lodging_id", "local_note")):
            raise ValueError("Invalid day")
        if day["lodging_id"]:
            stay = next((item for item in lodging if item["id"] == day["lodging_id"]), None)
            if not stay or not stay["selected"] or not stay["check_in"] <= day["date"] < stay["check_out"]:
                raise ValueError("Invalid lodging reference")
        if not isinstance(day.get("activities"), list) or len(day["activities"]) > 12:
            raise ValueError("Invalid day")
        for activity in day["activities"]:
            if not isinstance(activity, dict) or not all(
                isinstance(activity.get(field), str) for field in ("time", "title", "notes", "url")
            ) or not valid_url(activity["url"]):
                raise ValueError("Invalid activity")
    if any(current != previous + timedelta(days=1)
           for previous, current in zip(itinerary_dates, itinerary_dates[1:])):
        raise ValueError("Itinerary dates must be consecutive")
    return result


def pi_events(command, *, env, timeout):
    """Consume JSONL without pipe deadlocks; EOF + successful process exit owns completion."""
    deadline = time.monotonic() + timeout
    # No raw stderr or event contents are exposed to users or persisted by default.
    with subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          start_new_session=True) as process:
        try:
            pending = b""
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0 or not selector.select(remaining):
                        raise TimeoutError("Planning agent timed out.")
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        if pending.strip():
                            raise RuntimeError("Incomplete agent event stream.")
                        break
                    pending += chunk
                    while b"\n" in pending:
                        line, pending = pending.split(b"\n", 1)
                        if line.strip():
                            event = json.loads(line)
                            if not isinstance(event, dict):
                                raise RuntimeError("Invalid agent event.")
                            yield event
                    if len(pending) > 2_000_000:
                        raise RuntimeError("Agent event exceeds the supported size.")
            if process.wait(timeout=max(0.001, deadline - time.monotonic())):
                raise RuntimeError("Planning agent failed.")
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError("Planning agent timed out.") from exc
        finally:
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()


def message_json(message):
    text = "\n".join(part["text"] for part in message.get("content", []) if part.get("type") == "text").strip()
    # Some models fence an otherwise pure JSON answer. Do not salvage JSON from prose.
    if text.startswith("```json\n") and text.endswith("\n```"):
        text = text[len("```json\n"):-len("\n```")].strip()
    return json.loads(text)


def update_progress(job_id, event):
    kind = event.get("type")
    if kind not in {"agent_start", "message_start", "message_update", "message_end",
                    "tool_execution_start", "tool_execution_update", "tool_execution_end",
                    "auto_retry_start", "auto_retry_end"}:
        return
    with JOBS_LOCK:
        job = JOBS[job_id]
        if job["status"] != "researching":
            return
        now = time.monotonic()
        job["last_activity"] = now
        if job["current"]["title"] == "Starting planner":
            job["current"]["title"] = "Working on your request"
        if kind.startswith("tool_execution"):
            job["activity"] = "tool"
        elif kind == "auto_retry_start":
            job["activity"] = "retry"
        elif kind in {"message_start", "message_update", "message_end", "auto_retry_end"}:
            job["activity"] = "model"
        if kind != "tool_execution_start" or event.get("toolName") != "bash":
            return
        command = event.get("args", {}).get("command", "")
        if not isinstance(command, str):
            return
        header = command.partition("\n")[0]
        prefix = "# wanderplan-progress: "
        if not header.startswith(prefix):
            return
        try:
            update = json.loads(header[len(prefix):])
        except ValueError:
            return
        if not isinstance(update, dict) or set(update) != {"step", "state", "next"}:
            return
        step, state, following = update["step"], update["state"], update["next"]
        if (not isinstance(step, str) or step not in PROGRESS_STEPS
                or state not in ("working", "blocked")
                or (following is not None and (not isinstance(following, str) or following not in PROGRESS_STEPS))):
            return
        title = PROGRESS_STEPS[step]
        if state == "blocked":
            title += " — some evidence is unavailable"
        current = {"title": title, "next": PROGRESS_STEPS.get(following), "state": state}
        if current != job["current"]:
            job["current"] = current
            job["stage_at"] = now
            job["history"].append({"elapsed_seconds": int(now - job["started"]), "title": title})
            job["history"] = job["history"][-6:]


def progress_snapshot(job):
    now = job.get("finished", time.monotonic())
    current = job["current"]
    # A task label is self-reported intent, not a durable claim about current work.
    if job["status"] == "researching" and job["stage_at"] is not None and now - job["stage_at"] > 60:
        current = {"title": "Continuing research", "next": None, "state": "working"}
    return {
        **current,
        "elapsed_seconds": max(0, int(now - job["started"])),
        "quiet_seconds": None if job["last_activity"] is None else max(0, int(now - job["last_activity"])),
        "activity": job["activity"],
        "history": list(job["history"]),
    }


def plan(request, on_event=None):
    request = validate_request(request)
    key = Path(os.getenv("OPENROUTER_KEY_FILE", "/run/secrets/openrouter")).read_text().strip()
    env = os.environ.copy()
    env.update({
        "OPENROUTER_API_KEY": key,
        "PI_CODING_AGENT_DIR": "/tmp/pi-agent",
        "HOME": "/tmp/home",
    })
    Path(env["PI_CODING_AGENT_DIR"]).mkdir(parents=True, exist_ok=True)
    Path(env["HOME"]).mkdir(parents=True, exist_ok=True)
    timeout = int(os.getenv("AGENT_TIMEOUT_SECONDS", "420"))
    command = [
        "pi", "--mode", "json", "--no-session", "--no-extensions", "--no-skills",
        "--no-prompt-templates", "--no-themes", "--no-context-files", "--tools", "read,bash",
        "--provider", "openrouter", "--model", MODEL, "--thinking", "low",
        "--system-prompt", str(SYSTEM_PROMPT), agent_prompt(request, timeout),
    ]
    last_message = None
    for event in pi_events(command, env=env, timeout=timeout):
        if on_event:
            on_event(event)
        if event.get("type") == "message_end" and event.get("message", {}).get("role") == "assistant":
            last_message = event["message"]
    # Pinned Pi can exit 0 after a provider error. Never reuse an earlier successful message.
    if not last_message or last_message.get("stopReason") != "stop":
        raise RuntimeError("The planner stopped before finishing its response.")
    try:
        return validate_result(message_json(last_message))
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("The planner returned an incomplete itinerary.") from exc


def run_job(job_id, request):
    global ACTIVE_JOB
    try:
        result, error = plan(request, lambda event: update_progress(job_id, event)), None
    except TimeoutError:
        result, error = None, "Research reached its time limit. Try a narrower request."
    except Exception as exc:
        print(f"Planner job {job_id} failed: {exc}", file=sys.stderr, flush=True)
        result, error = None, "The planner is unavailable. Try again shortly."
    with JOBS_LOCK:
        JOBS[job_id].update(status="failed" if error else "complete", result=result, error=error, finished=time.monotonic())
        ACTIVE_JOB = None


def launch_job(request):
    global ACTIVE_JOB
    request = validate_request(request)
    # ponytail: one browser job globally; isolated per-job workers if concurrency is needed.
    with JOBS_LOCK:
        if ACTIVE_JOB:
            raise RuntimeError("Wanderbot is researching another trip. Try again shortly.")
        job_id = secrets.token_urlsafe(12)
        ACTIVE_JOB = job_id
        JOBS[job_id] = {
            "status": "researching", "result": None, "error": None,
            "started": time.monotonic(), "last_activity": None, "stage_at": None, "activity": "starting",
            "current": {"title": "Starting planner", "next": None, "state": "working"},
            "history": [],
        }
        finished = [key for key, value in JOBS.items() if value["status"] != "researching" and key != job_id]
        for key in finished[:-20]:
            JOBS.pop(key, None)
    threading.Thread(target=run_job, args=(job_id, request), daemon=True).start()
    return job_id


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            content = (ROOT / "docs/trip-calendar.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if self.path.startswith("/api/plan/"):
            job_id = self.path.removeprefix("/api/plan/")
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                progress = progress_snapshot(job) if job else None
            if not job:
                self.send_json(404, {"error": "Planning job not found."})
            elif job["status"] == "researching":
                self.send_json(202, {"status": "researching", "progress": progress})
            elif job["error"]:
                self.send_json(502, {"error": job["error"], "progress": progress})
            else:
                self.send_json(200, {**job["result"], "progress": progress})
            return
        self.send_error(404)

    def do_POST(self):
        if self.path != "/api/plan":
            self.send_error(404)
            return
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            self.send_json(415, {"error": "Send the request as application/json."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 110000:
                raise ValueError("Request is too large.")
            job_id = launch_job(json.loads(self.rfile.read(size)))
            status, data = 202, {"job_id": job_id, "status": "researching"}
        except (ValueError, json.JSONDecodeError) as exc:
            status, data = 400, {"error": str(exc)}
        except RuntimeError as exc:
            status, data = 429, {"error": str(exc)}
        self.send_json(status, data)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
