import json
import os
import streamlit as st
from google import genai

MOCK_WARNING = "⚠️ MOCK_AI_RESPONSE — set GOOGLE_API_KEY in Streamlit secrets for live Gemma."

SYSTEM_PROMPT = """You are PumpSmart, a Filipino fuel savings advisor for Metro Manila drivers.
Given a user's vehicle, budget, and recent trip data, provide exactly 3 actionable recommendations.

Respond ONLY with a valid JSON array of 3 objects, each with:
- "title": short action title (max 8 words)
- "recommendation": specific advice (2-3 sentences, use PHP amounts)
- "estimated_savings_php": integer estimate of monthly savings
- "category": one of ["timing", "routing", "behavior"]

Ground advice in Manila traffic patterns (EDSA rush hours 7-9am, 5-8pm).
Always mention specific PHP savings. Never recommend illegal actions."""


def _mock_recommendations(context: dict) -> list[dict]:
    fuel_type = context.get("fuel_type", "GASOLINE").lower()
    budget = context.get("monthly_budget_php", 3000)
    return [
        {
            "title": "Avoid EDSA during peak hours",
            "recommendation": (
                "Your typical routes show peak-hour departure patterns. "
                "Shifting trips by 30-45 minutes past 9AM or before 6:30AM cuts fuel burn by ~25% "
                f"due to reduced stop-and-go. Estimated saving: ₱{int(budget * 0.12):,}/month."
            ),
            "estimated_savings_php": int(budget * 0.12),
            "category": "timing",
        },
        {
            "title": f"Refuel at Seaoil or Phoenix",
            "recommendation": (
                f"Seaoil and Phoenix consistently price {fuel_type} ₱1.50-₱2.00/L below Shell and Petron. "
                "Switching your refueling station saves roughly ₱30 per full tank. "
                f"At 2 fill-ups/month that's ₱{int(budget * 0.05):,} back in your pocket."
            ),
            "estimated_savings_php": int(budget * 0.05),
            "category": "routing",
        },
        {
            "title": "Combine errands on one trip",
            "recommendation": (
                "Multiple short cold-start trips waste more fuel than one consolidated trip. "
                "Grouping your weekly errands (groceries, pickup, etc.) into a single loop route "
                f"can save 3-5 liters/week — around ₱{int(budget * 0.08):,}/month."
            ),
            "estimated_savings_php": int(budget * 0.08),
            "category": "behavior",
        },
    ]


def get_recommendations(context: dict) -> tuple[list[dict], bool]:
    """Returns (recommendations, is_mock)."""
    api_key = None
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        return _mock_recommendations(context), True

    try:
        client = genai.Client(api_key=api_key)
        user_message = (
            f"Driver context:\n{json.dumps(context, indent=2)}\n\n"
            "Provide 3 fuel-saving recommendations as a JSON array."
        )
        response = client.models.generate_content(
            model="gemma-3-27b-it",
            contents=user_message,
            config={"system_instruction": SYSTEM_PROMPT},
        )
        raw = response.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        recommendations = json.loads(raw.strip())
        return recommendations, False
    except Exception as err:
        st.warning(f"MOCK_AI_FALLBACK — Gemma call failed: {err}")
        return _mock_recommendations(context), True
