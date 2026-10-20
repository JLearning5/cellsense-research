# Design research log

Visit date: 20 October 2026, Africa/Lagos. This is a record of what was observed, not a claim that the full premium-saas-redesign research gate passed.

## Research status

The full firsthand gate is **incomplete**. Codex Browser returned an empty Awwwards document and a blank screenshot. Chrome initially provided working gallery and entry access, then repeatedly hit CDP dispatch/frame-tree deadlines and two 30-second browser-session timeouts. Native Computer access worked after restoring the minimized Chrome window, but only a gallery entry was visually confirmed through that route. No complete responsive, motion, or live-reference comparison is claimed.

The app implementation and its own Playwright testing can proceed independently. The design is original and evidence-led; reference-inspired features are not described as fully validated reproductions.

## Visits and observations

| Area | Gallery / entry | Live URL | Direct evidence and outcome | Adaptation / rejection |
| --- | --- | --- | --- | --- |
| Product Honors | https://www.awwwards.com/honors/winners#product | — | Opened in Codex Browser: blank document and screenshot. Chrome fallback rendered the gallery, category navigation, three product entries, and other honors areas. Scrolled two pages before opening a product entry. | Use concise product framing; do not depend on a heavy cinematic introduction. |
| Product entry 1 | https://www.awwwards.com/sites/lidar-drone-scanning | https://drone.riotters.com/ | Entry opened; live site opened. Live accessibility content exposed a menu, numbered technical sections, solution tabs, capability buttons, and expandable inspection points. The loader was at 0 in the initial state; screenshot capture timed out. No completed visual/motion assessment. | Numbered workflow and contextual measurements are relevant. Replace the terrain/3D metaphor with original lightweight SVG cell morphology. Do not reuse media. |
| Product entry 2 | https://www.awwwards.com/sites/the-watch | https://thewatch.60fps.fr/ | Entry opened and live link resolved. Live page first showed a loader; after a downward scroll, the FS 60P title and swap/hold/select-model controls were exposed. Rendering and motion were not fully verified. | Adapt clear experiment controls; reject hold-to-explore as the primary lab interaction. No 3D watch assets reused. |
| Business & Services Honors | https://www.awwwards.com/honors/winners#business-services | — | Category and latest entries were present in the rendered Honors document. Separate beyond-first-viewport visual exploration was not completed. | Partial gallery evidence only. |
| Business entry 1 | https://www.awwwards.com/sites/santioni-spirits | https://santionispirits.com/ | Entry opened; palette, illustration/storytelling elements, and live link read. Live navigation reached the correct title but returned an empty accessibility document with `CDP operation exceeded its deadline before command dispatch`. | Reject mandatory audio and a cinematic loader for a data-first research workspace. No claimed live-site visual findings. |
| Business entry 2 | https://www.awwwards.com/sites/why-zero | https://why.zero.university/ | Entry opened; live URL read. Live visit and controls not completed. | No live behavior adopted. |
| Typography Honors | https://www.awwwards.com/honors/winners#typography | — | Category and a-lign, Mosby's Files, PP Neue Montreal entries present in initial rendered Honors document. Separate deeper gallery inspection incomplete. | Provisional typography direction is original, using freely licensed DM fonts. |
| Typography entry 1 | https://www.awwwards.com/sites/a-lign-studio | https://www.a-lign.studio/ | Entry opened with Chrome. Native Computer screenshot confirmed the Awwwards entry, oversized title, centered hierarchy, and generous whitespace. Attempted live-tab creation timed out; no successful live inspection claimed. | Editorial headings adapted to an app shell; no fonts or assets taken from the reference. |
| Typography entry 2 | https://www.awwwards.com/sites/mosbys-files | https://mosbyfiles.com/ | Entry opened with Chrome; research-archive description, CSS folder-navigation concept, mobile/page-transition highlights, and live link inspected. Live site was not exercised. | Research-library concept is relevant, but keep conventional links and accessible navigation. Do not reproduce untested folder interactions. |
| Mobile & Apps | https://www.awwwards.com/websites/mobile-apps/ | — | Direct Chrome navigation attempted. `Timed out ... Page.getFrameTree`, followed by a further 30-second timeout and session reset. No verified entry selection. | Unfulfilled reference gate. App mobile composition verified separately. |
| UI design | https://www.awwwards.com/websites/ | — | Not directly inspected after the Chrome control route failed repeatedly. Current tag URL was not guessed. | Unfulfilled, explicitly not counted as a visit. |
| Data Visualization | https://www.awwwards.com/websites/ | — | Not directly inspected after the Chrome control route failed repeatedly. | Unfulfilled. App charts are original presentations of supplied metrics, with explicit aggregation labels. |
| Interaction Design | https://www.awwwards.com/websites/ | — | This tag was observed on the Mosby's Files entry; its gallery was not opened. | Unfulfilled gallery/live-entry requirement. |

No paywalls, subscriptions, paid courses, paid assets, or billable trials were used. Advertising prices on Awwwards were not acted on.

## Reference-to-implementation mapping

| Observed or original principle | Product need | Implementation | Responsive / accessible behavior | Verification |
| --- | --- | --- | --- | --- |
| Aevion's exposed numbered technical sections (DOM evidence only) | Explain how a measurement becomes a prediction | Overview workflow + detailed methodology timeline | Four compact tiles become a 2×2 grid; timeline retains readable order | Three viewport captures, semantic heading checks |
| Aevion's measurement context (DOM evidence only) | Keep result meaning attached to the number | Explicit SVM threshold, class mapping, all-model table, provenance | Result panel becomes a separate mobile block | Prediction and threshold parity checks |
| The Watch's exposed selection controls (partial live evidence) | Make exploration discoverable | Clearly named presets, feature tabs, comparison selector | Native buttons/selects, visible focus, keyboard tabs | Playwright interaction checks |
| a-lign entry's large title hierarchy (gallery visual evidence) | Give dense research an editorial entry point | Serif title, concise subtitle, quiet metadata | Fluid type; separate mobile illustration composition | Desktop/tablet/mobile visual review |
| Mosby's Files research-archive concept (entry evidence only) | Make evidence inspectable | Research library with actual artifact downloads and enlarged original figures | Conventional links, native dialog with Escape/close | Download and modal checks |
| Original CellSense decision | Avoid generic medical stock imagery and licensing ambiguity | Original cell-nuclei SVG, labeled schematic, radius annotation | CSS motion with pause and reduced-motion behavior; no WebGL | Rendered screenshots and pause-state test |
| Original CellSense decision | Show close scores without exaggeration | Zero-origin metric bars plus exact comparison table | Scrollable detailed tables, persistent row/column meaning | Data-to-artifact checks |

## Build comparison

There was no original web application, package manifest, or app route in the supplied project. The source documents, notebook, models, statistics, and figures are the preserved baseline. No fabricated before-app screenshots or local original-app URL are supplied. `original-files-manifest.json` records the original files for preservation checks.

See `VERIFICATION.md` for the app's own rendered and functional checks. Completing the full gallery and live-site research gate remains a design-research limitation.
