---
name: plan-multi-city-trip
description: Plan or revise multi-destination leisure trips with current research, route-feasibility checks, local-time schedules, complete two-person budgets, savings targets, reservation guidance, and destination-specific safety advice. Use when a traveler starts with either a desired route or a fixed budget and wants an actionable itinerary; do not use it to make bookings or payments without explicit authorization.
---

# Plan a Multi-City Trip

Turn an evolving travel conversation into one internally consistent plan. Preserve confirmed choices, label estimates, and propagate every revision through dates, transport, lodging, activities, safety guidance, and cost.

## Establish the planning state

Track these facts as the user supplies them:

- party size and room-sharing assumptions;
- origin, destinations, order, dates, and desired trip length;
- lodging tier, flight cabin, pace, mobility needs, and transport preferences;
- interests such as beaches, hiking, diving, food, culture, and hidden gems;
- budget, existing savings, and acceptable tradeoffs.

Support both directions discussed by the project team: recommend a trip that fits a budget, or price a trip the traveler already wants. Ask only for missing information that would materially change the route or total. Otherwise, use a reasonable assumption and make it visible.

Treat later user messages as revisions to the same plan. Recalculate all dependent dates, nights, transfer days, reservations, and costs instead of appending contradictory alternatives.

## Research unstable facts

Use current research for fares, schedules, hotel rates, reservation rules, seasonal conditions, transport availability, advisories, and local disruptions. Prefer official operators and government, park, museum, and tourism sources. Use reputable aggregators only when an official source does not expose comparable prices or schedules.

When the repository's `travel-browser-research` skill is available and the trip facts are sufficiently defined, use it to collect the source-backed dataset before synthesizing the itinerary. Keep this skill responsible for conversation state, feasibility decisions, scheduling, critique, and the final traveler-facing plan.

- Date-stamp prices and safety information that may expire.
- Distinguish a live, bookable quote from a planning estimate or forecast.
- Never invent an exact departure time. If schedules for the requested dates are not published, provide a clearly labeled planning window and say when exact times can be selected.
- Verify that requested transport actually exists. If it does not, explain the constraint and compare practical substitutes, including time, luggage, weather, accessibility, and cost implications.
- Do not book, reserve, pay, or contact a third party unless the user explicitly authorizes that action.

## Build the itinerary

Use local dates and times at each destination. State both the inclusive calendar duration and number of paid lodging nights. Account for overnight flights, time-zone changes, airport buffers, hotel check-in, jet lag, rest, meals, and realistic travel between activities.

Balance headline sights with neighborhoods, hidden gems, beaches, hikes, food, unstructured time, and weather alternatives. Put timed tickets and restaurant targets at plausible times, but identify them as targets until booked.

For scuba or other safety-sensitive activities, consult current authoritative guidance and leave an adequate interval before flying. Operator and medical advice takes precedence over a generic itinerary.

## Produce a complete budget

Unless the user says otherwise, calculate for two adults sharing one room. Include:

- every flight leg, baggage, and seat fees;
- lodging taxes, resort fees, and the exact paid-night count;
- meals, drinks, taxes, and customary tips;
- admissions, tours, diving, and equipment;
- rental vehicles, parking, fuel, transit, trains, and taxis;
- travel insurance, connectivity, souvenirs, and spending money;
- a 10–15% contingency appropriate to uncertainty.

Show a defensible range and one rounded savings target. Price materially different choices separately—for example, scheduled inter-island flights versus private helicopter charters—so an expensive preference does not silently distort the baseline.

For a monthly savings request, use the actual months remaining and current savings:

`monthly contribution = (target budget - current trip savings) / remaining contributions`

State the assumed starting balance and contribution count.

## Cover safety and local context

Give concise, actionable guidance for each destination:

- common scams and theft patterns;
- demonstrations, strikes, or other political disruptions relevant to travelers;
- environmental risks such as surf, heat, trails, volcanic conditions, or severe weather;
- cultural etiquette, sensitive sites, and access restrictions;
- emergency numbers, insurance considerations, and when to recheck official advisories.

Avoid stereotypes and partisan commentary. Separate persistent risks from temporary conditions, and attach dates and sources to the latter.

## Critique before delivery

Check the plan for impossible connections, missing nights, double-booked activities, inadequate transfer or recovery time, stale claims presented as facts, and totals that do not reconcile. When the user asks for a critique, identify the consequential weaknesses first and then provide a corrected plan.

For the detailed checklist, output structure, and the Hawaii–Rome–Paris prompting case study, read [references/planning-method.md](references/planning-method.md).
