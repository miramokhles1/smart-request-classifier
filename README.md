# Smart Request Classifier API ☁️

A lightweight, cloud-deployed REST API that automatically classifies incoming
text requests (support tickets, customer messages, operational requests) by
**category** and **priority**.

Built as a cloud-engineering companion to my
[AI Customer Support Automation Pipeline](https://github.com/miramokhles1/ai-customer-support-pipeline)
(n8n + Google Gemini API) — this project takes the same classification idea
and exposes it as a standalone, cloud-hosted web service.

## Live Demo
Deployed on Render (free tier): `https://<your-app-name>.onrender.com`
Interactive API docs: `https://<your-app-name>.onrender.com/docs`

## Features
- `POST /classify` — takes a text request and returns a category (Technical,
  Billing, Account, General Inquiry) and priority (High, Medium, Low).
- `GET /health` — health check endpoint used by the cloud platform to confirm
  the service is running.
- Works out of the box with a **rule-based classifier** — no API key needed.
- Optional **AI mode**: set a `GEMINI_API_KEY` environment variable and the
  service automatically switches to using Google's Gemini API for smarter
  classification, with automatic fallback to the rule-based logic if the
  request fails.

## Tech Stack
- **Python 3.11**, **FastAPI**, **Uvicorn**
- Deployed on **Render** (or any platform that runs a Python web service —
  Railway, Google Cloud Run, AWS Elastic Beanstalk, etc.)
- Optional integration with **Google Gemini API**

## Run Locally
```bash
git clone https://github.com/<your-username>/smart-request-classifier.git
cd smart-request-classifier
pip install -r requirements.txt
uvicorn main:app --reload
```
Then open `http://127.0.0.1:8000/docs` to try it interactively.

## Example Request
```bash
curl -X POST https://<your-app-name>.onrender.com/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "My internet connection keeps failing, this is urgent!"}'
```
Response:
```json
{
  "category": "Technical",
  "priority": "High",
  "method": "rule-based",
  "text": "My internet connection keeps failing, this is urgent!"
}
```

## Deploy It Yourself (Free, ~5 minutes)

### Option A — Render (recommended, easiest)
1. Push this project to a new GitHub repo.
2. Go to [render.com](https://render.com) → New → Web Service → connect your
   GitHub repo.
3. Render auto-detects the `Procfile`. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. (Optional) Add an environment variable `GEMINI_API_KEY` to enable AI mode.
5. Click **Deploy** — Render gives you a free public URL.

### Option B — Railway
1. Push to GitHub, then go to [railway.app](https://railway.app) → New
   Project → Deploy from GitHub repo.
2. Railway auto-detects the `Procfile` and deploys automatically.

## What This Project Demonstrates
- Designing and deploying a REST API on a cloud platform (PaaS)
- Environment-variable-based configuration for optional AI integration
- Graceful fallback logic between an AI service and a rule-based system
- API documentation via FastAPI's built-in OpenAPI/Swagger UI

## Author
**Mira Mokhles Samy** — Electronics & Communications Engineering student
[LinkedIn](https://linkedin.com/in/mira-mokhles-a9a841357) ·
[GitHub](https://github.com/miramokhles1)
