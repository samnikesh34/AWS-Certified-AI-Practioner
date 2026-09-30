# AWS AI Practitioner Exam Study Platform

A modern, offline-first learning platform for AWS AI Practitioner (AIF-C01) certification with 650 practice questions across 5 exam domains. No backend, database, or authentication required.

## Key Features

- **10 Practice Tests**: 650 comprehensively explained questions aligned with exam domains
- **Offline Capable**: Works entirely in-browser using local storage
- **Profile System**: Track multiple learners with independent progress on one device
- **Complete Offline**: No internet connection required after initial load
- **Study Notes**: Reference material organized by domain in table format

## Quick Start

### Run Locally

1. Extract the ZIP file
2. Open the project folder in VS Code (File → Open Folder)
3. Start a local server:
   ```bash
   python -m http.server 8000 --directory dist
   ```
   Or on macOS/Linux: `python3 -m http.server 8000 --directory dist`
4. Visit `http://localhost:8000`

**Note**: A local HTTP server provides better browser storage consistency than opening `dist/index.html` directly.

### Deploy to GitHub Pages

1. Push the project to a GitHub repository
2. Include at the root:
   - `.github/workflows/pages.yml`
   - `dist/` folder
   - `scripts/` folder
   - `package.json`
3. Enable GitHub Pages in Settings → Pages with GitHub Actions as source
4. Run the deployment workflow in Actions
5. Share the published HTTPS link

## How Profiles Work

- **Username**: Create or resume a profile (2–30 characters: letters, numbers, underscores, hyphens)
- **Local Storage**: Progress saves automatically in your browser, not synced online
- **Profile Backup**: Export and import progress using "My profile & backup" in the sidebar
- **Device Specific**: Each device maintains independent progress, even with the same username

**Best Practice**: Export progress regularly as a backup before clearing browser data.

## File Structure

- `dist/index.html`: Main application
- `dist/app.js`: Learning and test interface
- `dist/data.js`: All questions and explanations
- `dist/profiles.js`: Profile management and data export/import
- `dist/style.css`: Responsive design
- `dist/study-notes.html`: Reference material by domain
- `scripts/check_app.cjs`: Quality checks (run with `npm test`)

## Quality Assurance

Run `npm test` (requires Node 20+) to validate:
- All 650 question explanations
- Grading logic and timer functionality
- Profile save/restore and data backup
- Cross-domain question accuracy

## Content Notes

- **Exam Coverage**: Organized by the five AIF-C01 domains
- **Practice Scores**: Not equivalent to AWS scaled scores
- **Source Material**: Tests 1–4 contain licensed course content
- **Last Updated**: 29 September 2026

## Licensing & Attribution

Obtain permission before redistributing course material from tests 1–4.

## Support

For issues or improvements, review the code structure and test output. All functionality uses standard browser APIs.
