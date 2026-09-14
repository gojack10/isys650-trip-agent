# ISYS 650 Trip Planning Agent

This public portfolio project is the home for a five-person ISYS 650 group project: a Langflow AI trip-planning agent that parses vacation requests, asks for missing critical details, researches bounded travel information, and produces a linked, color-coded day-by-day itinerary with one supported revision.

## Assignment and rubric scope

The draft targets the course assignment over the next few weeks by demonstrating a practical agent workflow: request parsing, clarification, bounded research, itinerary synthesis, critique, and follow-up revision. The design is intentionally a first pass and will be refined against the team's rubric and instructor expectations.

## Current status

**Draft setup only.** A separate Langflow project (`trip-planning-agent`) and flow (`Trip Planning Agent — Draft`) were created. The flow is intentionally blank; implementation and validation are deferred.

`flows/trip-agent.json` is the JSON export of that new Langflow flow. It is kept in Git so the team can review project history and import/export the flow through Langflow; the Langflow server is the runtime, not a substitute for this repository.

Team roles, `AGENTS.md`, and CI are intentionally not set up yet. They will be ideated separately.

## Travel research skill

`skills/travel-browser-research/` contains the first data-and-tooling checkpoint: a Browser Harness workflow for researching an already-defined trip. It discovers candidates, verifies prices and restrictions on primary sources, and returns structured, source-backed data for the itinerary agent.

The skill is a research workflow and is not yet wired into the blank Langflow export. It does not book travel, enter credentials, or guarantee changing prices and availability.
