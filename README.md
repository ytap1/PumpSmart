# PumpSmart

> AI-powered fuel companion for Metro Manila drivers. Reduce fuel spend through predictive trip cost analysis and smart refueling decisions.

## Status

- **Phase:** MVP / hackathon demo
- **Version:** 0.1.0
- **Deployed?** No — deploy to Streamlit Community Cloud
- **AI:** Gemma-3-27b-it via Google AI Studio (mock fallback if no key)

## Features

| Page | What it does |
|---|---|
| Dashboard | Budget gauge, recent trip history, fuel price snapshot |
| Trip Predictor | Compare fuel cost across 3 departure windows (now / +30 / +60 min) |
| Refuel Advisor | Rank nearby stations by price + detour cost, folium map |
| AI Advisor | Gemma-powered personalized recommendations |

## Stack

- **Frontend/Backend:** Streamlit
- **AI:** `gemma-3-27b-it` via `google-genai`
- **Maps:** Folium + streamlit-folium (MOCK routes — real Directions API pending)
- **Data:** SQLite (dev) · Neon Postgres (prod via `DATABASE_URL`)
- **Deploy:** Streamlit Community Cloud

## Deploy

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select `app.py`
3. Add secret: `GOOGLE_API_KEY = "your-key"` in the Streamlit secrets UI
4. Deploy — live in ~2 minutes

## Local Run (Claude Code sandbox only)

```
streamlit run app.py
```

## Mock Data

All Google Maps calls are mocked with straight-line distance × 1.4 road factor.
Fuel stations are 10 real Manila-area locations with realistic PHP prices.
Set `GOOGLE_API_KEY` to activate live Gemma responses.
