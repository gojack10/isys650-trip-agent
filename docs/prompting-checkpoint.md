# Prompting Checkpoint: Multi-City Trip Planning

**Contributor:** Zack

**Role:** Prompting

**Exercise date:** September 14, 2026

## Goal

The prompting checkpoint tested how a trip-planning agent should respond when a simple destination request grows into a detailed, changing itinerary. The session used a trip for two from San Francisco through Hawaii, Rome, and Paris.

The deliverable is the repository [`plan-multi-city-trip`](../skills/plan-multi-city-trip/SKILL.md) skill. It turns the exercise into reusable behavior rather than preserving one answer as a fixed template.

## What the exercise tested

The conversation introduced constraints in stages:

1. Start with desired destinations.
2. Add a second traveler and price the trip for a shared room.
3. Include every flight leg.
4. Add island hopping and test whether the requested ferry route exists.
5. Substitute realistic aircraft options when it does not.
6. Request exact travel times and distinguish published schedules from estimates.
7. Select medium-tier hotels and account for a future travel year.
8. Add sightseeing, hidden gems, restaurants, beaches, hiking, scuba, scams, political disruptions, and traveler safety.
9. Reconcile the itinerary into an exact day and night count.
10. Convert the complete cost into a monthly savings goal.
11. Compare spring, summer, fall, and winter across the entire route.

## Resulting prompt requirements

The agent should maintain a structured planning state instead of answering each new message independently. When a preference changes, it should revise every affected part of the plan.

It should also:

- accept either a destination-first or budget-first request;
- research unstable facts and attach current sources;
- challenge impossible transport assumptions constructively;
- distinguish bookable facts, planning estimates, and forecasts;
- avoid claiming exact flight times before schedules are published;
- produce a local-time timetable with realistic transfer and recovery time;
- include the full cost of flights, lodging, dining, activities, ground transportation, insurance, spending money, and contingency;
- calculate savings from the remaining contributions and current balance;
- cover environmental, cultural, political, and crime-related safety;
- treat recommendations and reservation targets as non-booking actions;
- critique the result for contradictions before presenting it.

## Example outcome

The refined example became a 22-day, 21-night trip for two:

`SFO → Maui → Honolulu → Kona → Rome → Paris → SFO`

It used 19 paid hotel nights and two nights in transit. A practical two-person planning target was $32,000, with $35,000 recommended for a stronger cushion. Requiring private helicopter transfers increased the illustrative target to approximately $42,000. With eight monthly contributions before May 2027, those targets translated to $4,000, $4,375, and $5,250 per month.

These figures document the checkpoint; the skill requires future runs to obtain current prices and recalculate them.

## Relationship to the MVP

The current MVP remains intentionally narrower: one city, three days, bounded data, one critic pass, and one revision. This checkpoint supplies prompting and evaluation ideas for later versions. It does not add booking, payment, live credentials, or an unsupported hand-written Langflow graph.

Useful MVP-sized tests derived from the session include:

- Does the agent preserve a two-person assumption after a revision?
- Does it reject a nonexistent transport route and offer sourced alternatives?
- Does the calendar reconcile dates and hotel nights?
- Does the critic catch an activity scheduled too close to a flight?
- Does the budget include taxes, fees, local transportation, and contingency?
- Does the answer label stale or unavailable prices as estimates?
