# Context: PumpSmart

> Single source of truth Claude reads at the start of every session.

Last updated: 2026-04-24

## What This Is

PumpSmart is an AI-powered fuel companion web app for Metro Manila drivers (PH market, PHP currency).

- **Problem:** Filipino drivers overspend on fuel due to poor trip timing and uninformed refueling choices.
- **User:** Metro Manila car owners who commute regularly.
- **Success:** User sees ₱ savings from departure time shift or station selection on first use.

## Current State

- **Phase:** MVP / hackathon demo
- **Version:** 0.1.0
- **Deployed?** No — target: Streamlit Community Cloud
- **Users?** None
- **Known broken:** Google Maps mocked (straight-line distance); Gemma mocked if no API key

## Stack

- **App:** Streamlit (Python)
- **AI:** `gemma-3-27b-it` via `google-genai` SDK
- **Maps:** Folium + streamlit-folium (MOCK_ROUTE until Directions API key added)
- **Storage:** SQLite via `sqlite3` (dev); Neon Postgres for prod
- **Deploy:** Streamlit Community Cloud

## Working Model

Hard rules about how work happens here. Do not violate without asking.

- **No local execution.** The user works from iPad/iPhone via Safari + Claude
  Code. There is no terminal, no `make`, no `npm`, no `curl localhost`.
- **No CLI instructions in docs.** If a step needs a command, it has to run
  in CI or in Claude Code's own sandbox — never on the user's machine.
- **Push directly to `main`** by default. Branch only for destructive or
  high-risk changes (schema rewrites, mass renames, deletions).
- **Deploy is automatic** on push to `main` (GitHub Pages or Netlify).
  Verification happens on the deployed preview, not localhost.
- **Multi-chat workflow.** The user maintains separate Claude chats per
  concern (e.g. App Dev, Prompt Refinement). Stay in the lane named in
  the current chat unless told otherwise.

## Key Constraints

Project-specific rules. Edit per project.

- <e.g. "Single HTML file — no build step.">
- <e.g. "No new top-level dependencies without an ADR.">
- <e.g. "Secrets only via Netlify env vars, never committed.">

## Entry Points

Where Claude should start reading when picking up cold. Links, not commands.

- **Main file(s):** <path(s)>
- **Config:** <path>
- **Tests (if any):** <path>
- **Deploy config:** <path, e.g. `netlify.toml` / `.github/workflows/pages.yml`>

## See Also

- `.ai/conventions.md` — coding rules
- `.ai/decisions.md` — ADRs
- `docs/workflow.md` — full working model
- `docs/architecture.md` — structure + data flow
