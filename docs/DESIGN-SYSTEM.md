# CellSense design and experience specification

## Strategy and brand voice

Create a quiet scientific workspace: warm white, forest green, sage, dark ink, restrained serif headings, and precise sans-serif controls. Let evidence and the experiment carry the story. The research question is about stacking; the actual deployment choice is SVM under the saved rule. Never imply that the ensemble won, that a synthetic preset is a patient, or that a model score is a clinical risk estimate.

Voice: calm, specific, concise. Headings describe the task; actions use verbs. Empty: “Ready for your experiment.” Loading: describe actual local loading. Error: retain values and provide a recoverable next step. Success: confirm that computation completed locally. No sound, celebratory medical verdicts, account prompts, or subscription flows.

## Tokens

Source of truth: `public/styles.css` CSS custom properties. Background #f5f6f2, white cards, ink #192f2b, muted #63736d, borders #dce3dc, forest #164f45, accent #d6edbc, pale #e9f1e5, malignant/attention #ab5869, amber #886222. Selection does not rely on color alone. Shadows are low-contrast, with 7–18px radii and consistent spacing.

DM Serif Display provides editorial headings; self-hosted variable DM Sans provides body, controls, and tabular metric values. Fluid title sizing uses clamp. Data labels retain the exact statistic and evaluation split.

## Layout and responsive behavior

Desktop: full fixed navigation, generous workspace header, split hero, four headline metrics, asymmetrical evidence grid, two-column lab with result panel. Tablet: navigation becomes an icon rail, hero compresses, the lab becomes one column, and secondary grids reduce density. Mobile: explicit menu/dismissible overlay, compact sticky header, re-composed hero, 2×2 metrics, single-column cards, 2×2 process tiles, horizontally scrollable dense data tables. Mobile is not merely a stacked desktop canvas.

## Visual asset system

The original SVG cell illustration supports the actual domain: contours, nuclei, a radius measurement, and a dimensional grid. It is explicitly labeled a schematic, not a microscopy image. The original research plots are preserved and lazy-loaded with enlargement controls. No photos, generated imagery, video, 3D models, sound, or copyrighted reference assets are needed. Avoid WebGL cost where it adds no research value.

## Motion language

Interaction: 220ms cubic-bezier(.2,.7,.2,1); subtle hover lift and pressed return. Page entry: 220–350ms opacity/7px translation. Illustration: slow 8-second drift, visible pause/resume. Loading: progress motion only while work is pending. Every animation/transition is disabled under prefers-reduced-motion. No cursor replacement or scroll hijacking.

## Component state matrix

| Component | Default / selected | Hover / focus / pressed | Disabled / loading | Empty / success / warning / error |
| --- | --- | --- | --- | --- |
| Navigation | Labeled current page, marker + aria-current | Surface tint; visible focus; native link activation | No artificial disabled pages | Mobile open/closed state, Escape and overlay dismissal |
| Inputs & tabs | Three groups, ten values each, preserved input buffer | Native number fields, visible focus; arrow/Home/End tab keys | Prediction prevents duplicate submit | Filled counter; invalid field focus + alert; out-of-range warning |
| Prediction actions | Run six saved learners | High-contrast focus and pressed shift | Disabled for pending work; status region | Recoverable engine error, values retained; results exported only when current |
| Presets | Explicit synthetic quartiles | Native button states | Ignore changes while prediction is running | Changes invalidate the old result |
| Batch import | Native file picker + exact schema guidance | Keyboard-accessible picker | Run disabled without valid batch or during work | Missing/duplicate/unknown/nonnumeric rejection; ready count; result table |
| Data filters | All summaries / chosen metric | Native search, select, checkbox | No fake asynchronous refresh | No-match row; instant real-statistic filtering |
| Metric cards / bars | Exact evidence and evaluation split | Informational, not clickable decoration | Evidence loading and retry state | Explicit source boundaries; no fabricated live telemetry |
| Figures | Original artifact + meaningful caption | Enlarge button, visible focus | Lazy-load image | Native dialog, Escape/close/backdrop dismissal |
| Downloads | Named artifact links | Link/button hover and keyboard focus | Export unavailable until results exist | Local Blob export, downloaded status message |

## Data visualization guide

Use zero-origin bars for model comparisons, never a visually amplified truncated axis. Distinguish mean outer-fold AP from pooled OOF AP and final test AP. The class donut shows actual 357/212 totals. The test confusion matrix names all four outcomes and labels the axes. Confidence intervals retain the bootstrap unit and conditional interpretation. The probability strip marks the locked 0.31 threshold; individual model scores are never presented as patient risk, certainty, or a fabricated explanation. Meta-coefficients are not causal effects. No decorative sparklines, invented trends, freshness timestamps, or made-up feature attributions.

## Accessibility and performance

Landmarks, one main heading, skip link, labels, visible focus, table headings/captions, dialog semantics, current-page labels, keyboard navigation, and reduced motion. Automated accessibility scans supplement, not replace, manual evaluation. Small text is reserved for secondary provenance; primary actions retain generous hit areas.

Eight actual HTML pages, buildless modules, self-hosted fonts, lazy original figures, no analytics, and no network writes. Prediction runs in a worker so the interface remains responsive. Compact saved-model parameters avoid shipping the scientific Python runtime to production. Verify numeric parity against the original saved pipelines before switching the production worker. No paid inference or server compute.
