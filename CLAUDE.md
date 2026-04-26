# PumpSmart — Project Conventions

AI-powered fuel companion app for Metro Manila drivers. Streamlit + Python + Google Gemma 4.

## Stack

- **Framework:** Streamlit 1.56+
- **Language:** Python 3.11+
- **AI:** Google Gemma 4 26B A4B via google-genai
- **Maps:** folium + streamlit-folium (mocked routing for now)
- **DB:** SQLite (local), schema must stay Postgres-compatible for prod
- **Currency:** PHP (₱) — Philippine Peso, never USD or generic

## Folder structure

```
PumpSmart/
├── app.py                # Dashboard (entry point)
├── pages/                # Streamlit auto-routes these
│   ├── 1_Trip_Predictor.py
│   ├── 2_Refuel_Advisor.py
│   └── 3_AI_Advisor.py
├── utils/                # Shared logic
│   ├── ai_client.py      # Gemma wrapper + mock fallback
│   ├── db.py             # SQLite operations
│   ├── fuel_calc.py      # Distance/cost/traffic logic
│   └── maps.py           # Folium map generators
├── data/
│   ├── mock_stations.json
│   └── pumpsmart.db      # gitignored
├── .streamlit/
│   └── secrets.toml      # gitignored — GOOGLE_API_KEY lives here
└── docs/
```

## Streamlit conventions (NON-NEGOTIABLE)

These rules exist because each one represents a bug we already shipped and fixed.

### 1. Session state for all stateful widgets

Never render results inside `if st.button(...):` when the same block contains:
- `st_folium` (map interactions trigger reruns)
- `st.chat_input`
- Any other widget that triggers reruns

Pattern:
```python
# WRONG — results vanish on any rerun
if st.button("Predict"):
    result = compute_something()
    render(result)
    st_folium(my_map)  # this rerun kills the render block above

# CORRECT — button stores, render reads
if st.button("Predict"):
    st.session_state["my_result"] = compute_something()

result = st.session_state.get("my_result")
if result:
    render(result)
    st_folium(my_map)
```

### 2. Persist all user input widgets

Never use `value=datetime.now()` or other unstable defaults. They reset on every rerun.

Pattern:
```python
# WRONG — resets to now() on every rerun
departure_time = st.time_input("When?", value=datetime.now().time())

# CORRECT — persists user choice
if "departure_time" not in st.session_state:
    st.session_state["departure_time"] = datetime.now().time()
departure_time = st.time_input("When?", value=st.session_state["departure_time"])
st.session_state["departure_time"] = departure_time
```

Apply this to: time_input, date_input, slider, selectbox, number_input — anything the user touches.

### 3. DB writes outside reruns

Never call `save_*()` inside a render block — it'll fire on every rerun. Use a `saved` flag in session_state to guarantee single-write per logical action.

```python
prediction = st.session_state.get("trip_prediction")
if prediction and not prediction["saved"]:
    save_prediction(...)
    st.session_state["trip_prediction"]["saved"] = True
```

## API & secrets

- `GOOGLE_API_KEY` lives in `.streamlit/secrets.toml`. Read via `st.secrets.get("GOOGLE_API_KEY")` with `os.environ.get` fallback for non-Streamlit contexts (CLI, tests).
- Never log raw API errors to the user (`st.warning(f"...{err}")` leaks API metadata). Use a generic user message + `print(err)` to terminal logs.
- Always provide a mock fallback. If the API is down or the key is missing, return mock recommendations with a `MOCK_` prefixed warning. The app must never crash on AI failure.

## Currency formatting

- Always `₱` (Unicode U+20B1), never "PHP" or "P"
- Use `f"₱{amount:.2f}"` for prices, `f"₱{amount:,}"` for round monthly totals
- Be explicit in mock data and AI prompts: "Estimated saving: ₱360/month"

## Manila context (for AI prompts)

When writing prompts or mock data:
- Use real PH brands: Petron, Shell, Caltex, Seaoil, Phoenix, Total
- Reference real Manila areas: Makati CBD, BGC, Ortigas, QC, Pasay, Alabang, etc.
- Traffic context: EDSA peak hours 7-9am, 5-8pm; lunch slowdown 11-1; off-peak after 8pm
- Realistic fuel prices for the year; check Phoenix or Petron site for current

## Mock data discipline

- All mock paths labeled with `MOCK_` prefix in code AND a yellow warning banner in the UI
- Mock outputs must be plausible enough to demo, distinct enough from real to recognize at a glance
- Track every mock with a TODO comment naming the real implementation: `# TODO(real-directions-api)`

## Testing & verification

Before commit:
1. Run `/review` (global skill) — fix all criticals, address warnings
2. Smoke test all 4 pages: dashboard, trip predictor, refuel advisor, AI advisor
3. Test rerun resilience on each page: click predict → interact with map/sidebar → results must persist
4. Verify no `MOCK_` paths fire when API key is set
5. Run `git diff --stat` and `git status --short` — confirm only intended files changed

## Commit conventions

Conventional commits format:
- `feat:` new feature
- `fix:` bug fix
- `chore:` config, gitignore, dependency updates
- `refactor:` no behavior change
- `docs:` documentation only
- `test:` test additions

Multi-line bodies for non-trivial commits — explain what AND why per file.

## Things to never do

- `git add .` or `git add -A` without first running `git status --short`
- Push without `git remote -v` paranoia check
- Commit `.streamlit/secrets.toml` (it's in `.gitignore` — keep it that way)
- Commit `venv/` (also gitignored)
- Hardcode API keys, prices, or station data anywhere except `data/` JSON files
- Edit Claude Code's auto-generated session metadata in `.claude/`

## Currently mocked (TODO list)

- `utils/maps.py:route_map` — straight-line approximation, not real road path
- `utils/fuel_calc.py:road_distance_km` — haversine × 1.4 instead of Google Directions
- `utils/fuel_calc.py:traffic_factor` — hardcoded time-of-day buckets, not live traffic
- `data/mock_stations.json` — needs scraper or partner API
