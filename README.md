# AWS AI Practitioner Learning Project

A standalone, responsive learning website for AWS Certified AI Practitioner (AIF-C01). Built with plain HTML, CSS and JavaScript. No AWS account, API key, backend, framework or package installation is required.

## Included

- 65 detailed topic lessons with worked scenarios and service comparisons.
- Searchable table-format study notes and official AWS references.
- 10 tests with 65 questions each: four supplied practice tests and six new scenario tests.
- Every-option explanations, review flags, missed-question review and domain scores.
- Study mode and timed practice with 90/120-minute settings.
- Browser-local progress; moving to a different domain or browser starts separate progress.

## Run locally

From this project folder:

```sh
python3 -m http.server 8000 --directory dist
```

On Windows, use `py` instead of `python3` if needed. Open http://localhost:8000. You can also open `dist/index.html` directly, but a local server is recommended for consistent browser storage behavior.

## Upload to GitHub

1. Extract the ZIP.
2. Create an empty GitHub repository. Use a private repository for your personal copy of the supplied tests.
3. Upload the **contents** of this folder, including `.github/workflows/pages.yml`, to the repository root. Do not upload the ZIP itself as the project.
4. Commit to `main`. The root should contain `README.md`, `package.json`, `dist/`, `scripts/` and `.github/`.

Alternatively, from this folder, replacing YOUR-USER and YOUR-REPO:

```sh
git init
git add .
git commit -m "Add AI Practitioner learning project"
git branch -M main
git remote add origin https://github.com/YOUR-USER/YOUR-REPO.git
git push -u origin main
```

## Optional GitHub Pages hosting

In repository **Settings → Pages → Build and deployment**, select **GitHub Actions** as the source. Then open **Actions → Deploy learning project to GitHub Pages → Run workflow**. Subsequent pushes to `main` trigger deployment automatically. The workflow publishes only `dist/` and displays the site URL on completion.

GitHub Pages availability for private repositories depends on your GitHub plan. A private repository does not necessarily make its Pages website private. The four supplied tests may contain third-party course material: keep the project for personal use unless you have permission to distribute that content publicly.

Workflow reference: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## Edit the project

| File | Purpose |
| --- | --- |
| `dist/index.html` | Page entry point, title, stylesheet and script loading |
| `dist/style.css` | Layout, colors, typography and responsive styles |
| `dist/app.js` | Navigation, quizzes, scoring, timers and local progress |
| `dist/data.js` | Lessons, questions, per-option explanations and AWS source links |
| `dist/study-notes.html` | Downloadable table-format study notes |
| `scripts/check_app.cjs` | Dependency-free Node functional checks |
| `.github/workflows/pages.yml` | Automated checks and optional Pages deployment |

All links to local assets are relative, supporting GitHub repository subpaths. The interface uses Google Fonts with system-font fallbacks. No analytics or server-side tracking is included.

## Verify changes

With Node.js 20 or newer:

```sh
npm test
```

These checks exercise all 650 question and explanation views, answer persistence, exact grading, flags, navigation and timers in a lightweight DOM simulation. They do not replace visual browser testing.

## Study and scoring notes

Official sources were checked on 29 September 2026. This is independent learning material, not an official AWS question bank. No passing outcome is guaranteed. Practice percentages are not AWS scaled scores.

Tests 1–4 preserve supplied questions and keys, with correction notes. Ambiguous or outdated items are marked review-only and excluded from adjusted scores. Tests 5–10 reuse concepts across distinct scenarios for learning; they are not independent readiness measurements. The 120-minute setting is intended for an approved exam accommodation.

Content is maintained directly in `dist/data.js`; there is no build step. No ChatGPT hosting configuration, credentials or source-repository history is included in this export. No blanket redistribution license is granted for the supplied third-party test material.
