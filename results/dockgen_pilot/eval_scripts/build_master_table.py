import os, re, glob
import pandas as pd

ROOT = "/home/jacks.local/sjun/docking_project/PoseBench"
RESULTS_DIR = f"{ROOT}/forks/DiffDock/results/dockgen_pilot"
INPUT_CSV = f"{ROOT}/forks/DiffDock/inference/diffdock_dockgen_inputs.csv"
BUST_CSV = f"{RESULTS_DIR}/bust_results.csv"

ids_122 = pd.read_csv(INPUT_CSV)["complex_name"].tolist()
assert len(ids_122) == 122 and len(set(ids_122)) == 122

bust = pd.read_csv(BUST_CSV)
bust_by_mol = bust.set_index("mol_id")

# map each of the 122 canonical ids to its actual result-dir name (handles the 13 truncated-name dirs)
result_dirs = set(os.listdir(RESULTS_DIR))
def find_result_dir(cid):
    if cid in result_dirs:
        return cid
    # truncated-name fallback: strip trailing _<digits>
    m = re.match(r"^(.*)_(\d+)$", cid)
    if m and m.group(1) in result_dirs:
        return m.group(1)
    return None

rows = []
for cid in ids_122:
    rd = find_result_dir(cid)
    has_output = rd is not None and len(os.listdir(os.path.join(RESULTS_DIR, rd))) > 0
    rmsd = None
    rmsd_le_2a = False
    confidence = None
    status = None
    if not has_output:
        status = "runtime_failure"
    else:
        rank1_files = glob.glob(os.path.join(RESULTS_DIR, rd, "rank1_confidence*.sdf"))
        if rank1_files:
            m = re.search(r"rank1_confidence(-?[\d.]+)\.sdf", os.path.basename(rank1_files[0]))
            if m:
                confidence = float(m.group(1))
            else:
                print("NO CONFIDENCE MATCH:", rank1_files[0])
        else:
            print("NO RANK1_CONFIDENCE FILE for", rd, os.listdir(os.path.join(RESULTS_DIR, rd)))
        if cid in bust_by_mol.index:
            status = "scored"
            rmsd = float(bust_by_mol.loc[cid, "rmsd"])
            rmsd_le_2a = bool(bust_by_mol.loc[cid, "rmsd_≤_2å"])
        else:
            status = "unscored_parsing_issue"
    rows.append({
        "complex_id": cid,
        "result_dir": rd,
        "status": status,
        "confidence_rank1": confidence,
        "rmsd": rmsd,
        "rmsd_le_2A": rmsd_le_2a,
    })

df = pd.DataFrame(rows)
out_path = f"{RESULTS_DIR}/master_eval_table_n122.csv"
df.to_csv(out_path, index=False)

print("status counts:")
print(df["status"].value_counts())
print()
print("success_count (rmsd<2A):", df["rmsd_le_2A"].sum())
print("success_rate /122:", df["rmsd_le_2A"].sum() / 122)
print("success_rate /111 (successful runs only):", df["rmsd_le_2A"].sum() / (df["status"] != "runtime_failure").sum())
print("success_rate /91 (scored only):", df["rmsd_le_2A"].sum() / (df["status"] == "scored").sum())
print()
print("confidence extracted for N of 111:", df["confidence_rank1"].notna().sum())
print("saved to:", out_path)
