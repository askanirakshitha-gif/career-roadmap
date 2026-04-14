# Backend setup (FastAPI)

Quick steps to run the backend locally:

1. Create and activate a Python virtual environment (recommended).

2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Provide environment variables:

- Copy `backend/.env.example` to `backend/.env` and set `ANTHROPIC_API_KEY` and `DATABASE_URL` if you have a Postgres database.
- If you do not set `DATABASE_URL`, the app will use a local SQLite file `dev.db` for development.

4. Run the server:

```bash
uvicorn backend.main:app --reload --port 8000
```

5. Open API docs: http://127.0.0.1:8000/docs

Notes:
- For production use, configure a proper Postgres database and set `DATABASE_URL` in `backend/.env`.
- Ensure `ANTHROPIC_API_KEY` is set for real AI responses; without it, the AI endpoint will fail.
