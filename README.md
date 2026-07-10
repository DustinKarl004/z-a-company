# Z.A. Company

Inventory, sales, and profit tracking system for Z.A. Company's branches — replacing the current manual Messenger-based stock reporting with a proper web app.







## Tech Stack

| Layer | Choice |
|---|---|
| Frontend | Vue 3 + Vite, Pinia, Vue Router — hosted on **Vercel** |
| Backend | Python, FastAPI + Uvicorn, SQLAlchemy + Alembic — hosted on **Railway** |
| Database | PostgreSQL |
| Auth | JWT (PyJWT), bcrypt, TOTP (pyotp) |

**Why Vercel + Railway instead of AWS:** avoids the cost of managing a custom domain/infrastructure setup on AWS — Vercel/Railway are cheaper and simpler to run for a project this size.


