# Travel research protocol

Use this protocol to turn browser research into consistent data for an itinerary-planning agent.

## 1. Category plan and stopping targets

Research only categories relevant to the trip. These are useful default stopping targets, not quotas:

| Category | Target | What to verify |
|---|---:|---|
| Intercity transportation | 2–3 viable options | Dated fare, duration, stations/airports, baggage, cancellation terms |
| Lodging | 3 viable options | Total stay price, taxes/fees status, location, cancellation, check-in/out |
| Attractions | 5–8 strong options | Price, hours for planned day, duration, reservation need, official link |
| Food | 1–2 options per day or neighborhood | Menu price, hours, dietary fit, reservation need |
| Local transit | 1 practical plan | Fare/pass price, coverage, operating constraints |
| Weather | 1 official source | Forecast only when within the source's forecast window; otherwise seasonal context |
| Safety | 1–2 official sources | Current advisories, closures, scams or local visitor guidance |

Stop earlier when the user asks for a narrower result. Stop when additional pages repeat the same choices without improving evidence.

## 2. Efficient query patterns

Replace bracketed values with trip facts:

- `[origin] to [destination] [date] official fare`
- `[destination] official tourism top attractions [interest]`
- `[attraction] official tickets price hours [date]`
- `[destination] public transit official fares day pass`
- `[neighborhood] [dietary need] restaurant official menu prices`
- `[destination] hotel [check-in] [check-out] total price official`
- `[destination] government visitor safety advisory`
- `[destination] official weather forecast`

Use an aggregator or review site to discover names only. Search each selected name with `official` plus the exact missing field to reach the source of record.

## 3. Source priority

Prefer sources in this order:

1. Government, transit authority, park service, airport, or official safety/weather source.
2. The attraction, restaurant, hotel, airline, rail, or bus provider's own website.
3. Official destination tourism organization.
4. Established booking platform or aggregator for comparison and availability discovery.
5. Editorial guides, reviews, forums, and social sources for qualitative ideas only.

Record a secondary source only when a primary source is unavailable. Label that limitation. Never treat a search-result snippet as final evidence.

## 4. Dataset fields

Use one row per option or scheduled item:

| Field | Meaning |
|---|---|
| `category` | transportation, lodging, attraction, food, local_transit, weather, safety, culture |
| `name` | Provider, venue, restaurant, or finding name |
| `destination` | City or area |
| `planned_date` | Intended trip date, if applicable |
| `time_or_hours` | Planned time or verified operating hours |
| `location` | Address, station, airport, or neighborhood |
| `duration_minutes` | Visit or journey duration when known |
| `travel_minutes` | Time from the previous cluster or relevant origin |
| `price_amount` | Numeric price for the relevant traveler count |
| `currency` | ISO currency such as USD or EUR |
| `price_status` | exact, from, range, estimate, free, or unavailable |
| `price_includes` | Taxes, fees, ferry, audio tour, baggage, etc. |
| `reservation` | required, recommended, not required, or unknown |
| `why_it_fits` | Short link to budget, interests, geography, or constraints |
| `source_url` | Direct evidence page, not a search-results URL |
| `checked_at` | Retrieval timestamp including time zone |
| `confidence` | high for primary source, medium for strong secondary source, low otherwise |
| `notes` | Closures, accessibility, dietary, seasonal, or uncertainty notes |

If one source provides several prices, preserve the labels that identify the relevant traveler type, ticket, room, date, or fare class.

## 5. Price and budget rules

- Use the total for all travelers when possible. Otherwise record whether the amount is per person, per night, per room, or one way.
- Keep advertised `from` prices distinct from a date-specific checkout price.
- State whether taxes, resort fees, baggage, booking fees, and tips are included.
- Convert currency only when necessary; save the original amount and the conversion date/source.
- Keep a contingency amount rather than filling the entire budget with planned spending.
- Do not claim availability unless the exact dates and traveler count were checked.

## 6. Feasibility checks

Before recommending an option, check:

- It is open on the intended day and time.
- The user can reach it with realistic travel and buffer time.
- Nearby activities are clustered to reduce unnecessary travel.
- Ticket or meal costs fit the remaining category budget.
- Reservation lead time fits the trip date.
- Accessibility, age, dietary, or mobility requirements are satisfied or clearly unresolved.

Weather forecasts should be checked close enough to the trip for the chosen official source to cover the dates. For a distant trip, provide climate/seasonal context and add a future recheck requirement.

## 7. Uncertainty language

Use explicit labels:

- `Verified`: directly supported by the linked primary source.
- `Advertised from`: lowest public starting price, not a dated quote.
- `Estimated`: planning allowance without a verified live price.
- `Unavailable`: the source did not expose the needed fact.
- `Recheck`: likely to change before travel.

Never fill a blank with a plausible value.
