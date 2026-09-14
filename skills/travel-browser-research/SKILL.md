---
name: travel-browser-research
description: Research an already-defined trip with Browser Harness and produce source-backed itinerary data covering transportation, lodging, attractions, food, costs, hours, travel time, weather, safety, and relevant constraints. Use when the destination, dates, budget, travelers, and preferences are already known and current web research is needed. Do not use for booking or open-ended destination selection.
---

# Travel Browser Research

Collect current, usable evidence for a trip-planning agent. The result is a clean research dataset, not a reservation and not an unsupported list of recommendations.

## Required context

Before browsing, identify the known trip facts: origin, destination(s), exact dates, traveler count, total budget, interests, transportation/lodging preferences, and relevant dietary, accessibility, or safety needs. Ask only for a missing fact that would materially change the research.

## Browser dependency

Use Browser Harness for the live research. Before controlling the browser, read the installed `browser-harness/SKILL.md` completely and follow its connection, tab, interaction, login, and recording rules.

Use `scripts/make_query_plan.py` when a consistent research checklist or query set would help. Read [references/research-protocol.md](references/research-protocol.md) before the first substantial research pass or whenever source choice, price handling, coverage, or output fields are uncertain.

## Research workflow

1. Turn the trip facts into a small category plan: intercity transportation, lodging, local transit, attractions, food, weather, safety, and any trip-specific constraints.
2. Use focused search queries to discover candidates. Include the exact destination, dates when availability matters, traveler needs, and terms such as `official`, `fare`, `menu`, `tickets`, or `hours`.
3. Treat search snippets, maps, social posts, listicles, and aggregators as discovery only. Open the original provider, venue, government, transit operator, or official tourism site before recording a fact.
4. Extract only the fields needed for the dataset. Prefer page text, links, and complete tables through DOM inspection; use screenshots only when layout or visual evidence matters.
5. Capture the surrounding labels with every price. Record `$47.95 adult day tour`, not an isolated `$47.95`. Mark prices as `exact`, `from`, `range`, or `estimate` and record currency, source URL, and checked time.
6. Compare candidates against the trip rather than popularity alone: budget fit, interests, location, hours on the planned day, travel time, reservation needs, and accessibility or dietary constraints.
7. Stop when the coverage targets in the protocol are met or the remaining sources repeat the same options. Report missing or unverified fields instead of guessing.

## Browser efficiency

- Create one research tab, then reuse it sequentially with `goto_url(...)`; keep extra tabs only when side-by-side comparison is necessary.
- Search a category once, collect a short candidate list, and verify only the strongest candidates.
- Filter DOM output before printing it. Extract relevant headings, links, tables, and lines containing prices or hours rather than dumping an entire page.
- Prefer official pages that answer multiple fields at once, such as a ticket table containing price, age category, inclusions, and reservation rules.
- Recheck live or date-sensitive values near departure. Long-range weather is not a forecast.
- Close research tabs created for the task when they are no longer needed.

## Output

Return:

1. A concise research summary with the best-supported options and major limitations.
2. A structured table or CSV-ready dataset using the protocol's fields.
3. A budget subtotal by category and remaining budget.
4. A source list with retrieval timestamps.
5. An `unverified` section for facts that could not be confirmed.

Do not log in, solve CAPTCHAs, submit forms, book anything, or enter traveler identity or payment information unless the user separately requests and authorizes that action. Never present changing prices, schedules, availability, weather, or travel times as guaranteed.
