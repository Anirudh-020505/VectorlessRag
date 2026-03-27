# Vercel Deployment Guide

## Deploy Backend (`backend/`)

1. Create new Vercel project.
2. Set root directory to `backend`.
3. Configure environment variables:
   - `DATABASE_URL`
   - `GEMINI_API_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `SECRET_KEY`
   - `CLIENT_URL` (frontend production URL)
   - `ENVIRONMENT=production`
4. Deploy. Vercel uses `backend/vercel.json` and serves FastAPI via `backend/api/index.py`.
5. Copy backend production URL (example: `https://pageindex-backend.vercel.app`).

## Deploy Frontend (`frontend/`)

1. Create second Vercel project.
2. Set root directory to `frontend`.
3. Add env variable:
   - `VITE_API_BASE_URL=<your-backend-url>`
4. Deploy. Vite build output is served as SPA with `frontend/vercel.json` rewrite.

## Local Run

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
