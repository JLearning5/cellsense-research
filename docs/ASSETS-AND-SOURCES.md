# Asset, source, and cost inventory

Checked 20 October 2026.

| Material | Source / creator | Rights / use | Local location / production status |
| --- | --- | --- | --- |
| CellSense cell-nuclei artwork, logo, interface icons | Original SVG and CSS created for this project | Original project material; no third-party reference media copied | `public/icon.svg`, `public/app.js`, `public/styles.css`; production |
| DM Sans | Google Fonts, Colophon Foundry | SIL Open Font License; license text downloaded | `public/fonts/sans.ttf`, `dmsans-OFL.txt`; production |
| DM Serif Display | Google Fonts, Colophon Foundry | SIL Open Font License; license text downloaded | `public/fonts/serif.ttf`, `dmserifdisplay-OFL.txt`; production |
| Font official sources | https://github.com/google/fonts/tree/main/ofl/dmsans and https://github.com/google/fonts/tree/main/ofl/dmserifdisplay | Actual font files downloaded, self-hosted; no runtime font API | Sizes and hashes in dependency inventory |
| Saved models, statistics, figures, original pipeline | Supplied `code/breast_cancer_stacking_artifacts` | User-provided project evidence; preserved originals. Reuse dataset-derived material with source attribution and mirror license conditions | Selected model parameters, figures, and downloads; production |
| Dataset metadata | https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data | Kaggle reports CC BY-NC-SA 4.0; noncommercial showcase with attribution. The upstream UCI entry separately reports CC BY 4.0; do not conflate the sources | Kaggle metadata evidence saved in docs; no new raw dataset download |
| Upstream dataset | Wolberg, Mangasarian, Street. https://doi.org/10.24432/C5DW2B | Attribution source; https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic | Provenance reference |
| scikit-learn 1.6.1 / libsvm probability computation | https://github.com/scikit-learn/scikit-learn/tree/1.6.1/sklearn/svm/src/libsvm | BSD-style license; required notices retained | Numerical implementation adapted for compact browser inference; production |
| Pyodide 0.27.7 | https://github.com/pyodide/pyodide/tree/0.27.7 ; https://cdn.jsdelivr.net/pyodide/v0.27.7/full/ | Open-source; dependency wheel checksums verified against official lock file | Local engineering reference for model serialization/parity; excluded from compact production deployment |
| Awwwards reference media | Owners listed in RESEARCH-LOG.md | Viewing does not grant reuse; no reference media or paid fonts downloaded | Research links only; none shipped |

The KNN model inherently retains fitted reference vectors, and SVM retains support vectors. Model artifacts can therefore contain recoverable dataset-derived measurements. No private user-entered measurements are included in the production bundle. Browser inputs remain in page memory, and selected report exports are saved locally.

The supplied high-resolution plots were resized for web display to at most 1800 pixels per dimension. Their data, labels, layout, and meaning were preserved; no research plot was regenerated. Source and web dimensions/byte sizes are in `web-figure-inventory.json`. Original high-resolution files remain unchanged in the original research folder.

The license-safe visual direction needs no stock images, AI image service, 3D service, video generator, paid font, sound library, or credit-card trial. Actual downloaded file byte sizes, SHA-256s, URLs, and scientific dependency metadata are recorded in `dependency-inventory.json`; final production inventory is recorded separately.

## Free hosting decision

Use a public GitHub repository and GitHub Pages for a noncommercial educational site. GitHub documents Pages availability on GitHub Free for public repositories: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits . Official limits include a 1GB published site, a 100GB/month soft bandwidth limit, and rate limits. This app is well below the size limit and does not use Actions minutes, billable functions, a custom domain purchase, hosted prediction, an external inference endpoint, or a database. If a usage limit is reached, do not upgrade to a paid plan automatically.

The existing GitHub CLI login was verified before publishing. Public documentation was not treated as evidence of account access; successful repository creation, Pages configuration, and live HTTP checks must be recorded in the delivery report.
