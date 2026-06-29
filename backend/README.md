# Qabul Backend

FastAPI backend for the Qabul SaaS MVP: auth, businesses, services, staff, working hours, bookings, dashboard stats, AI chat and Telegram bot integration.

## Local setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

API docs:

```text
http://localhost:8000/docs
```

## Test

```bash
cd backend
pytest
```

The test suite uses SQLite in memory and checks the main MVP flow: auth, business setup, service/staff setup, working hours, bookings, dashboard summary and mock AI confirmation.

## Seed demo data

```bash
python -m scripts.seed_demo
```

Default demo owner:

```text
email: owner@example.com
password: password123
```

## Telegram bot

Set `TELEGRAM_BOT_TOKEN` and `DEFAULT_BUSINESS_ID` in `.env`, then run:

```bash
python -m app.bot.main
```
