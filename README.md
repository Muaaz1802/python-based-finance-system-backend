# Finance Tracker API

A Python-based finance tracking backend built with FastAPI, PostgreSQL, and SQLAlchemy.

## Stack

- **FastAPI** — API framework
- **PostgreSQL** — Primary database
- **SQLAlchemy 2.0** — ORM
- **Alembic** — Database migrations
- **JWT (python-jose)** — Authentication
- **passlib[bcrypt]** — Password hashing
- **pytest** — Testing (SQLite in-memory)

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd finance-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Generate a secure `SECRET_KEY` for JWT signing:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Edit `.env` with your PostgreSQL credentials:

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/finance_db
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Seed the database

```bash
python seed.py
```

This creates three users and 120 randomised transactions across 2024.

| Role    | Email               | Password   |
| ------- | ------------------- | ---------- |
| admin   | admin@finance.dev   | admin123   |
| analyst | analyst@finance.dev | analyst123 |
| viewer  | viewer@finance.dev  | viewer123  |

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

---

## Role Permissions

| Endpoint                   | Viewer | Analyst | Admin |
| -------------------------- | ------ | ------- | ----- |
| `GET /transactions`        | ✓      | ✓       | ✓     |
| `GET /transactions/:id`    | ✓      | ✓       | ✓     |
| `POST /transactions`       | ✗      | ✗       | ✓     |
| `PATCH /transactions/:id`  | ✗      | ✗       | ✓     |
| `DELETE /transactions/:id` | ✗      | ✗       | ✓     |
| `GET /analytics/*`         | ✗      | ✓       | ✓     |

Viewers and analysts only see their own transactions. Admins see all.

---

## API Reference

### Auth

```
POST /auth/register   Register a new user
POST /auth/login      Obtain a JWT token
```

### Transactions

```
GET    /transactions                    List with filters + pagination
GET    /transactions/:id               Get a single transaction
POST   /transactions                    Create (admin only)
PATCH  /transactions/:id               Update (admin only)
DELETE /transactions/:id               Delete (admin only)
```

**Query parameters for listing:**

| Param       | Type   | Description                    |
| ----------- | ------ | ------------------------------ |
| `type`      | string | `income` or `expense`          |
| `category`  | string | Partial match                  |
| `from_date` | date   | `YYYY-MM-DD`                   |
| `to_date`   | date   | `YYYY-MM-DD`                   |
| `page`      | int    | Page number (default: 1)       |
| `page_size` | int    | Results per page (default: 20) |

### Analytics

```
GET /analytics/summary       Total income, expenses, and balance
GET /analytics/by-category   Spending grouped by category
GET /analytics/monthly       Income and expenses per month
GET /analytics/recent        Last N transactions (default: 10)
GET /analytics/dashboard     All of the above in a single response
```

---

## Running Tests

Tests use SQLite and require no database setup.

```bash
pytest tests/ -v
```

---

## Assumptions

1. **Decimal for amounts** — `Numeric(12, 2)` is used instead of float to avoid floating-point precision errors in financial calculations.
2. **User-scoped data** — Viewers and analysts can only access their own transactions. Admins have global visibility.
3. **Soft role creation** — Any role can be assigned at registration. In a production system this would be restricted to admin-only.
4. **Analytics aggregations are DB-level** — All summaries use SQL `GROUP BY` and `SUM` rather than in-memory computation, keeping the approach scalable.
5. **No soft deletes** — Transactions are hard-deleted. This keeps the schema simple for the scope of this assignment.
6. **updated_at on transactions** — Managed at the ORM level via `onupdate`. For production, a DB trigger would be more reliable.
