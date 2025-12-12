# Sewer Flow Modelling

FastAPI + SQLAlchemy backend with optional Streamlit UI for sewer flow modelling workflows (ingestion → QC → cleaning → hydraulics → rainfall/I/I → exports → reporting → auth).

## Quickstart (local)
- Create a virtualenv: `python -m venv .venv && source .venv/bin/activate`
- Install deps: `pip install -r requirements-dev.txt`
- Run API: `uvicorn app.main:app --reload`
- Run tests: `pytest`
- Run Streamlit UI: `streamlit run ui/main.py`

## Docker
- `docker-compose up --build`
- API on http://localhost:8000, Postgres on 5432.

## Configuration
- Copy `.env.example` to `.env` and adjust `APP_DATABASE_URL` (use Postgres for non-dev).
- Settings live in `app/config.py` via pydantic-settings; env prefix `APP_`.

## Database & Migrations
- Models: see `db/models/core.py` (Project, Site, TimeSeriesRaw, TimeSeriesProcessed, RatingCurve).
- Alembic scaffold: `alembic.ini`, scripts under `db/migrations`. Example command: `alembic revision --autogenerate -m "init" && alembic upgrade head`.
- For a quick start with SQLite: `python scripts/seed_demo.py` creates tables.

## Project layout
- `app/` FastAPI app, routers, services (ingestion stub in `app/services/ingestion.py`).
- `db/` SQLAlchemy base/models and Alembic setup.
- `ui/` Streamlit placeholder UI following workflow phases.
- `scripts/` utilities (seed demo DB).
- `tests/` pytest-based tests (health check sample).

## Next steps
- Flesh out ingestion/upload endpoints and QC pipelines.
- Add domain routes (projects/sites/timeseries) and auth once requirements stabilize.