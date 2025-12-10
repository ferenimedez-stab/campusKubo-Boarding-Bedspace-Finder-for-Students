# CampusKubo — Emerging Tech & Architecture README

This document records the features and design notes that are currently present in this repository, and briefly lists design proposals that are not implemented here.

Project Overview & Problem Statement
- Project: CampusKubo — Boarding & Bedspace Finder for Students
- Problem statement: Provide a lightweight local-development-friendly application to discover and reserve student boarding/bedspace, and tools for property managers to list and manage properties.

What this repository currently implements (facts)
- UI: built with Flet — views, components, and navigation are implemented under `app/views` and `app/components`.
- Search & Browse: browse and search listings with filters and images; the live-search UX was implemented to update results in-place and preserve focus while typing.
- Accounts & RBAC: user accounts and role-based access controls exist (roles include visitor, tenant, PM, admin). Session handling and `SessionState` helpers are implemented.
- Reservations: basic reservation data model and reservation flows exist (models and services under `app/models` and `app/services`).
- Soft-delete: user/listing soft-delete support (a `deleted_at` column/migration exists in `app/storage`).
- Login UX: email format validation was added to the login flow; account lockout logic was adjusted (short-duration lockout) and the UI disables the login button with a countdown while locked out.
- Branding: a reusable `Logo` component was added at `app/components/logo.py` and used in primary navbars.
- Tests & docs: a unit test suite exists under `tests/` (tests were run during development), and documentation artifacts were added: `docs/SRS.md`, `docs/README_EMERGING_TECH.md`, `docs/campuskubo_schema.json`, `docs/ARCHITECTURE.md`, and `docs/architecture.puml`.

Design proposals / not implemented in this repository (explicit)
- Real-time updates (WebSocket server) — design notes and PlantUML exist, but no operational WebSocket server is included.
- AI-assisted inference (text summary, classification) — design guidance and fallback strategies are described, but no cloud-hosted AI integration or packaged on-device model is included in the repository.
- Offline-first sync, cloud sync, and edge device inference — these are listed as future enhancements or design notes and are not implemented here.

Scope Table (current state)
| Feature | Status | Notes |
|---|---|---|
| Browse & search listings | Implemented | Live in-place updates; consider adding debounce for production
| Listings CRUD | Implemented (basic) | Admin/PM CRUD available in code
| Reservations | Implemented (basic) | Reservation model and flows present; payments not integrated
| RBAC / Session handling | Implemented | `SessionState` and role checks used by views
| Email input validation | Implemented | Login validates presence of `@` and `.`
| Login lockout + cooldown UI | Implemented | Short-duration lockout with disabled login button and countdown UI
| Real-time updates | Not implemented (design only) | PlantUML and notes included as a proposal
| AI-assisted features | Not implemented (design only) | Design and fallback patterns provided in docs

Architecture (what's in the repo)
```
  [Flet UI (Desktop/Web client)]
           |
           v
  [Views & Components] --- [SessionState & Navigation]
           |
           v
  [Services Layer] (auth, listing, reservation, notification)
           |
           v
  [Storage Layer]
    - SQLite database in `app/storage/`
    - Local uploads in `assets/uploads/` (dev-focused)
```

Data model and schema
- Primary entities: Users, Listings, Reservations, Activity Logs, Login Attempts, Settings.
- A full JSON Schema describing these entities is provided in `docs/campuskubo_schema.json`.

Setup & Run (what works locally)
- Prerequisites: Python 3.11+ and a virtual environment are recommended.

Windows (PowerShell):
```powershell
python -m venv venv
venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app/main.py
```

Run tests:
```bash
pip install -r requirements.txt
pytest -q
```

**Data Model (overview)**
- Primary entities (simplified):
  - Users: { id, email, password_hash, role, full_name, deleted_at, created_at }
  - Listings: { id, title, address, price, description, owner_id, status, amenities, image_urls, availability_status, created_at }
  - Reservations: { id, listing_id, user_id, start_date, end_date, status, created_at }
  - Activity / Audit logs: { id, actor_id, action, metadata, created_at }

Example JSON schema snippets:
```
Listing {
  "id": 123,
  "title": "1BR near University",
  "address": "123 Campus St",
  "price": 6000,
  "amenities": ["wifi","fan","private_bath"],
  "owner_id": 7,
  "status": "approved",
}
```

ERD summary (text): Users 1--* Listings (owner relationship), Listings 1--* Reservations, Users 1--* Reservations. Activity logs reference users and objects by id.

**Emerging Tech Explanation & Integration**
This section enumerates the experimental / emerging features we can add, the rationale for choosing them, their integration approach, and limitations.

- Data visualization (interactive charts)
  - Why: Surface trends (bookings over time, occupancy rates, popular neighborhoods) for admin insight.
  - Integration: Use client-side charting via Flet components or embed small interactive charts (Plotly/Altair static images as fallback). Wire charts to aggregated data endpoints or in-memory events for near-real-time updates.
  - Limitations: Real-time charts need efficient aggregation; heavy datasets may require pre-aggregation or pagination.

**Technical Patterns & Responsibility**
- Defensive integration: each external integration uses a wrapper service that handles retries, exponential backoff, circuit breaker (soft failure), and returns a deterministic fallback.
- Feature flags: emergent features gated behind config flags to allow safe rollout and A/B testing.

**Setup & Run Instructions**
- Prerequisites: Python 3.11+ recommended. Windows / macOS / Linux supported. A virtual environment is strongly recommended.

Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app/main.py   # or use your run script
```

Windows (cmd.exe):
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python app/main.py
```

macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

Notes:
- If using experimental AI features that call external APIs, add credentials to environment variables (e.g., `OPENAI_API_KEY`) or a local `.env` file and restart the app.

**Testing Summary**
- Test runner: `pytest` is used for unit tests located under `tests/`.
- Run tests:
```bash
pip install -r requirements.txt
pytest -q
```
- Coverage notes: The repo contains unit tests for core services and views. Emerging features (real-time server, AI models) include only integration stubs by default — add integration tests against the simulated server or mock external APIs when enabling those features.

**Team Roles & Contribution Matrix**
- Product Owner: defines priorities and acceptance criteria
- Backend Engineer: services, storage, API, sync and background workers
- Frontend (Flet) Engineer: views, components, UX, offline handling
- ML / Data Engineer: model selection, inference integration, privacy review
- DevOps / Infra: optional WebSocket server, remote API endpoints, Redis/Cloud storage

Contribution Matrix (example):
| Role | Area | Primary Owner |
|---|---|---|
| Backend | DB, services, sync | Backend Engineer |
| Frontend | Flet views, components | Frontend Engineer |
| AI | Models & inference | ML Engineer |
| Infra | WS server, caches | DevOps |

**Risk / Constraint Notes & Future Enhancements**
- Risks:
  - SQLite suits small deployments; moving to PostgreSQL recommended for multi-user concurrency.
  - Background Python threads for UI updates are fragile — migrate to Flet timers or a proper event loop.

- Constraints:
  - Local file storage for images lacks durability and CDN performance; add object storage for production.
  - Client devices vary in capability — offline-first features must be carefully scoped.

- Future Enhancements:
  - Add a pluggable storage adapter (SQLite → PostgreSQL → Cloud DB)
  - Implement a microservice for real-time events and horizontal scaling
  - Add optional on-device ML models for image tagging or lightweight inference
  - Add analytic pipelines (ETL) for aggregated admin dashboards

---
