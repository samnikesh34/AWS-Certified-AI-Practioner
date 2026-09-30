# AWS AI Practitioner (AIF-C01) — Learn and Practice

A static website with lessons for the five AIF-C01 exam domains, ten 65-question practice tests with explanations, a review desk, and exam references. There is no backend or account system.

## Scoring

Results show an **estimated scaled score from 100 to 1000**, with the 700 pass mark, next to the number of questions correct.

AWS does not publish its exact conversion, so the estimate maps scored questions linearly: 0 correct is 100 and all correct is 1000. About 67% correct gives 700. Questions marked review-only, because of an ambiguous or outdated source key, are excluded. Treat the figure as a practice guide, not a prediction of your exam result.

## Profiles

Enter a username to start or resume. Progress is saved in your browser's local storage for each username. It is not authentication, and it does not sync between devices. Use **My profile & backup** to export or import progress.

## Run locally

```bash
python3 -m http.server 8000 --directory dist
```

Open http://localhost:8000.

## Publish with GitHub Pages

Commit the repository root (`dist/`, `scripts/`, `package.json`) to `main`, then set Settings → Pages → Source to GitHub Actions. Your existing deploy workflow publishes `dist/` unchanged.

## Tests

`npm test` (Node 20+) simulates the app in the DOM and checks all 650 question views, grading, timer behaviour, profile separation and backup validation. It does not test visual layout.

## Files

- `dist/app.js`: pages, quiz logic and scoring
- `dist/data.js`: lessons, questions and explanations
- `dist/profiles.js`: usernames, export and import
- `dist/style.css`: design
- `dist/study-notes.html`: downloadable notes

## Content notes

Independent study material, not official AWS exam questions. Tests 1–4 include supplied course material; get permission before redistributing it publicly. Content reference date: 29 September 2026.
