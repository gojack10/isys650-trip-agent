# Prepared agent instructions

This package is a candidate, not a production-deployment claim.

## Ownership and assembly

- `system.md`: one authored travel procedure encoding Jesus's research specification and Zack's planning specification. The original skills remain the requirement sources, not competing runtime workflows.
- `browser-runtime.md`: compatibility adapter for the pinned container and observed helper surface. Deployment-specific overrides live here, not in copied source nodes.
- `browser-nodes.md`: faithful SiftText snapshots (scope, warnings, ruled-out approaches and crystallization), with UUID and update time for each node.
- `prompt.md`: generated concatenation in that order, passed as Pi's **system** prompt. The user message is only a JSON task/state envelope. No live SiftText access or skill-discovery decision is required.

Rebuild offline after an instruction edit:

```sh
uv run --no-project python scripts/prepare_agent.py
uv run --no-project python scripts/prepare_agent.py --check
```

Refresh the allowlisted browser nodes intentionally from the authenticated local SiftText CLI:

```sh
uv run --no-project python scripts/prepare_agent.py --refresh-browser
```

Review the snapshot diff and compatibility rules before shipping a refresh. The exporter fails on missing/extra IDs and never writes SiftText. UUIDs and timestamps identify sources; the build prints a SHA-256 for the exact assembled prompt. The credentials and CLI are not shipped in the image. The offline freshness test catches source-part changes without regenerating the assembled prompt.

Do not preload unrelated domain hubs, case studies, historical fares, search-result URLs, or private browser state. Historical examples in the faithful snapshots remain explicitly reference-only. Known obsolete invocation forms and unavailable optional helpers are resolved in `browser-runtime.md`; snapshots are not silently rewritten.

## Requirement coverage

| Requirement owner | Prompt location / receiving output |
|---|---|
| Jesus: known facts, category plan and efficient browsing | Steps 1–2; planning_state and research stop conditions |
| Jesus: source priority, field labels, quote scope and retrieval time | Step 2; sources, prices, notes and limitations |
| Jesus: uncertainty, access failures and relevant coverage | Step 2 branches; partial result instead of fabricated completion |
| Zack: budget-first or destination-first, evolving constraints | Step 1; exploring/clarification/defined-trip/revision branches |
| Zack: route feasibility, local times, transfers and night counts | Step 3; days, flights, lodging and critique |
| Zack: full-party cost, contingency, alternatives and savings | Step 3; budget items, totals, variants and savings |
| Zack: reservation guidance, safety and culture | Steps 2–3; reservations, local_note and sources |
| Zack: critique and propagation of changes | Step 4; corrected complete/partial plan |
| Canopy: roles, reading order, branches, handoff and boundaries | One agent, explicit preloaded order, steps 1–4 and output contract |

`selected` means recommended by the agent, not booked or human-confirmed. A human can change that recommendation through chat. A dedicated option-picker UI remains separate work.

## Canopy walkthrough (instruction review, not live evidence)

1. **Defined flight trip:** recover party/dates/preferences → research dated options and direct evidence → reconcile flight legs, hotel nights and all-party costs → critique → render the plan. Unavailable inventory makes a partial draft, not invented precise fares.
2. **Budget first, no destination/date:** do not invoke the old blanket date gate. Explore relevant destinations/seasons; no fabricated calendar. Expose the choice and resume intent recovery when the human answers.
3. **Human override, no flights:** retain confirmed dates/party, replace affected flight/transfer costs and schedule with driving evidence, and recalculate savings. A previous recommendation cannot override the user.
4. **Different capability / unfamiliar site:** the agent need not infer a handoff or know an omitted tool. Runtime notes give the actual invocation, observation→interaction→verification loop and fallback. Failure ends in disclosed missing evidence. This reasoning walkthrough does not prove performance on a second model.

## Verification and remaining limits

Offline tests cover prompt assembly/provenance, branch-compatible outputs, numeric reconciliation, source validation, paid-night references, revisions as data, and existing async behavior. They do not prove researched facts are correct.

`tests/agent_trial.py` is an opt-in, paid, fresh-agent check using the actual app prompt/validation path with Pi JSON event capture. Run only in a disposable configured browser container with the authorized test key. It exercises clarification, budget-first exploration, a dated trip, and a no-flights revision; retains request, tool trace and result artifacts, including partial traces on timeout. Optional scenario-name arguments restrict reruns. The app supplies the real wall-clock deadline and a synthesis reserve; this is an explicit instruction, not proof that a model will obey it.

`TRIP_TEST_URL=http://127.0.0.1:18081/ browser-harness < tests/ui_trial.py` (from the repository root) tests dated plans, budget/source modals and empty-calendar exploration with synthetic data against a running candidate. It never submits a research job. Trace inspection and this UI check are separate from factual verification. Never treat a successful result shape or model assertion as evidence that a travel fact is true.

This is not a hardened public-agent deployment. In particular, read/bash plus a shared browser profile and an agent-readable provider key are not a security sandbox. Prompt instructions do not enforce private-network egress or secret isolation. Keep production unchanged until a separate deployment/security review; retained traces must be handled as potentially sensitive.
