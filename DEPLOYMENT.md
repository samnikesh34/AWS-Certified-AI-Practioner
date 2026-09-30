# Publish the website, keep the repository private

This version needs a Python backend and durable storage. GitHub Pages and uploading just a `dist` folder are no longer suitable.

## Example: Render web service

1. Keep the GitHub repository **Private** and replace its contents with this project.
2. In Render, create a **Web Service** and authorize access only to this repository.
3. Select the Python runtime and configure:

| Setting | Value |
|---|---|
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 app:app` |
| Health check | `/health` |
| `APP_ENV` environment variable | `production` |
| `SECRET_KEY` environment variable | A unique random secret, at least 32 characters |
| `DATABASE_PATH` environment variable | `/var/data/progress.sqlite3` |
| Persistent disk mount path | `/var/data` |

Generate SECRET_KEY locally:

```sh
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste it into the host's secret environment settings. Do not commit it. Keep the same value across deploys. Use HTTPS; production cookies intentionally do not work over plain HTTP.

4. Choose a service plan that supports persistent disks and attach the disk **before** inviting learners. Persistent disk hosting may incur charges. Review the provider's current pricing. Without a persistent disk, account data can disappear after restart/redeployment.
5. Deploy. Open the provider's HTTPS website address and create your account.
6. Test a second account, complete a lesson and test, log out, and sign back in from another browser to verify persistence. Share the HTTPS website URL, not the GitHub repository URL.

Use one application instance with this SQLite implementation. The gunicorn command uses one process and four threads. Do not scale horizontally against independent local disks.

Official provider guides:
- https://render.com/docs/deploy-flask
- https://render.com/docs/disks

## Other hosts / Docker

The Dockerfile runs Gunicorn as a non-root user. Supply `SECRET_KEY`, keep `APP_ENV=production`, and mount a persistent writable volume at `/data`. Put the container behind the host's HTTPS endpoint. Port 8000 is the internal application port. Do not expose a directory listing or publish `private/` as static assets.

Only `static/` is intended as a public file directory. Back up the database through SQLite's backup API (not a partial copy of a running WAL file). Keep backups private. Periodically remove expired records from the sessions table.

## Existing website

This project does not automatically change or remove the earlier ChatGPT-hosted site or GitHub Pages site. Disable the old Pages deployment after switching, so visitors use the account-based version. Old browser-local progress is not automatically imported; the new account begins with a fresh record.
