import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.environ.get("DOCKGEN_RESULTS_DIR", os.path.dirname(SCRIPT_DIR))
df = pd.read_csv(f"{RESULTS_DIR}/master_eval_table_n122.csv")

# only rows with BOTH a confidence score AND a ground-truth-labeled RMSD outcome
scored = df[df["status"] == "scored"].copy()
scored["p"] = 1 / (1 + np.exp(-scored["confidence_rank1"]))  # sigmoid(logit) -> P(RMSD<2A)
y = scored["rmsd_le_2A"].astype(int).values
p = scored["p"].values

N_BINS = 10
bin_edges = np.linspace(0, 1, N_BINS + 1)
bin_idx = np.digitize(p, bin_edges[1:-1], right=True)

ece = 0.0
bin_rows = []
for b in range(N_BINS):
    mask = bin_idx == b
    n_b = mask.sum()
    if n_b == 0:
        bin_rows.append((bin_edges[b], bin_edges[b+1], 0, np.nan, np.nan))
        continue
    conf_b = p[mask].mean()
    acc_b = y[mask].mean()
    ece += (n_b / len(p)) * abs(acc_b - conf_b)
    bin_rows.append((bin_edges[b], bin_edges[b+1], n_b, conf_b, acc_b))

bin_df = pd.DataFrame(bin_rows, columns=["bin_lo", "bin_hi", "n", "mean_confidence", "empirical_accuracy"])
bin_df.to_csv(f"{RESULTS_DIR}/ece_reliability_bins_n91.csv", index=False)

print(f"N scored (labeled) = {len(p)}")
print(f"ECE (10-bin, sigmoid(logit) as P(RMSD<2A)) = {ece:.4f}")
print()
print(bin_df.to_string(index=False))

# confidence distribution over all 111 successful-run cases (raw logit + sigmoid), regardless of scorability
ran = df[df["status"] != "runtime_failure"].copy()
ran["p"] = 1 / (1 + np.exp(-ran["confidence_rank1"]))
print()
print("Confidence (raw logit) distribution, N=111 successful runs:")
print(ran["confidence_rank1"].describe())
print()
print("Confidence (sigmoid-transformed), N=111 successful runs:")
print(ran["p"].describe())

# reliability diagram
fig, ax = plt.subplots(figsize=(5, 5))
valid = bin_df.dropna()
bin_centers = (valid["bin_lo"] + valid["bin_hi"]) / 2
ax.bar(bin_centers, valid["empirical_accuracy"], width=0.08, edgecolor="black", alpha=0.7, label="empirical accuracy")
ax.plot([0, 1], [0, 1], "k--", label="perfect calibration")
ax.set_xlabel("Mean predicted confidence (sigmoid(logit))")
ax.set_ylabel("Empirical accuracy (RMSD < 2A)")
ax.set_title(f"DockGen-E DiffDock-L reliability diagram (n={len(p)} scored, ECE={ece:.3f})")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.legend()
fig.tight_layout()
fig.savefig(f"{RESULTS_DIR}/reliability_diagram_n91.png", dpi=150)
print()
print("saved reliability diagram to", f"{RESULTS_DIR}/reliability_diagram_n91.png")
print("saved bin csv to", f"{RESULTS_DIR}/ece_reliability_bins_n91.csv")
