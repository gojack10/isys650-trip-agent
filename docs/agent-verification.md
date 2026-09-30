# Prepared-prompt verification — 2026-09-30 UTC

Candidate only; production was not deployed or restarted. Runtime: Pi 0.73.1, Browser Harness 0.1.13, DeepSeek V4.1 Flash through OpenRouter, headless Chromium in a disposable 10server container.

Final assembled prompt SHA-256: `eb8d7da2757b57fa327f281cf3c9b439a368717bbc5d51f1b18b9cd143d4d147` (35,706 bytes). Nine SiftText node snapshots were fetched with the CLI, preserving node UUID/update time and original content. Compatibility rules remain separate. Instructions are preloaded in the system prompt; requests and previous model output are JSON data.

## Checks and observations

- **14 offline tests passed**, including assembled-prompt freshness, export ID coverage, state separation, exploration without dates, budget/savings arithmetic, nullable unavailable costs, source validation, paid-night references and existing async-job behavior. JavaScript compilation, shell syntax and diff whitespace checks passed.
- **Clarification:** final prompt returned a question with zero browser calls.
- **Budget-first:** the first prompt candidate researched two destinations, returned `exploring`, and did not invent a dated calendar. It took 24 browser calls. This branch was not rerun on the final prompt revision.
- **Dated trip:** the evidence-label candidate researched SFO–LA, Oct 15–17, two adults and a USD 2500 ceiling. It returned three calendar days, a hotel range, an estimated full-party budget with savings, source links and explicit gaps. It correctly returned `partial`, not complete; 43 browser calls. The recorded result also passed the final validator.
- **Human override:** the next fresh invocation received that prior plan and a no-flights/driving/free-activities revision. It removed flights, retained dates/party/hotel, recalculated the budget and savings, and kept uncertainty visible (`partial`); eight browser calls. Its recorded output passed the final validator.
- **Unknown-unit regression:** final prompt, no browsing allowed, inherited a USD 158 hotel figure with no verified unit/date/source. It returned `partial`, retained `unavailable`, did not turn the figure into an exact nightly rate, and withheld complete budget totals. Zero browser calls.
- **UI:** Browser Harness exercised the actual candidate page using a synthetic dated fixture, Budget and Plan details/source modals, and undated exploration with an empty calendar. A retained real dated-trip result was also rendered: three days, Freehand Los Angeles and the actual budget/limitations appeared. This is rendering verification, not a fresh UI-to-agent end-to-end request.

## Failed attempts that informed the repair

1. The first dated-trip trial timed out at 420 seconds. The model had no visible execution deadline. The request envelope now supplies research/response deadlines with a synthesis reserve. This remains an instruction plus a hard process timeout, not a guarantee of consistent latency.
2. A subsequent trial passed structural checks but mislabeled an assumed hotel unit as exact and called missing dated research complete. The prompt now explicitly propagates evidence uncertainty through recommendations, costs, status and revisions. The later trial used range/estimate labels and `partial`.
3. The unknown-cost regression produced appropriate null quantity/contingency values, which the app rejected. The validator now permits these only for unavailable/incomplete costs; known-price arithmetic remains checked. Final fresh-agent regression passed.

## Evidence and limits

Local evidence is retained under the git-ignored `tmp/agent-trials/2026-09-30/`, with v1–v4 request/results and compressed Pi JSONL tool traces. v1's timed-out dated run has no partial trace because the initial recorder buffered output; later recording streams to disk. Do not commit traces blindly: they may contain sensitive page content.

These trials prove bounded behavior, not universal reliability or that every fare, fee or safety claim is accurate. No second model was evaluated. The final small null-cost contract change was checked against the final fresh clarification/uncertainty trials and replayed dated/revision outputs, not a new full dated-trip run. Public deployment still requires the separate key/egress/browser-isolation security review described in `agent/README.md`.
