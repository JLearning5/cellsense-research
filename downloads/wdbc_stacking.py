import ast
import atexit
import gc
import hashlib
import io
import json
import os
import platform
import re
import resource
import sys
import threading
import time
import tokenize
import zipfile
from contextlib import contextmanager
from pathlib import Path
import joblib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psutil
import sklearn
from IPython.display import display
from PIL import Image
from matplotlib.colors import ListedColormap
from sklearn.base import clone
from sklearn.calibration import calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, balanced_accuracy_score, brier_score_loss, classification_report, confusion_matrix, f1_score, fbeta_score, log_loss, precision_score, recall_score, roc_auc_score, roc_curve, precision_recall_curve
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

START = time.perf_counter()
SEED = 42
RUN_ID = "wdbc_stacking_20261007_v1"
OUT = Path(os.environ.get("STUDY_OUTPUT", "/kaggle/working/wdbc_stacking"))
FIGURE_DPI = int(os.environ.get("FIGURE_DPI", "1200"))
EXPECTED_CODE_CELLS = 8
BOOTSTRAPS = 2000
MODEL_IDS = ["Dummy", "Logistic", "SVM", "RandomForest", "KNN", "GaussianNB", "Stacking"]
PALETTE = ["#707070", "#0072B2", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#111111"]
IP = get_ipython() if "get_ipython" in globals() else None
CODE_CELL_START = len(IP.history_manager.input_hist_raw) - 1 if IP is not None else 0
for directory in ["models", "preprocessors", "metrics", "figures", "environment", "logs", "source"]:
    (OUT / directory).mkdir(parents=True, exist_ok=True)
np.random.seed(SEED)
matplotlib.rcParams.update({"figure.dpi": 110, "font.size": 9, "axes.grid": False, "savefig.facecolor": "white"})
RESOURCES = []
FIGURES = []

def runtime_output():
    print("TOTAL_RUNTIME_SECONDS", round(time.perf_counter() - START, 3), flush=True)

atexit.register(runtime_output)

def error_runtime(result):
    if result.error_in_exec is not None or result.error_before_exec is not None:
        runtime_output()

if IP is not None:
    IP.events.register("post_run_cell", error_runtime)

def save_json(relative, value):
    (OUT / relative).write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")

@contextmanager
def monitor(model_id, phase, fold):
    process = psutil.Process()
    process.cpu_percent()
    stop = threading.Event()
    initial = time.perf_counter()
    samples = []
    def sample():
        while not stop.is_set():
            samples.append({"elapsed_seconds": time.perf_counter() - initial, "rss_mb": process.memory_info().rss / 1048576, "cpu_percent": process.cpu_percent()})
            stop.wait(0.25)
    worker = threading.Thread(target=sample, daemon=True)
    worker.start()
    try:
        with threadpool_limits(limits=2):
            yield
    finally:
        stop.set()
        worker.join()
        elapsed = time.perf_counter() - initial
        samples.append({"elapsed_seconds": elapsed, "rss_mb": process.memory_info().rss / 1048576, "cpu_percent": process.cpu_percent()})
        RESOURCES.append({"model_id": model_id, "phase": phase, "fold": fold, "wall_seconds": elapsed, "peak_rss_mb": max(s["rss_mb"] for s in samples), "mean_rss_mb": float(np.mean([s["rss_mb"] for s in samples])), "mean_cpu_percent": float(np.mean([s["cpu_percent"] for s in samples])), "samples": samples})

def finish_figure(fig, figure_id, models):
    FIGURES.append({"id": figure_id, "models": models})
    for ax in fig.axes:
        ax.grid(False)
    fig.savefig(OUT / ("figures/" + figure_id + ".png"), dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
    print("FIGURE_ID", figure_id, flush=True)
    plt.show()
    plt.close(fig)
    gc.collect()

def score_metrics(labels, scores, threshold):
    prediction = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(labels, prediction, labels=[0, 1]).ravel()
    return {"average_precision": float(average_precision_score(labels, scores)), "roc_auc": float(roc_auc_score(labels, scores)), "accuracy": float(accuracy_score(labels, prediction)), "balanced_accuracy": float(balanced_accuracy_score(labels, prediction)), "precision": float(precision_score(labels, prediction, zero_division=0)), "recall": float(recall_score(labels, prediction)), "specificity": float(tn / (tn + fp)), "f1": float(f1_score(labels, prediction)), "f2": float(fbeta_score(labels, prediction, beta=2)), "macro_f1": float(f1_score(labels, prediction, average="macro")), "brier": float(brier_score_loss(labels, scores)), "log_loss": float(log_loss(labels, scores, labels=[0, 1])), "threshold": float(threshold), "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}

print("RUN_ID", RUN_ID)
print("RUNTIME_ENVIRONMENT", platform.platform(), sklearn.__version__, os.cpu_count())

data_paths = sorted(set(p.resolve() for p in Path("/kaggle/input").rglob("data.csv")))
print("DATA_PATHS", [str(p) for p in data_paths], flush=True)
matches = [p for p in data_paths if "breast-cancer-wisconsin-data" in str(p)]
assert len(matches) == 1, "DATA_ATTACHMENT_MISSING_OR_AMBIGUOUS"
DATA_PATH = matches[0]
raw = pd.read_csv(DATA_PATH)
assert {"id", "diagnosis"}.issubset(raw.columns), "SCHEMA_MISMATCH"
assert set(raw["diagnosis"].unique()) == {"B", "M"}, "TARGET_MISMATCH"
empty_columns = [c for c in raw.columns if c.startswith("Unnamed:") and raw[c].isna().all()]
features = raw.drop(columns=["id", "diagnosis"] + empty_columns)
assert features.shape[1] == 30 and all(pd.api.types.is_numeric_dtype(features[c]) for c in features), "FEATURE_SCHEMA_MISMATCH"
assert np.isfinite(features.to_numpy(dtype=float)).all(), "NONFINITE_FEATURES"
assert not raw["id"].duplicated().any(), "REPEATED_ID_REQUIRES_GROUP_SPLIT"
assert not features.duplicated().any(), "DUPLICATE_FEATURES_REQUIRE_GROUP_SPLIT"
labels = raw["diagnosis"].map({"B": 0, "M": 1}).astype(int)
row_ids = np.array([hashlib.sha256(str(v).encode()).hexdigest()[:16] for v in raw["id"]])
all_rows = np.arange(len(raw))
development, test = train_test_split(all_rows, test_size=0.2, stratify=labels, random_state=SEED)
development, test = np.sort(development), np.sort(test)
assert not set(development).intersection(test), "SPLIT_OVERLAP"
X_dev = features.iloc[development].reset_index(drop=True)
y_dev = labels.iloc[development].to_numpy()
X_test = features.iloc[test].reset_index(drop=True)
outer = list(RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=SEED).split(X_dev, y_dev))
split_rows = [{"row_id": row_ids[i], "split": "development" if i in set(development) else "test"} for i in all_rows]
fold_membership = [{"repeat": k // 5 + 1, "fold": k % 5 + 1, "training_ids": row_ids[development[train_index]].tolist(), "validation_ids": row_ids[development[valid_index]].tolist()} for k, (train_index, valid_index) in enumerate(outer)]
split_manifest = {"seed": SEED, "test_fraction": 0.2, "outer_folds": 5, "repeats": 2, "stack_inner_folds": 5, "rows": split_rows, "folds": fold_membership}
split_hash = hashlib.sha256(json.dumps(split_manifest, sort_keys=True).encode()).hexdigest()
split_manifest["sha256"] = split_hash
save_json("metrics/split_manifest.json", split_manifest)
data_audit = {"path": str(DATA_PATH), "dataset": "uciml/breast-cancer-wisconsin-data", "data_sha256": hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(), "rows": len(raw), "features": list(features.columns), "dropped_columns": ["id", "diagnosis"] + empty_columns, "target_counts": raw["diagnosis"].value_counts().to_dict(), "missing_predictors": int(features.isna().sum().sum()), "duplicate_ids": int(raw["id"].duplicated().sum()), "duplicate_predictors": int(features.duplicated().sum()), "development_n": len(development), "test_n": len(test), "development_positive_n": int(y_dev.sum()), "test_positive_n": int(labels.iloc[test].sum()), "patient_linkage_available": False}
save_json("metrics/data_audit.json", data_audit)
X_dev.describe().T.to_csv(OUT / "metrics/development_feature_summary.csv")
print("DATA_AUDIT", json.dumps(data_audit))
print("SPLIT_HASH", split_hash)
fig, ax = plt.subplots(figsize=(4.2, 3.1), layout="constrained")
counts = raw["diagnosis"].value_counts().reindex(["B", "M"])
bars = ax.bar(["Benign", "Malignant"], counts, color=["#0072B2", "#D55E00"])
ax.bar_label(bars, padding=3)
ax.set(title="Dataset Class Distribution", ylabel="Observations", ylim=(0, max(counts) * 1.16))
finish_figure(fig, "class_balance", [])
fig, ax = plt.subplots(figsize=(6.2, 5.5), layout="constrained")
correlations = X_dev.corr()
image = ax.imshow(correlations, vmin=-1, vmax=1, cmap="RdBu_r")
ax.set_xticks(range(30), features.columns, rotation=90, fontsize=6)
ax.set_yticks(range(30), features.columns, fontsize=6)
ax.set_title("Development Feature Correlations")
fig.colorbar(image, ax=ax, shrink=0.72, label="Pearson r")
finish_figure(fig, "feature_correlations", [])

def scaled(estimator):
    return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), estimator)

def model_set(seed):
    bases = {
        "Logistic": scaled(LogisticRegression(C=1.0, max_iter=3000, random_state=seed)),
        "SVM": scaled(SVC(C=2.0, kernel="rbf", gamma="scale", probability=True, random_state=seed)),
        "RandomForest": make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=200, min_samples_leaf=2, max_features="sqrt", random_state=seed, n_jobs=2)),
        "KNN": scaled(KNeighborsClassifier(n_neighbors=7, weights="distance", n_jobs=2)),
        "GaussianNB": scaled(GaussianNB())
    }
    stack = StackingClassifier(estimators=[(name, clone(estimator)) for name, estimator in bases.items()], final_estimator=make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=3000, random_state=seed)), cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=seed + 1000), stack_method="predict_proba", passthrough=False, n_jobs=1)
    return {"Dummy": DummyClassifier(strategy="prior"), **bases, "Stacking": stack}

OOF = {name: np.full((2, len(development)), np.nan) for name in MODEL_IDS}
fold_records = []
training_records = []
for fold_number, (train_index, valid_index) in enumerate(outer):
    repeat = fold_number // 5
    seed = SEED + fold_number
    for name, estimator in model_set(seed).items():
        with monitor(name, "outer_fit", fold_number + 1):
            estimator.fit(X_dev.iloc[train_index], y_dev[train_index])
        prediction_start = time.perf_counter()
        scores = estimator.predict_proba(X_dev.iloc[valid_index])[:, 1]
        OOF[name][repeat, valid_index] = scores
        training_scores = estimator.predict_proba(X_dev.iloc[train_index])[:, 1]
        record = {"model_id": name, "repeat": repeat + 1, "fold": fold_number % 5 + 1, "inference_seconds": time.perf_counter() - prediction_start, **score_metrics(y_dev[valid_index], scores, 0.5)}
        fold_records.append(record)
        training_records.append({"model_id": name, "repeat": repeat + 1, "fold": fold_number % 5 + 1, **score_metrics(y_dev[train_index], training_scores, 0.5)})
    print("OUTER_FOLD_COMPLETE", fold_number + 1, flush=True)
assert all(np.isfinite(scores).all() for scores in OOF.values()), "OOF_INCOMPLETE"
oof_mean = {name: scores.mean(axis=0) for name, scores in OOF.items()}
fold_table = pd.DataFrame(fold_records)
fold_table.to_csv(OUT / "metrics/fold_metrics.csv", index=False)
pd.DataFrame(training_records).to_csv(OUT / "metrics/training_metrics.csv", index=False)
predictions = pd.DataFrame({"row_id": row_ids[development], "true_label": y_dev})
for name in MODEL_IDS:
    predictions[name + "_repeat_1"] = OOF[name][0]
    predictions[name + "_repeat_2"] = OOF[name][1]
    predictions[name + "_mean"] = oof_mean[name]
predictions.to_csv(OUT / "metrics/development_oof_predictions.csv", index=False)
summary = fold_table.groupby("model_id", sort=False)[["average_precision", "roc_auc", "recall", "accuracy", "brier"]].agg(["mean", "std"])
summary.columns = ["_".join(c) for c in summary.columns]
summary = summary.reindex(MODEL_IDS)
summary["train_ap_mean"] = pd.DataFrame(training_records).groupby("model_id")["average_precision"].mean()
summary["ap_generalization_gap"] = summary["train_ap_mean"] - summary["average_precision_mean"]
summary["pooled_oof_ap"] = [average_precision_score(y_dev, oof_mean[n]) for n in MODEL_IDS]
summary.to_csv(OUT / "metrics/model_comparison.csv")
print("MODEL_COMPARISON")
display(summary.round(6))

threshold_grid = np.linspace(0.01, 0.99, 99)
thresholds = {}
oof_metrics = {}
for name in MODEL_IDS:
    scores = oof_mean[name]
    f2_values = np.array([fbeta_score(y_dev, scores >= t, beta=2, zero_division=0) for t in threshold_grid])
    best_indices = np.flatnonzero(np.isclose(f2_values, f2_values.max(), rtol=0, atol=1e-12))
    threshold = threshold_grid[best_indices[np.argmin(abs(threshold_grid[best_indices] - 0.5))]]
    thresholds[name] = float(threshold)
    oof_metrics[name] = score_metrics(y_dev, scores, threshold)
    report = classification_report(y_dev, scores >= threshold, labels=[0, 1], target_names=["Benign", "Malignant"], digits=4, zero_division=0)
    print("CLASSIFICATION_REPORT_ID", name, "OOF", "THRESHOLD", round(threshold, 4))
    print(report)
    (OUT / ("metrics/" + name + "_classification_report.txt")).write_text(report, encoding="utf-8")
    pd.DataFrame(classification_report(y_dev, scores >= threshold, labels=[0, 1], target_names=["Benign", "Malignant"], output_dict=True, zero_division=0)).T.to_csv(OUT / ("metrics/" + name + "_classification_report.csv"))
best_component = max([n for n in MODEL_IDS if n not in ["Dummy", "Stacking"]], key=lambda n: summary.loc[n, "average_precision_mean"])
minimum_gain = 0.001
gain = float(summary.loc["Stacking", "average_precision_mean"] - summary.loc[best_component, "average_precision_mean"])
winner = "Stacking" if gain >= minimum_gain else best_component
selection = {"winner": winner, "best_component": best_component, "stacking_fold_mean_ap_gain": gain, "minimum_ap_gain": minimum_gain, "primary_metric": "mean_outer_fold_average_precision", "threshold_objective": "max_pooled_oof_f2", "thresholds": thresholds, "winner_threshold": thresholds[winner], "test_evaluations_planned": 1}
save_json("metrics/selection.json", selection)
save_json("metrics/oof_metrics.json", oof_metrics)
rng = np.random.default_rng(SEED + 20000)
negative_rows, positive_rows = np.flatnonzero(y_dev == 0), np.flatnonzero(y_dev == 1)
differences = []
for _ in range(BOOTSTRAPS):
    sampled = np.concatenate([rng.choice(negative_rows, len(negative_rows), replace=True), rng.choice(positive_rows, len(positive_rows), replace=True)])
    differences.append(average_precision_score(y_dev[sampled], oof_mean["Stacking"][sampled]) - average_precision_score(y_dev[sampled], oof_mean[best_component][sampled]))
paired_delta = {"comparison": "Stacking-minus-" + best_component, "metric": "pooled_oof_average_precision", "point": float(average_precision_score(y_dev, oof_mean["Stacking"]) - average_precision_score(y_dev, oof_mean[best_component])), "ci95": np.quantile(differences, [0.025, 0.975]).tolist(), "bootstrap_n": BOOTSTRAPS, "bootstrap_unit": "row_stratified_conditional_on_fitted_oof_scores", "accounts_for_training_variability": False}
save_json("metrics/paired_bootstrap.json", paired_delta)
print("LOCKED_SELECTION", json.dumps(selection))
print("PAIRED_OOF_AP_DIFFERENCE", json.dumps(paired_delta))

def plot_confusion(name, labels_value, scores, threshold, figure_id):
    matrix = confusion_matrix(labels_value, scores >= threshold, labels=[0, 1])
    colors = np.zeros((2, 2), dtype=int)
    for row in range(2):
        for column in range(2):
            if matrix[row, column] > 0:
                colors[row, column] = 1 if row == column else 2
    fig, ax = plt.subplots(figsize=(3.25, 2.75), layout="constrained")
    ax.imshow(colors, cmap=ListedColormap(["#FFFFFF", "#2F6BFF", "#F28E2B"]), vmin=0, vmax=2)
    for row, column, label in [(0, 0, "TN"), (0, 1, "FP"), (1, 0, "FN"), (1, 1, "TP")]:
        ax.text(column, row, label + "\n" + str(matrix[row, column]), ha="center", va="center", fontsize=12, color="white" if colors[row, column] == 1 else "black")
    ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["Benign", "Malignant"], yticklabels=["Benign", "Malignant"], xlabel="Predicted", ylabel="Actual", title=name + " | t=" + format(threshold, ".2f"))
    finish_figure(fig, figure_id, [name])

for name in MODEL_IDS:
    plot_confusion(name, y_dev, oof_mean[name], thresholds[name], "confusion_" + name)
fig, ax = plt.subplots(figsize=(5.4, 4.0), layout="constrained")
for name, color in zip(MODEL_IDS, PALETTE):
    precision, recall, _ = precision_recall_curve(y_dev, oof_mean[name])
    ax.plot(recall, precision, color=color, label=name + " AP=" + format(average_precision_score(y_dev, oof_mean[name]), ".4f"))
ax.axhline(y_dev.mean(), color="gray", linestyle="--", label="Prevalence=" + format(y_dev.mean(), ".3f"))
ax.set(xlabel="Malignant Recall", ylabel="Malignant Precision", title="OOF Precision-Recall", xlim=(0, 1), ylim=(0, 1.03))
ax.legend(fontsize=7, loc="lower left")
finish_figure(fig, "precision_recall", MODEL_IDS)
fig, ax = plt.subplots(figsize=(5.4, 4.0), layout="constrained")
for name, color in zip(MODEL_IDS, PALETTE):
    fpr, tpr, _ = roc_curve(y_dev, oof_mean[name])
    ax.plot(fpr, tpr, color=color, label=name + " AUC=" + format(roc_auc_score(y_dev, oof_mean[name]), ".4f"))
ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Chance")
ax.set(xlabel="False Positive Rate", ylabel="True Positive Rate", title="OOF ROC", xlim=(0, 1), ylim=(0, 1.03))
ax.legend(fontsize=7, loc="lower right")
finish_figure(fig, "roc", MODEL_IDS)
for metric_id, metric_function, ylabel in [("precision_confidence", precision_score, "Malignant Precision"), ("f1_confidence", f1_score, "Malignant F1"), ("recall_confidence", recall_score, "Malignant Recall")]:
    fig, ax = plt.subplots(figsize=(5.4, 4.0), layout="constrained")
    for name, color in zip(MODEL_IDS, PALETTE):
        curve = [metric_function(y_dev, oof_mean[name] >= t, zero_division=0) for t in threshold_grid]
        ax.plot(threshold_grid, curve, color=color, label=name)
    ax.set(xlabel="Malignant Probability Threshold", ylabel=ylabel, title="OOF " + ylabel + " vs Threshold", xlim=(0, 1), ylim=(0, 1.03))
    ax.legend(fontsize=7, loc="lower left")
    finish_figure(fig, metric_id, MODEL_IDS)
fig, ax = plt.subplots(figsize=(5.4, 4.0), layout="constrained")
for name, color in zip(MODEL_IDS, PALETTE):
    observed, predicted = calibration_curve(y_dev, oof_mean[name], n_bins=6, strategy="quantile")
    ax.plot(predicted, observed, marker="o", markersize=3, color=color, label=name + " Brier=" + format(brier_score_loss(y_dev, oof_mean[name]), ".4f"))
ax.plot([0, 1], [0, 1], color="gray", linestyle="--", label="Ideal")
ax.set(xlabel="Mean Malignant Probability", ylabel="Observed Malignant Fraction", title="OOF Calibration", xlim=(0, 1), ylim=(0, 1.03))
ax.legend(fontsize=7)
finish_figure(fig, "calibration", MODEL_IDS)
probability_correlation = pd.DataFrame({n: oof_mean[n] for n in MODEL_IDS if n != "Dummy"}).corr()
error_indicator = pd.DataFrame({n: (oof_mean[n] >= thresholds[n]) != y_dev for n in MODEL_IDS if n != "Dummy"})
diversity = pd.DataFrame(index=error_indicator.columns, columns=error_indicator.columns, dtype=float)
for left in diversity:
    for right in diversity:
        diversity.loc[left, right] = float(np.mean(error_indicator[left] & error_indicator[right]))
diversity.to_csv(OUT / "metrics/error_overlap.csv")
probability_correlation.to_csv(OUT / "metrics/probability_correlation.csv")
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.9), layout="constrained")
for ax, values, title in [(axes[0], probability_correlation, "Probability Correlation"), (axes[1], diversity, "Joint Error Fraction")]:
    image = ax.imshow(values, cmap="Blues")
    ax.set_xticks(range(len(values)), values.columns, rotation=90, fontsize=7)
    ax.set_yticks(range(len(values)), values.index, fontsize=7)
    ax.set_title(title)
    for row in range(len(values)):
        for column in range(len(values)):
            fraction = (values.iloc[row, column] - values.to_numpy().min()) / max(np.ptp(values.to_numpy()), 1e-12)
            ax.text(column, row, format(values.iloc[row, column], ".2f" if ax is axes[0] else ".3f"), ha="center", va="center", color="white" if fraction > 0.65 else "black", fontsize=6)
finish_figure(fig, "ensemble_diversity", list(diversity.columns))

fitted = {}
for name, estimator in model_set(SEED).items():
    with monitor(name, "development_refit", 0):
        fitted[name] = estimator.fit(X_dev, y_dev)
    joblib.dump(fitted[name], OUT / ("models/" + name + ".joblib"), compress=3)
    if isinstance(fitted[name], Pipeline):
        joblib.dump(fitted[name][:-1], OUT / ("preprocessors/" + name + ".joblib"), compress=3)
for name, estimator in fitted["Stacking"].named_estimators_.items():
    joblib.dump(estimator, OUT / ("models/Stacking_component_" + name + ".joblib"), compress=3)
    joblib.dump(estimator[:-1], OUT / ("preprocessors/Stacking_" + name + ".joblib"), compress=3)
joblib.dump(fitted["Stacking"].final_estimator_, OUT / "models/Stacking_meta.joblib", compress=3)
save_json("preprocessors/schema.json", {"columns": list(features.columns), "classes": {"0": "Benign", "1": "Malignant"}, "positive_label": 1, "winner": winner, "threshold": thresholds[winner]})
save_json("models/ensemble_recipe.json", {"base_ids": [n for n in MODEL_IDS if n not in ["Dummy", "Stacking"]], "meta_model": "StandardScaler_LogisticRegression_C1", "stack_method": "predict_proba", "passthrough": False, "inner_folds": 5})
LOCKED = {"model": winner, "threshold": thresholds[winner], "selection_sha256": hashlib.sha256((OUT / "metrics/selection.json").read_bytes()).hexdigest()}
save_json("metrics/test_lock.json", LOCKED)
y_test = labels.iloc[test].to_numpy()
with monitor(winner, "test_inference", 0):
    test_scores = fitted[winner].predict_proba(X_test)[:, 1]
test_metrics = score_metrics(y_test, test_scores, LOCKED["threshold"])
test_metrics_default = score_metrics(y_test, test_scores, 0.5)
test_report = classification_report(y_test, test_scores >= LOCKED["threshold"], labels=[0, 1], target_names=["Benign", "Malignant"], digits=4, zero_division=0)
print("FINAL_TEST_MODEL", winner)
print("CLASSIFICATION_REPORT_ID", "FinalTest")
print(test_report)
print("FINAL_TEST_METRICS", json.dumps(test_metrics))
(OUT / "metrics/final_test_classification_report.txt").write_text(test_report, encoding="utf-8")
pd.DataFrame({"row_id": row_ids[test], "true_label": y_test, "malignant_probability": test_scores, "prediction": (test_scores >= LOCKED["threshold"]).astype(int), "split": "test"}).to_csv(OUT / "metrics/test_predictions.csv", index=False)
save_json("metrics/test_metrics.json", {"locked_threshold": test_metrics, "default_threshold_secondary": test_metrics_default, "candidate_test_comparison": False, "test_evaluations": 1})
rng = np.random.default_rng(SEED + 30000)
test_negative, test_positive = np.flatnonzero(y_test == 0), np.flatnonzero(y_test == 1)
bootstrap_metrics = {k: [] for k in ["average_precision", "roc_auc", "accuracy", "recall", "specificity", "f1"]}
for _ in range(BOOTSTRAPS):
    sampled = np.concatenate([rng.choice(test_negative, len(test_negative), replace=True), rng.choice(test_positive, len(test_positive), replace=True)])
    values = score_metrics(y_test[sampled], test_scores[sampled], LOCKED["threshold"])
    for key in bootstrap_metrics:
        bootstrap_metrics[key].append(values[key])
test_ci = {key: {"point": test_metrics[key], "ci95": np.clip(np.quantile(values, [0.025, 0.975]), 0, 1).tolist()} for key, values in bootstrap_metrics.items()}
save_json("metrics/test_confidence_intervals.json", {"bootstrap_n": BOOTSTRAPS, "unit": "stratified_test_row", "conditional_on_fitted_model": True, "metrics": test_ci})
print("TEST_CONFIDENCE_INTERVALS", json.dumps(test_ci))
plot_confusion(winner + " Test", y_test, test_scores, LOCKED["threshold"], "final_test_confusion")
meta_weights = fitted["Stacking"].final_estimator_.named_steps["logisticregression"].coef_[0]
pd.DataFrame({"base_id": list(fitted["Stacking"].named_estimators_), "standardized_meta_coefficient": meta_weights}).to_csv(OUT / "metrics/stacking_meta_coefficients.csv", index=False)
fig, ax = plt.subplots(figsize=(4.6, 3.2), layout="constrained")
ax.barh(list(fitted["Stacking"].named_estimators_), meta_weights, color="#0072B2")
ax.set(xlabel="Standardized Meta Coefficient", title="Stacking Meta-Model")
finish_figure(fig, "stacking_meta_coefficients", ["Stacking"])

save_json("logs/resource_samples.json", RESOURCES)
resource_summary = pd.DataFrame([{k: v for k, v in record.items() if k != "samples"} for record in RESOURCES])
resource_summary.to_csv(OUT / "metrics/resource_summary.csv", index=False)
fig, axes = plt.subplots(1, 3, figsize=(8.4, 3.3), layout="constrained")
for name, color in zip(MODEL_IDS, PALETTE):
    record = next(r for r in RESOURCES if r["model_id"] == name and r["phase"] == "development_refit")
    samples = record["samples"]
    axes[0].plot([s["elapsed_seconds"] for s in samples], [s["rss_mb"] for s in samples], color=color, label=name)
    axes[1].plot([s["elapsed_seconds"] for s in samples], [s["cpu_percent"] for s in samples], color=color, label=name)
times = resource_summary.query("phase == 'outer_fit'").groupby("model_id")["wall_seconds"].sum().reindex(MODEL_IDS)
axes[2].barh(MODEL_IDS, times, color=PALETTE)
axes[0].set(title="Refit Process Memory", xlabel="Elapsed Seconds", ylabel="RSS (MiB)")
axes[1].set(title="Refit Process CPU", xlabel="Elapsed Seconds", ylabel="CPU Percent")
axes[1].legend(fontsize=6)
axes[2].set(title="Total Outer Fit Time", xlabel="Seconds")
finish_figure(fig, "resource_profiles", MODEL_IDS)
versions = {"python": sys.version.split()[0], "scikit-learn": sklearn.__version__, "numpy": np.__version__, "pandas": pd.__version__, "matplotlib": matplotlib.__version__, "joblib": joblib.__version__, "psutil": psutil.__version__}
(OUT / "environment/requirements.txt").write_text("\n".join(k + "==" + v for k, v in versions.items() if k != "python") + "\n", encoding="utf-8")
save_json("environment/run_manifest.json", {"run_id": RUN_ID, "seed": SEED, "dataset": data_audit["dataset"], "data_sha256": data_audit["data_sha256"], "split_hash": split_hash, "versions": versions, "os": platform.platform(), "cpu_count": os.cpu_count(), "gpu_requested": False, "internet_requested": False, "figure_dpi": FIGURE_DPI, "model_ids": MODEL_IDS, "figure_ids": [f["id"] for f in FIGURES], "primary_metric": "mean_outer_fold_average_precision", "model_configurations": {name: str(estimator) for name, estimator in model_set(SEED).items()}, "threshold_grid": threshold_grid.tolist(), "bootstrap_n": BOOTSTRAPS})
save_json("metrics/metrics.json", {"run_id": RUN_ID, "task_type": "classification", "model": winner, "dataset": data_audit["dataset"], "split_hash": split_hash, "seed": SEED, "primary_metric": {"name": "average_precision", "split": "nested_repeated_outer_validation", "aggregation": "mean_of_10_folds", "value": float(summary.loc[winner, "average_precision_mean"]), "higher_is_better": True}, "metrics": {"validation_ap_std": float(summary.loc[winner, "average_precision_std"]), "validation_pooled_ap": oof_metrics[winner]["average_precision"], "train_ap_mean": float(summary.loc[winner, "train_ap_mean"]), **{"test_" + k: v for k, v in test_metrics.items()}}, "stacking_fold_mean_ap_gain": gain, "runtime_seconds": time.perf_counter() - START, "resources": {"peak_rss_mb": max(r["peak_rss_mb"] for r in RESOURCES), "gpu": None}, "status": "complete"})

import subprocess

history = IP.history_manager.input_hist_raw[CODE_CELL_START:] if IP is not None else []
if IP is not None:
    assert len(history) == EXPECTED_CODE_CELLS, (len(history), EXPECTED_CODE_CELLS)
    source = "\n\n".join(history) + "\n"
    source_path = OUT / "source/wdbc_stacking.py"
    source_path.write_text(source, encoding="utf-8")
else:
    source = Path(__file__).read_text(encoding="utf-8")
    source_path = OUT / "source/wdbc_stacking.py"
    source_path.write_text(source, encoding="utf-8")

def audit_source(src):
    tokens = list(tokenize.generate_tokens(io.StringIO(src).readline))
    comments = sum(t.type == tokenize.COMMENT for t in tokens)
    triples = sum(t.type == tokenize.STRING and re.sub(r"(?i)^[rubf]*", "", t.string).startswith((chr(34) * 3, chr(39) * 3)) for t in tokens)
    tree = ast.parse(src)
    docstrings = sum(ast.get_docstring(n) is not None for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)))
    strings = sorted(set(n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)))
    narrative_findings = [s for s in strings if len(s.split()) >= 12 and re.search(r"[.!?](?:\s|$)", s)]
    sink_calls = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ["write_text", "write", "writelines"]]
    return {"comments": int(comments), "docstrings": int(docstrings), "triple_quoted_strings": int(triples), "embedded_narrative_strings": len(narrative_findings), "narrative_findings": narrative_findings, "string_inventory": strings, "text_sinks": sink_calls, "syntax_valid": True}

code_audits = [{"cell": i + 1, "sha256": hashlib.sha256(src.encode()).hexdigest(), **audit_source(src)} for i, src in enumerate(history)]
keys = ["comments", "docstrings", "triple_quoted_strings", "embedded_narrative_strings"]
code_totals = {key: sum(r[key] for r in code_audits) for key in keys}
source_audit = audit_source(source)
source_totals = {key: source_audit[key] for key in keys}
assert all(value == 0 for value in [*code_totals.values(), *source_totals.values()]), "SOURCE_AUDIT_FAILED"
save_json("environment/notebook_code_audit.json", {"cells": code_audits, "totals": code_totals})
save_json("environment/python_sources_audit.json", {"files": [{"path": "source/wdbc_stacking.py", "sha256": hashlib.sha256(source.encode()).hexdigest(), **source_audit}], "totals": source_totals})
if history:
    notebook_ast = ast.dump(ast.parse("\n\n".join(history)), include_attributes=False)
    source_ast = ast.dump(ast.parse(source), include_attributes=False)
    assert notebook_ast == source_ast, "SOURCE_RECONSTRUCTION_MISMATCH"
    save_json("environment/source_reconstruction_manifest.json", {"ordered_cells": [{"cell": r["cell"], "sha256": r["sha256"]} for r in code_audits], "separator": "\n\n", "trailing_newline": True, "source_sha256": hashlib.sha256(source.encode()).hexdigest(), "notebook_canonical_ast_sha256": hashlib.sha256(notebook_ast.encode()).hexdigest(), "source_canonical_ast_sha256": hashlib.sha256(source_ast.encode()).hexdigest(), "equivalent": True})
smoke_rows = X_dev.iloc[:3]
reference_scores = fitted[winner].predict_proba(smoke_rows)[:, 1]
smoke_data = OUT / "environment/smoke_input.json"
smoke_data.write_text(smoke_rows.to_json(orient="split"), encoding="utf-8")
smoke_source = "\n".join(["import json", "import sys", "from pathlib import Path", "import joblib", "import pandas as pd", "model = joblib.load(sys.argv[1])", "frame = pd.read_json(Path(sys.argv[2]).read_text(), orient='split')", "scores = model.predict_proba(frame)[:, 1]", "print(json.dumps(scores.tolist()))"]) + "\n"
smoke_audit = audit_source(smoke_source)
assert all(smoke_audit[key] == 0 for key in keys), "SMOKE_SOURCE_AUDIT_FAILED"
smoke_result = subprocess.run([sys.executable, "-c", smoke_source, str(OUT / ("models/" + winner + ".joblib")), str(smoke_data)], check=True, capture_output=True, text=True)
restored_scores = np.array(json.loads(smoke_result.stdout))
assert restored_scores.shape == reference_scores.shape and np.allclose(restored_scores, reference_scores, rtol=0, atol=1e-12), "INFERENCE_SMOKE_FAILED"
smoke_data.unlink()
save_json("environment/inference_smoke_test.json", {"status": "passed", "fresh_process": True, "rows": len(smoke_rows), "max_probability_difference": float(np.max(abs(restored_scores - reference_scores))), "ephemeral_source_audit": smoke_audit})
figure_checks = []
for figure in FIGURES:
    path = OUT / ("figures/" + figure["id"] + ".png")
    with Image.open(path) as picture:
        picture.verify()
    with Image.open(path) as picture:
        figure_checks.append({**figure, "bytes": path.stat().st_size, "dimensions": list(picture.size), "dpi": list(picture.info.get("dpi", [])), "mode": picture.mode, "decodable": True})
save_json("environment/figure_qa.json", {"figures": figure_checks, "visual_status": "pending_control_plane_inspection", "grid_enabled": False})
save_json("environment/source_audit.json", {"notebook_code": code_totals, "python_source": source_totals, "ephemeral_smoke_source": {k: smoke_audit[k] for k in keys}, "string_inventory_review": "pending_control_plane_review"})
print("AUDIT_NOTEBOOK", json.dumps(code_totals))
print("AUDIT_PYTHON_SOURCES", json.dumps(source_totals))
print("INFERENCE_SMOKE_TEST", "passed")
try:
    metrics_record = json.loads((OUT / "metrics/metrics.json").read_text())
    metrics_record["runtime_seconds"] = time.perf_counter() - START
    save_json("metrics/metrics.json", metrics_record)
    manifest = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "checksums.sha256":
            manifest.append(str(path.stat().st_size) + " " + hashlib.sha256(path.read_bytes()).hexdigest() + " " + path.relative_to(OUT).as_posix())
    (OUT / "environment/checksums.sha256").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    zip_path = Path("/kaggle/working/wdbc_stacking_artifacts.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(OUT).as_posix())
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.testzip() is None, "ZIP_CRC_FAILED"
    print("ZIP_PATH", str(zip_path), "ZIP_BYTES", zip_path.stat().st_size)
    print("PRIMARY_VALIDATION_AP", float(summary.loc[winner, "average_precision_mean"]))
finally:
    runtime_output()
