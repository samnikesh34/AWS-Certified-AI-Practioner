# AWS AI Practitioner — username profiles

A static website with 10 tests (650 questions), lessons, explanations and review. No database, passwords, API keys or backend required.

## How profiles work

Enter a username to start or resume. Names are case-insensitive and can contain 2–30 letters, numbers, underscores or hyphens. Progress saves automatically in localStorage, separately for each username on that browser and website address. It is a profile selector, not authentication. Anyone using the same browser can select the same name.

Other people on other devices have independent local progress even if they choose the same name. Clearing browser data removes progress. Private browsing may erase progress on exit. No automatic cross-device synchronization is possible without shared storage.

Use **My profile & backup** in the sidebar to switch usernames, view recent lesson/test activity, export progress or import a backup on another device. Import replaces the current profile's progress after confirmation. Export regularly. Retaking a test replaces that test's detailed attempt; the recent activity list keeps completion summaries (up to 200 events). Existing progress from the earlier app is not automatically migrated.

## Run in Visual Studio Code

1. Extract this ZIP and open the project folder in VS Code (File → Open Folder).
2. Open the terminal and run `python -m http.server 8000 --directory dist` (or `python3` on macOS/Linux).
3. Open http://localhost:8000.

Alternatively open `dist/index.html` directly, though a local HTTP server gives more consistent browser storage. No npm installation is required. Stopping the local server stops that local link only.

## Share a link that works with your laptop off

Host the project on GitHub Pages. GitHub serves the files independently of your computer.

1. Replace the previous project in your GitHub repository with this folder's contents. Remove the previous Flask files if you uploaded the account-based version.
2. Include `.github/workflows/pages.yml`, `dist/`, `scripts/` and `package.json` at the repository root.
3. Commit to `main`.
4. In Settings → Pages, choose GitHub Actions as the source.
5. In Actions, run **Deploy learning project to GitHub Pages**.
6. After a successful deployment, use Settings → Pages → Visit site and share that HTTPS link.

The workflow checks the app before publishing. Hosting does not depend on your laptop. Localhost links cannot be shared this way.

## Source visibility

This static version sends JavaScript, lessons and question data to browsers; visitors can inspect them. Hiding all source is incompatible with this no-backend design. A private repository can hide repository history, but not delivered website assets. GitHub Pages from a private repository needs an eligible paid GitHub plan; alternatively host `dist/` separately while retaining a private repository. Tests 1–4 contain supplied course material; obtain permission before publicly redistributing it.

## Verification and files

Run `npm test` with Node 20+. Checks cover the 650 question and explanation views, grading, timer behavior, username separation, resume, activity and backup validation. They are DOM-simulation checks, not browser visual tests.

- `dist/profiles.js`: username selection, progress export/import, profile activity.
- `dist/app.js`: learning and test UI.
- `dist/data.js`: all learning content and questions.
- `dist/style.css`: responsive layout.
- `dist/study-notes.html`: table-format notes.
- `.github/workflows/pages.yml`: publishing workflow.

Independent study material; practice percentages are not AWS scaled scores. Question-key caveats remain marked review-only. Six original practice sets repeat concepts across scenarios. Content reference date: 29 September 2026.
