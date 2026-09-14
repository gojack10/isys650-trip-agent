# Trip Planning Agent Design (Draft)

> This is a draft for the ISYS 650 group project. It describes the supplied first-pass idea without selecting a destination or promising live integrations.

## First-pass behavior

The Langflow AI trip-planning agent should:

1. Parse a traveler's vacation request.
2. Ask for missing critical details before planning.
3. Research transport and lodging, attractions and hidden gems, and scams/cultural norms.
4. Build a linked, color-coded day-by-day itinerary.
5. Support one follow-up revision.

The intended experience is a planning aid, not a booking service. Research sources and data boundaries still need to be selected and evaluated by the team.

## Proposed MVP

- Plan one city over three days.
- Use synthetic or otherwise controlled travel data.
- Limit research to two bounded tools.
- Include one critic step to check the draft itinerary.
- Accept one follow-up revision.
- Keep links and color categories in the itinerary output.

## Non-goals for the MVP

- Booking transportation, lodging, or attractions.
- Payments or handling credentials.
- Promising live prices or availability.
- Open-ended live web research.
- Multiple destinations, complex routing, or unlimited revisions.

## Open draft decisions

The team still needs to choose the controlled data, the two tools, the output format, evaluation cases, and the exact rubric mapping. No destination or live integration is assumed here.
