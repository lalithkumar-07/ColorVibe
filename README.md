# ColorVibe — Palette Generator

A color palette generator and manager built with **Flask**, **MySQL**, and
plain **HTML/CSS/JavaScript** — no TypeScript, no frontend framework, no
build step.

Generate palettes using real color-harmony rules (complementary, analogous,
triadic, monochromatic), lock the swatches you like, and save the ones you
want to keep to your account.

## Tech stack

- **Backend:** Python 3 + Flask (blueprints, MVC-style structure)
- **Database:** MySQL, accessed with parameterized queries via `mysql-connector-python`
- **Auth:** Server-side sessions, passwords hashed with Werkzeug's `generate_password_hash`
- **Frontend:** Static HTML templates (Jinja2) + hand-written CSS + vanilla JavaScript (`fetch`, no jQuery, no bundler)

## Project structure

```
colorvibe/
├── app.py                     # Flask app factory / entry point
├── config.py                  # Configuration from environment variables
├── requirements.txt
├── database/
│   ├── schema.sql              # MySQL DDL — run once to create tables
│   └── db.py                   # Connection handling + parameterized query helper
├── models/                     # Data access layer (one class per table)
│   ├── user.py
│   └── palette.py
├── controllers/                # Route handlers, grouped by feature (blueprints)
│   ├── main_controller.py      # Home page / generator
│   ├── auth_controller.py      # Register / login / logout
│   ├── palette_controller.py   # Palette CRUD + dashboard
│   └── api_controller.py       # JSON API for color generation
├── utils/
│   ├── color_utils.py          # Color math + harmony algorithms
│   └── validators.py           # Server-side form validation
├── templates/                  # Jinja2 templates (server-rendered HTML)
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── palette_detail.html
│   ├── auth/
│   └── partials/
└── static/
    ├── css/                    # base.css (tokens/reset), components.css, pages.css
    └── js/                     # generator.js, auth.js, dashboard.js, utils.js
```

## Setup

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create the database

Make sure MySQL is running locally, then:

```bash
mysql -u root -p < database/schema.sql
```

This creates the `colorvibe` database and its `users` / `palettes` tables.

### 3. Configure environment variables

Copy `.env.example` to `.env` (or export the variables directly) and set
your MySQL credentials and a real `SECRET_KEY`:

```bash
cp .env.example .env
```

If you're not using a tool that auto-loads `.env`, export the variables
manually before running the app, e.g.:

```bash
export MYSQL_USER=root
export MYSQL_PASSWORD=yourpassword
export SECRET_KEY=some-long-random-string
```

### 4. Run the app

```bash
python app.py
```

Visit **http://127.0.0.1:5000** in your browser.

## Features

- **Generate** — a Python-side harmony engine (`utils/color_utils.py`) produces
  palettes using complementary, analogous, triadic, monochromatic, or random rules.
- **Lock & shuffle** — lock swatches you like (press the lock icon or the
  spacebar to shuffle unlocked ones).
- **Copy** — click any hex code to copy it to your clipboard.
- **Accounts** — register/login with hashed passwords and server-side sessions.
- **Save (Create)** — save the current palette to your account.
- **Dashboard (Read)** — view all your saved palettes in a grid.
- **Rename (Update)** — rename a saved palette from the dashboard.
- **Delete** — remove a saved palette.
- **Export** — view any saved palette as CSS custom properties or JSON.
- **Validation** — every form is validated in the browser (JS) *and* re-validated
  on the server (Python), and every SQL query uses parameter placeholders.

## Security notes

- All SQL queries are parameterized (`%s` placeholders) — no string-built SQL.
- Passwords are hashed with `werkzeug.security.generate_password_hash`, never stored in plain text.
- Every palette-modifying route checks that the palette belongs to the
  logged-in user before reading or writing it.
- Session cookies are `HttpOnly` and `SameSite=Lax`.
- Change `SECRET_KEY` before deploying — the default in `config.py` is for local development only.
