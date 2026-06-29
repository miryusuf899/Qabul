# Qabul

Qabul is a SaaS MVP for online booking, AI-assisted administration and small-business customer management.

This repository is a monorepo. The backend is implemented in `backend/` with FastAPI, SQLAlchemy Async, Alembic, JWT auth, booking rules, dashboard analytics, mock AI chat and Telegram bot integration.

Backend quick start:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m scripts.seed_demo
uvicorn app.main:app --reload
```

Tests:

```bash
cd backend
pytest
```
