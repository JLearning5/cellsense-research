# Verification evidence

Date: 20 October 2026. The application presents the supplied research results; these engineering checks do not establish a new research score or clinical validity.

## Saved-model agreement

The original saved scikit-learn 1.6.1 pipelines were loaded in a browser WebAssembly runtime. Their fitted preprocessing, SVM calibration, logistic coefficients, forest trees, KNN reference vectors, Gaussian parameters, and stacking meta-learner were serialized for a compact browser worker. No model was fitted or retuned.

Twenty-five synthetic application fixtures produced 150 model-probability comparisons. Tolerance: 1e-8. Maximum absolute error: 2.831068712794149e-15. Classification disagreements: zero across all six learners. This verifies implementation agreement on those fixtures, not performance on an independent patient sample. Exact per-model errors and fixture outputs are in `qa/model-parity.json` and `qa/parity-fixtures.json`.

## Local app checks

The final corrected Playwright run passed 24 route/viewport checks: eight pages at desktop 1440×1000, tablet 820×1180, and mobile 390×844. Every page loaded with one main heading and no document overflow. Twenty-four interaction checks passed, including navigation/Escape, pause/reduced motion, feature filtering and empty state, model-metric selection, figure enlargement, artifact download, input rejection, all input groups, six-model prediction, JSON export, stale-result invalidation, invalid CSV rejection, two-row batch inference, CSV export, and repeated model agreement.

Twenty-four axe-core scans reported zero WCAG A/AA violations in the tested default page states. The test context bypassed CSP solely to inject the local accessibility diagnostic; this is not a CSP/security certification. A normal browser-context production smoke check is recorded separately with the live release checks.

Observed application network activity during testing: zero network writes and zero external application requests. All model, font, script, figure, and evidence requests were local to the site origin. No browser errors remained. The machine recorded 13,226ms for the first compact prediction during the local diagnostic run; this includes load/parse/startup and is not a cross-device speed guarantee.

Raw results: `qa/local-verification.json`. Captures: `qa/local-index-desktop.png`, `local-index-tablet.png`, `local-index-mobile.png`, `local-lab-mobile-result.png`, and `local-lab-desktop-result.png`.

## Visual inspection

The desktop, tablet, and mobile overview and prediction views were inspected. Mobile has a distinct navigation drawer, 2×2 metric grid, shorter hero composition, and compact process tiles; tablet uses an icon rail and balanced evidence columns. Overflowing research tables are keyboard-focusable scroll regions. Secondary label contrast was strengthened after the first scan.

All seven web versions of supplied research figures were opened and visually inspected at readable resolution: feature correlations, precision–recall, ROC, calibration, ensemble diversity, stacking meta-coefficients, and final test confusion. Titles, axes, legends, panels, and confusion counts remained readable. Resizing was a web-delivery transformation; no plots or research metrics were regenerated. Original source plots are untouched.

## Preservation

All 183 original project files in the initial content manifest retained their byte sizes and SHA-256 hashes. Transfer metadata `sync.ffs_db` was excluded from the content manifest. See `preservation-verification.json` and `original-files-manifest.json`. No original web app existed, so there is no original-app port or fabricated before screenshot. Local QA used http://localhost:4173 in the separate `UI-fixed` project.

## Design research limitation

The invoked [premium-saas-redesign skill](C:/Users/user/.codex/skills/premium-saas-redesign/SKILL.md) says: “The research gate is complete only when the required areas have been explored firsthand”. That gate is incomplete. Codex Browser was blank, and the Chrome fallback later hit repeated CDP deadlines and session timeouts. Native Computer confirmed a gallery entry, not a complete live-reference audit. Exact visits, interactions, blocked visits, unfulfilled areas, and provisional pattern mappings are in `RESEARCH-LOG.md`.

## Interpretation limits

Automated accessibility checks are not a complete manual screen-reader or assistive-technology audit. The browser tested was Chromium-based Edge; Safari, Firefox, low-memory phones, and every possible CSV/input combination were not tested. The model experiment has no available patient linkage or external clinical validation. Synthetic presets are not actual patients. No inputs are needed to use the completed app; a verified externally representative dataset and a completed reference-research pass would support future improvements.
