# AWS AI Practitioner — account-based learning app

A server-rendered Flask application with individual learner accounts, 65 topic deep dives, section references and 10 tests (650 questions). This **replaces** the previous static project. Keep this repository private.

## What changed

- Username + password registration and login; names alone cannot protect accounts.
- Scrypt password hashes, server-stored expiring sessions and logout revocation.
- One-time recovery keys for password resets without an email provider. Resetting invalidates existing sessions and rotates the key.
- SQLite stores each user's lessons, attempts, answers, flags, explanation views and activity.
- Saved attempts resume across devices after login. Multiple completed attempts remain available for review.
- Questions render individually on the server. There is no downloadable `data.js` question bank.
- Grading runs on the server. Timed tests reveal explanations only after submission; study mode reveals on request.
- All-or-nothing multi-select, matching and ordering grading. Source-key corrections and review-only exclusions are retained.
- Per-domain results and every-option explanations.
- No frontend JavaScript is required. Forms have CSRF protection; output is escaped; login/recovery are rate-limited.

## Privacy boundaries

The server Python code, database, password hashes and complete content JSON are never exposed by a public file route. The browser receives rendered HTML and CSS plus the question or lesson being viewed. **Every website's rendered browser content can be inspected or copied.** No website can make content invisible to a person while showing it to them. This design protects backend implementation and other users' records; it is not DRM. Users can review material they are allowed to access, including explanations after completing a test.

The operator can access the database as the site administrator. The app has no public user directory and no cross-user progress endpoint. Activity timestamps are UTC. Concurrent editing of the same attempt in multiple tabs is not supported; use one active tab per attempt.

## Replace the old repository contents

1. Set the existing GitHub repository to **Private**.
2. Remove the old `dist/`, `scripts/`, `package.json` and `.github/workflows/pages.yml` from that repository. Disable any old GitHub Pages deployment.
3. Upload the contents of this folder to the repository root, including `.github`, `.gitignore` and `private/`.
4. Commit with `Add user accounts, private server content and saved learning progress`.
5. Deploy as a Python web service, following DEPLOYMENT.md. GitHub Pages cannot run this app.

The `private/` name is descriptive, not an access control by itself. Flask serves only its `static/` directory and declared routes. Do not configure a web server to expose the entire project directory.

Previously published source copies or downloads cannot be recalled by changing repository visibility. Tests 1–4 contain supplied course material; only publish/share that material with the required permission.

## Run locally

Requires Python 3.12 (tested).

```sh
python -m venv .venv
```

Activate the environment:
- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

```sh
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:8000 and create an account. Local data persists in `instance/progress.sqlite3`. Local mode chooses an ephemeral signing secret if none is configured, so a restart may require signing in again; saved progress remains. Production requires a stable secret and HTTPS. `.env.example` is a configuration reference; Flask does not automatically load it in this project.

Answers save when pressing Save, Next, Previous, Flag or Finish. Use these before leaving a page. Timed deadlines continue while away and are enforced by the server; the displayed remaining minutes update on page navigation. Study mode has no deadline.

## Test

```sh
python -m unittest discover -s tests -v
```

Tests cover 650 question/explanation pages, all lesson pages, scoring, account isolation, persistence across login, session revocation, CSRF checks, private-file denial, rate limits and expired attempts. These are server integration tests, not visual browser tests.

## Layout

| Path | Purpose |
|---|---|
| `app.py` | Authentication, authorization, database, server grading and routes |
| `templates/` | Server-rendered screens |
| `static/` | Public CSS only |
| `private/content.json` | Server-only course and question data |
| `instance/` | Local database; excluded from Git |
| `tests/` | Server integration checks |
| `Dockerfile` | Optional container deployment |
| `DEPLOYMENT.md` | Private-repository/public-website hosting instructions |

## Operational limits

Designed for a small shared learning app using one server instance and a persistent SQLite disk. Do not use an ephemeral filesystem or multiple replicas with separate databases. For a larger audience, migrate to managed PostgreSQL, add robust edge abuse controls and operational monitoring. Behind a proxy, authentication rate limits use the direct peer IP by default; add provider-level rate limiting and configure trusted proxy handling for the exact deployment if needed. Do not blindly trust forwarded IP headers.

No email verification or email reset service is configured. Recovery is via the saved recovery key. Keep regular database backups. There is no self-service account deletion screen; the operator manages account-data requests. No blanket license grants redistribution of the supplied third-party tests.

Official learning sources remain in the authenticated Sources page. Content review date: 29 September 2026. Independent practice material; no certification guarantee.
