"""
Smart Request Classifier API
-----------------------------
A lightweight cloud-deployable REST API that classifies incoming text
requests (e.g. support tickets, customer messages, operational requests)
by CATEGORY and PRIORITY.

Two modes:
1. Rule-based (default, no API key needed) — works out of the box.
2. AI-powered (optional) — if a GEMINI_API_KEY environment variable is set,
   the app uses Google's Gemini API for smarter classification, reusing the
   same AI-agent idea from the n8n automation pipeline project.

Built with FastAPI so it can be deployed for free on Render, Railway,
Google Cloud Run, or any platform that runs a Python web service.
"""

import os
import re
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Smart Request Classifier API",
    description="Classifies incoming text requests by category and priority. "
                 "Cloud-deployable companion service to the n8n AI automation pipeline.",
    version="1.0.0",
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    category: str
    priority: str
    method: str
    text: str


# ---------------------------------------------------------------------------
# Rule-based fallback classifier (no external API needed)
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Technical": ["error", "bug", "crash", "not working", "issue", "fail", "network", "server", "connection"],
    "Billing": ["invoice", "payment", "charge", "refund", "price", "subscription", "bill"],
    "Account": ["password", "login", "account", "access", "sign in", "sign up", "reset"],
    "General Inquiry": ["information", "question", "how do", "when", "where", "hello", "hi"],
}

URGENT_KEYWORDS = ["urgent", "asap", "immediately", "critical", "down", "not working", "emergency"]


def rule_based_classify(text: str) -> ClassifyResponse:
    lowered = text.lower()

    category = "General Inquiry"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            category = cat
            break

    priority = "High" if any(kw in lowered for kw in URGENT_KEYWORDS) else "Medium"
    if len(lowered.strip()) < 15:
        priority = "Low"

    return ClassifyResponse(category=category, priority=priority, method="rule-based", text=text)


# ---------------------------------------------------------------------------
# Optional AI-powered classifier (Gemini API)
# ---------------------------------------------------------------------------

def gemini_classify(text: str) -> Optional[ClassifyResponse]:
    if not GEMINI_API_KEY:
        return None

    try:
        import requests

        prompt = (
            "Classify the following request into one category "
            "(Technical, Billing, Account, or General Inquiry) and one priority "
            "(High, Medium, or Low). Respond ONLY in the exact format "
            "'category: <category> | priority: <priority>'.\n\n"
            f"Request: {text}"
        )

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()

        output = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        match = re.search(r"category:\s*(\w[\w\s]*)\s*\|\s*priority:\s*(\w+)", output, re.IGNORECASE)
        if not match:
            return None

        category, priority = match.group(1).strip(), match.group(2).strip()
        return ClassifyResponse(category=category, priority=priority, method="gemini-ai", text=text)

    except Exception:
        # Any network/API issue silently falls back to the rule-based classifier
        return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "Smart Request Classifier API",
        "status": "running",
        "ai_mode_enabled": bool(GEMINI_API_KEY),
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/classify", response_model=ClassifyResponse)
def classify(request: ClassifyRequest):
    if GEMINI_API_KEY:
        result = gemini_classify(request.text)
        if result:
            return result
    return rule_based_classify(request.text)
