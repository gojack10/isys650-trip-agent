# Multi-City Planning Method

Use this reference when producing a full itinerary, reviewing a plan, or explaining the Hawaii–Rome–Paris prompting exercise.

## Planning checklist

Before presenting a final plan, verify:

1. Every calendar date is assigned exactly once.
2. The inclusive day count and lodging-night count are both correct.
3. Every route segment has a feasible transport mode.
4. Overnight travel and time-zone changes are reflected in arrival dates.
5. Airport, station, check-in, meal, and rest buffers are realistic.
6. Safety-sensitive activities are separated from flights appropriately.
7. Attractions and restaurants that require reservations are labeled as targets until booked.
8. Dynamic claims have current sources and dates.
9. The budget covers all travelers and reconciles to the displayed total.
10. Revisions have propagated through the entire plan.

## Useful output shape

Lead with the recommendation and the assumptions that most affect it. For a substantial trip, use:

1. route, calendar duration, and paid-night count;
2. local-time day-by-day timetable;
3. lodging and transport recommendations with planning prices;
4. reservation checklist and release windows;
5. cost table with lean, recommended, and premium variants;
6. monthly savings calculation;
7. destination-specific safety and cultural notes;
8. links to current authoritative sources.

A timetable row should normally identify the local date, destination, morning, afternoon, evening, lodging, reservations, and important constraints. Keep transit days lighter than destination days.

## Pricing method

Build the total from quantities instead of guessing one package price:

- `lodging = paid nights × all-in nightly rate`
- `food = travel days × daily amount for the full party`
- `transport = each ticket or rental + baggage + parking + fuel + transfers`
- `activities = price per participant × participants, plus equipment or fees`
- `trip target = category subtotal + contingency`

Avoid false precision. Round the final savings target upward after showing the underlying estimate. If departure is too far away for bookable inventory, base the plan on recent comparable prices plus a documented escalation assumption.

## Prompting case study: Hawaii, Rome, and Paris

This case study records the decisions made during Zack's prompting checkpoint on September 14, 2026. Its prices are historical planning estimates, not reusable quotes.

### Request evolution

The traveler began with Hawaii, Rome, and Paris, then progressively added:

- two travelers;
- all flight legs from and back to San Francisco;
- several nights each on Maui, Oʻahu, and Hawaiʻi Island;
- a preference for boat travel between the Hawaiian islands;
- small-aircraft or helicopter alternatives when ferries were unavailable;
- exact travel times, medium-tier hotels, and a trip roughly one year away;
- sightseeing, hidden gems, restaurants, scams, local politics, and general safety;
- beaches, hiking, scuba, local transport, spending money, and souvenirs;
- seasonal comparison and a monthly savings target.

This sequence demonstrated why the agent must maintain a single planning state. Each new constraint changes several earlier answers.

### Consolidated example plan

- Party: two adults sharing one room.
- Route: SFO → Maui → Honolulu → Kona → Rome → Paris → SFO.
- Duration: 22 calendar days and 21 nights, including two nights in transit.
- Paid lodging: 19 nights—four Maui, three Honolulu, four Kona, four Rome, and four Paris.
- Lodging: medium-tier hotels and resorts.
- Activities: scuba on Maui and Kona, beaches, Road to Hāna, Haleakalā, Diamond Head, Pearl Harbor, manta-ray snorkeling, Hawaiʻi Volcanoes National Park, ancient Rome, the Vatican, the Louvre, the Eiffel Tower, and neighborhood hidden gems.

The requested Maui–Honolulu–Kona ferry chain was not feasible because no public passenger ferry serves those routes. The plan therefore separated scheduled inter-island aircraft from private helicopter charters. It also replaced a second late-night scuba dive with manta snorkeling to preserve a wider pre-flight safety interval.

Exact 2027 flight times were not yet available. The responsible output used route-duration estimates and planning windows rather than fabricated clock times.

### Example budget result

As estimated on September 14, 2026:

| Variant | Two-person target |
| --- | ---: |
| Practical plan with scheduled inter-island flights | $32,000 |
| Recommended cushion with scheduled flights | $35,000 |
| Plan with private helicopter transfers | $42,000 |

The recommended estimate included flights, 19 hotel nights, meals and tips, activities, local transportation, insurance, $2,000 of souvenir money, and contingency. With eight monthly contributions before a May 2027 departure, the illustrative savings figures were $4,000, $4,375, or $5,250 per month respectively.

Always rebuild these figures from current prices, actual dates, current savings, party size, and the traveler's selected transport variant.

### Lessons for the agent

- Resolve feasibility before polishing a timetable.
- Treat “exact” as a request for sourced precision, not permission to invent unavailable schedules.
- Count calendar days, nights in transit, and paid hotel nights separately.
- Separate a practical baseline from premium preferences.
- Include environmental and activity-specific safety, not only crime.
- Revisit seasonality across the whole route: late spring was the best overall compromise, while mid-September to early October remained a strong alternative with higher Central Pacific storm exposure.

## Selected authoritative sources from the exercise

- [Hawaii Public Utilities Commission water carriers](https://puc.hawaii.gov/water-carriers/)
- [National Weather Service Honolulu marine information](https://www.weather.gov/hfo/marine)
- [Go Hawaii weather and surf guidance](https://www.gohawaii.com/trip-planning/weather)
- [Go Hawaii ocean safety](https://www.gohawaii.com/trip-planning/travel-smart/ocean-safety-in-hawaii)
- [Divers Alert Network flying-after-diving guidance](https://world.dan.org/health-medicine/health-resources/diseases-conditions/flying-after-diving/)
- [Hawaiʻi Volcanoes National Park conditions](https://www.nps.gov/havo/planyourvisit/conditions.htm)
- [Official Colosseum tickets](https://colosseo.it/en/opening-times-and-tickets/)
- [Vatican Museums visitor information](https://www.museivaticani.va/content/museivaticani/en/organizza-visita.html)
- [Official Louvre website](https://www.louvre.fr/en)
- [Official Eiffel Tower ticket office](https://ticket.toureiffel.paris/en)
- [U.S. State Department Italy advisory](https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/italy-travel-advisory.html)
- [U.S. State Department France advisory](https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/france-travel-advisory.html)
