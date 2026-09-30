# Browser Runtime Compatibility

Deployment-specific adapter for the source snapshots below. This section is separate from, and does not alter, the faithful SiftText exports. It takes precedence over historical invocation examples and unavailable optional helpers, not over evidence or safety rules.

## Prepared runtime

The container supplies Pi 0.73.1 and Browser Harness 0.1.13 with its own headless Chromium. `BU_CDP_URL` connects to that browser. No human desktop, signed-in profile, SiftText credentials, helper workspace from Jack's machine, or LocateAnything worker is supplied. Never attempt to acquire them. Use only the assigned browser and public web research; no local/private-network browsing other than Browser Harness's provided CDP connection.

All reference snapshots are already loaded below in execution order. Their SiftText UUID links are provenance, not runtime dependencies. Do not recursively retrieve tree nodes. The app's one-agent travel workflow owns execution; snapshots are browser technique references.

## Invocation and helper surface

Send Python through stdin. Historical `browser-harness -c` examples in snapshots are obsolete:

```bash
browser-harness <<'PY'
print(list_tabs())
PY
```

`js()` evaluates JavaScript; the surrounding stdin program is Python. The 0.1.13 smoke observed these callable names: `list_tabs`, `new_tab`, `switch_tab`, `goto_url`, `page_info`, `js`, `cdp`, `click_at_xy`, `fill_input`, `type_text`, `press_key`, `wait`, `wait_for_load`, `capture_screenshot`, `close_tab`. Treat this as a version-scoped observation, not a promise about every installation or signature. If a needed helper is missing or its signature is unclear, inspect it once, not before every action:

```bash
browser-harness <<'PY'
import inspect
print(', '.join(sorted(name for name, value in globals().items() if callable(value) and not name.startswith('_'))))
print(inspect.signature(fill_input))
print(inspect.signature(press_key))
PY
```

The clean container smoke did not expose `extract_text()`; this does NOT establish that upstream removed it. Where snapshots recommend that helper, use `js("document.body.innerText")`, filtering/truncating to relevant evidence before printing. Optional custom workspace helpers and visual location helpers are not assumed available. Prefer accessibility/targeted DOM and CDP interactions; no automatic installation of a visual worker.

## Browser control and verification

List tabs first. Reuse one task-owned research tab, or create one when necessary. There are no user tabs to commandeer in this container; the snapshot's human-active-tab safeguards remain relevant if the environment changes. Do not read a pre-existing page's content as evidence for the current job. Navigate to the requested source afresh. Close task-created tabs on completion; a cached session/page is not current evidence.

For an unfamiliar page: get page information; inspect filtered accessibility roles/names or DOM controls; choose a specific target; interact; verify the changed state. These can be successive statements in ONE Browser Harness stdin script; use a new Bash turn only when the observation changes the next action in a way the script cannot safely determine. Within a script, fail/stop on a missing control or mismatched date instead of continuing blind clicks. For each source, extract short relevant text, the verbatim `location.href`, and `datetime.now(timezone.utc).isoformat()` in the same visit (import `datetime, timezone` from Python's `datetime` module). A request start time, rounded model-generated time, or guessed deep link is not page evidence. When checking several independent official pages in one script, label each source and catch/report errors separately so a failed page cannot inherit another's facts. Use current geometry for coordinate clicks. For duplicate controls, match both identity and visibility. Use screenshots only when visual evidence matters, and only through the assigned browser. Unavailable semantic visual helpers do not block ordinary DOM probing.

Input helpers may not commit framework state. Read the value back and verify the page's response; use native input setters plus a bubbling InputEvent or trusted typing as appropriate. Do not repeatedly click stale coordinates. Wrap multi-line JS in an IIFE; variables otherwise persist across calls.

## Version-scoped site hints (not fixed itineraries)

Observed in the earlier Google Flights smoke: autocomplete candidates used `[role=option]`; date cells used `[role=gridcell][data-iso="YYYY-MM-DD"]` with a `[role=button]` child; result rows often used `li` or accessible flight links. Inspect actual controls and verify origin, destination, dates and traveler count before extracting prices. These are navigation hints, not guaranteed selectors or evidence of a fare. Do not reuse historical result URLs, flights, prices or dates as answers.

Use only the live inspected page to locate controls or read evidence. If a hint fails, return to semantic inspection rather than inventing a click. Google is discovery/comparison; the travel contract defines when primary-source verification or a labeled secondary fallback is required.

## Runtime boundaries

Use Browser Harness for all web interaction in this application, even though the general Runtime Invocation snapshot permits plain HTTP in other projects. Search/filter forms are allowed; submitting personal data, authentication, bookings or payments is not. Unlike the general Login and Consent snapshot, this worker has no authorized SSO identity: report a login wall and use another public source. Stop that source at CAPTCHA, credentials, consent, or other forbidden actions; return the useful evidence and limitations to planning.
