# CellSense Research Lab

A noncommercial final-year research showcase by Adegoke Oluwakayode, Federal University Oye-Ekiti.

[Open CellSense](https://jlearning5.github.io/cellsense-research/) · [Prediction lab](https://jlearning5.github.io/cellsense-research/lab.html)

Eight static pages cover the overview, six-model prediction lab, dataset explorer, model comparison, methodology, held-out results, research library, and project context. Enter all 30 measurements, load explicitly synthetic quartile presets, or import a CSV batch of up to 100 records. JSON/CSV reports are exported locally.

## Run or edit

This repository is the ready-to-serve static site. Serve the root directory with any static file server; no build, framework, Python runtime, account, database, or API key is required. Edit app.js, styles.css, inference.js, and portable-worker.js directly. Models are in models/portable.json.

Predictions execute on the visitor’s device. Inputs are not uploaded. Hosting uses GitHub Pages; there are no paid runtime services or inference APIs.

## Evidence

The original experiment used 569 Wisconsin Diagnostic Breast Cancer records and 30 numeric predictors. Development/test counts: 455/114. The saved selection rule retained SVM because stacking’s mean-fold AP gain of 0.000315 was below the preset 0.001 minimum. SVM threshold: 0.31. Locked test accuracy: 97.37%; AP: 0.9931674424; confusion matrix: [[70,2],[1,41]]. No retraining or new research evaluation was performed for this app.

The compact browser implementation matched the original scikit-learn 1.6.1 pipelines on 25 synthetic application fixtures / 150 probabilities within 1e-8, with no classification disagreements. See models/provenance.json and docs/model-parity.json.

Design and research notes are in docs/. Design-reference browsing was partial; the full firsthand reference gate is not claimed complete. Viewport, accessibility, interaction, and preservation checks are described in docs/VERIFICATION.md and docs/verification-local.json.

## Scope and rights

This is research software, not a diagnostic tool or a personal cancer-risk calculator. No verified patient grouping or external clinical validation exists. Synthetic presets are not actual patients. KNN and SVM models inherently retain dataset-derived reference/support vectors.

Dataset: https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data . Mirror license: CC BY-NC-SA 4.0. Upstream attribution: Wolberg, Mangasarian, Street (1993), https://doi.org/10.24432/C5DW2B . Preserve attribution and noncommercial share-alike conditions. Self-hosted DM fonts use the SIL Open Font License; libsvm/scikit-learn notices are retained. See LICENSES.md.
