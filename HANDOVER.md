# Handover — 2026-04-26

## Session goal
Fix rerun bugs across all PumpSmart pages, harden AI client error handling, and build a personal Claude Code skill toolkit.

## Status
IN PROGRESS

## Completed — Yesterday (already committed, different chat)
- **MVP scaffolded** — Dashboard (`app.py`), Trip Predictor, Refuel Advisor, AI Advisor all built and routing correctly (`f735055`)

## Completed — Today (this session)
- **Rerun bugs fixed** — session_state pattern applied across all pages, map interactions no longer wipe results (`bffc11c`)
- **AI client hardened** — error handling added, mock fallback wired, generic user-facing error messages (no API leaks) (`bffc11c`)
- **Gitignore cleaned** — `venv/`, `__pycache__/`, `.streamlit/secrets.toml`, `pumpsmart.db` all covered (`bffc11c`)
- **CLAUDE.md rewritten** — replaced generic scaffold with PumpSmart-specific conventions (stack, folder structure, Streamlit rules, currency, Manila context, mock discipline) — **uncommitted**

## Tooling improvements (cross-project)
These don't appear in PumpSmart's git history — they live in user-level config at `~/.claude/` — but they're the highest-leverage work from this session.

| Skill | Path | Purpose |
|-------|------|---------|
| `/review` | `~/.claude/skills/review/SKILL.md` | Pre-commit code audit — bugs, security, anti-patterns |
| `/commit` | `~/.claude/skills/commit/SKILL.md` | Conventional commit message generation from staged diff |
| `/deploy-check` | `~/.claude/skills/deploy-check/SKILL.md` | Pre-deploy checklist (secrets, mocks, version mismatches) |
| `/handover` | `~/.claude/skills/handover/SKILL.md` | Session handover doc generator (this skill) |

- **Global `~/.claude/CLAUDE.md` updated** — personal workflow rules: communication style, step-by-step protocol, disaster prevention, code review discipline, file/repo conventions

## In flight (uncommitted)
| File | Change | Why |
|------|--------|-----|
| `CLAUDE.md` | Full rewrite from generic template to PumpSmart project conventions | Establishes non-negotiable rules for session-state, DB writes, currency, AI prompts |
| `CLAUDE.md.backup` | Auto-generated backup of old CLAUDE.md | Safe to delete — old content is gone and not needed |

## Next steps (priority order)
1. **Commit CLAUDE.md + delete backup** — `CLAUDE.md.backup` should be deleted or added to `.gitignore`; commit CLAUDE.md with `chore:` prefix
2. **Update CHANGELOG.md** — still a placeholder template (`{{PROJECT_NAME}}`, no real entries); add v0.1.0 entry for MVP and v0.1.1 for rerun fixes
3. **Replace haversine routing** — `utils/fuel_calc.py:road_distance_km` uses haversine × 1.4; wire to Google Directions API or OSM alternative (`TODO(real-directions-api)`)
4. **Replace hardcoded traffic factors** — `utils/fuel_calc.py:traffic_factor` uses time-of-day buckets; replace with live MMDA or Google traffic data
5. **Replace mock station data** — `data/mock_stations.json` needs a scraper or partner API (Petron/Shell/Caltex station locator)
6. **Smoke test all 4 pages end-to-end** — rerun resilience, no MOCK_ paths firing when API key is set

## Open questions
- Is the SQLite schema Postgres-compatible enough to migrate cleanly, or does it need a review before any prod migration?
- What's the target deploy environment — Streamlit Cloud, or self-hosted?

## Blockers
- Real routing/traffic: blocked on Google Directions API key (separate from Gemma key) or OSM Overpass access
- Real station data: no scraper or partner API yet — manual JSON updates are not scalable

## Context for next session
The MVP is built and running. All major rerun bugs (session_state, map interactions, DB double-writes) are fixed and committed. CLAUDE.md has been rewritten with project conventions but not yet committed — do that first. The highest-leverage next move on the product side is replacing the three mocked utils (routing, traffic, station data), starting with `utils/fuel_calc.py` since it affects both Trip Predictor and Refuel Advisor accuracy.

## Run state
- App running locally? Unknown — run `streamlit run app.py` on port 8501
- Last test run? No automated tests — manual smoke test only
- Last deploy? Not deployed — local only as of 2026-04-26

## Files to look at first
- `utils/fuel_calc.py` — `road_distance_km` and `traffic_factor` are the two highest-impact mocks to replace
- `utils/maps.py` — `route_map` renders straight-line path; needs real road geometry
- `data/mock_stations.json` — all station data is static mock; source of truth for Refuel Advisor
