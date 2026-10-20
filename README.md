# CellSense Research Lab

Eight-page research showcase for **Breast Cancer Prediction Using a Stacking Machine Learning Ensemble**, Adegoke Oluwakayode, Federal University Oye-Ekiti, October 2026.

Open the overview, prediction lab, dataset explorer, model comparison, methodology, held-out results, research library, and project context. All 30 numeric inputs, three explicitly synthetic presets, six saved model pipelines, CSV batches up to 100 rows, local JSON/CSV report export, and original research figures are supported.

## Run locally

With Node.js installed, run `npm start` in this directory and open http://localhost:4173 . The compact production models are already present; no Python installation or paid service is needed. Input files and measurements stay in page memory and are never uploaded.

`npm run build` prepares `dist/` for static hosting. Runtime dependencies: none. The site has no prediction API, server functions, external font calls, analytics, login, subscription, or database.

## Scientific evidence

The existing study used `uciml/breast-cancer-wisconsin-data`, 569 rows / 30 predictors, 455 development rows and 114 stratified held-out test rows. SVM was retained because stacking's mean-fold AP gain 0.000315 did not meet the preset minimum 0.001. The selected SVM used a locked threshold of 0.31, giving held-out AP 0.9931674424, accuracy 0.9736842105, and confusion matrix `[[70,2],[1,41]]`. See the actual saved metrics; this website introduces no new research score.

The compact browser implementation was checked against the original scikit-learn 1.6.1 saved pipelines on 25 synthetic application fixtures / 150 model probabilities. All matched within 1e-8 with no class disagreements. These fixtures verify implementation agreement, not clinical validity or external generalization.

## Project boundaries

Original research files were preserved outside `UI-fixed`. No previous web application existed, so no invented original-app URL or before screenshot is supplied. `docs/original-files-manifest.json` supports content preservation checks. Design-reference research was partial due repeated browser-control deadlines; see the detailed record, including unfulfilled galleries, in `docs/RESEARCH-LOG.md`.

This app does not process mammograms or symptoms, diagnose patients, or provide a personal cancer-risk estimate. Patient linkage and external validation are absent. The original KNN/SVM artifacts inherently retain dataset-derived reference/support vectors. Preserve source attribution and noncommercial licensing conditions.

## Development and verification

Core source: `public/app.js`, `styles.css`, `inference.js`, `portable-worker.js`, and eight static HTML entry points. The compact model payload is `public/models/portable.json`; provenance and original-model hashes are in `models/provenance.json`. Design, motion, states, assets, evidence, free hosting, and limitations are documented under `docs/`.

Local engineering tests use Playwright and axe-core. On this Windows workstation, Playwright is provided by the bundled Codex runtime and launches installed Edge; `scripts/verify.mjs` records viewport, accessibility, interaction, privacy-network, download, and model-agreement checks. Set `VERIFY_URL` to test a deployed base URL. For another workstation, install Playwright or adjust its local package resolution. `scripts/parity.mjs` requires the local reference worker and Pyodide files prepared by `scripts/prepare.mjs`; these large engineering files are deliberately excluded from production deployment.

No new Kaggle notebook or training run was created. Kaggle was used read-only to verify metadata, file summary, and file tree. Browser export/parity is deployment engineering on the supplied saved artifacts.

## Deployment

Publish the contents of `dist/` through a public GitHub Pages repository using branch `main`, root `/`, with `.nojekyll`. Public GitHub Pages is available on GitHub Free; see https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits . Do not introduce paid inference or upgrade services automatically. Respect the site's educational/noncommercial purpose and GitHub's published usage limits.
