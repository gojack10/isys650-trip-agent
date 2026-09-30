# ISYS 650 Trip Planning Agent

This public portfolio project is the home for a five-person ISYS 650 group project: an AI trip-planning agent that parses vacation requests, asks for missing critical details, researches bounded travel information, and produces a linked, color-coded day-by-day itinerary with continued revisions.

## Assignment and rubric scope

The draft targets the course assignment over the next few weeks by demonstrating a practical agent workflow: request parsing, clarification, bounded research, itinerary synthesis, critique, and follow-up revision. The design is intentionally a first pass and will be refined against the team's rubric and instructor expectations.

## Current status

**Browser-agent candidate, not yet deployed.** The working tree replaces the existing OpenRouter web-search demo with Pi + Browser Harness + headless Chromium. It supports dated itineraries (up to 30 days), budget-first exploration without fabricated dates, and revisions. The UI displays recommended flights/stays, budgets, assumptions, reservations and sources. Research runs asynchronously one job at a time. [Production Wanderplan](https://isys650.10server.net/) remains on the previous deployment until an explicit deployment. Nothing books travel; the blank Langflow export is historical.

## Prompting skill

Zack's first prompting checkpoint is documented in [`docs/prompting-checkpoint.md`](docs/prompting-checkpoint.md). Its reusable behavior is encoded in [`skills/plan-multi-city-trip/`](skills/plan-multi-city-trip/). The skill maintains evolving constraints, checks route feasibility, synthesizes timed itineraries, builds complete budgets and savings goals, and includes reservation and safety guidance.

## Travel research skill

`skills/travel-browser-research/` contains the first data-and-tooling checkpoint: a Browser Harness workflow for researching an already-defined trip. It discovers candidates, verifies prices and restrictions on primary sources, and returns structured, source-backed data for the itinerary agent.

The candidate encodes Jesus's research and Zack's planning requirements into one explicit operating procedure, rather than concatenating competing skills into a user message. Selected SiftText browser nodes are exported ahead of time through the CLI as faithful Markdown snapshots, with a separate pinned-runtime compatibility adapter. The generated system prompt is preloaded; no SiftText access or credentials are needed at runtime. See [`agent/README.md`](agent/README.md) for preparation commands, requirement mapping, branch walkthroughs and verification limits.

Every push to `main` runs [tests and deploys](.github/workflows/deploy.yml) the Docker app on 10server.net; do not push an unreviewed candidate. Pi uses `deepseek/deepseek-v4.1-flash` through OpenRouter. One-job serialization is not a security boundary: the public endpoint, agent-readable provider key and unrestricted shell/browser egress still require deployment hardening. Prompt instructions do not protect secrets or private networks. Use a dedicated spend-capped key for authorized isolated tests.

Run tests locally with `uv run --no-project python -m unittest discover -s tests`. Repository commit conventions are in [`AGENTS.md`](AGENTS.md).
