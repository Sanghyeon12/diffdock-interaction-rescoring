import os, glob, sys
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

import MDAnalysis as mda
import prolif as plf
from rdkit import Chem

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.environ.get("DOCKGEN_RESULTS_DIR", os.path.dirname(SCRIPT_DIR))
GT_DIR = os.environ.get("DOCKGEN_GT_DIR", os.path.join(RESULTS_DIR, "dockgen_set"))

master = pd.read_csv(f"{RESULTS_DIR}/master_eval_table_n122.csv")
scored = master[master["status"] == "scored"].copy()

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else len(scored)
scored = scored.head(LIMIT)

fp = plf.Fingerprint()

rows = []
for _, row in scored.iterrows():
    cid = row["complex_id"]
    rd = row["result_dir"]
    protein_pdb = f"{GT_DIR}/{cid}/{cid}_protein_processed.pdb"
    true_ligand_pdb = f"{GT_DIR}/{cid}/{cid}_ligand.pdb"
    pred_sdf = glob.glob(f"{RESULTS_DIR}/{rd}/rank1_confidence*.sdf")
    if not pred_sdf or not os.path.exists(protein_pdb) or not os.path.exists(true_ligand_pdb):
        rows.append({"complex_id": cid, "plif_status": "missing_input_files", "n_true_interactions": None, "n_recovered": None, "recovery": None})
        continue
    pred_sdf = pred_sdf[0]
    try:
        protein_u = mda.Universe(protein_pdb)
        protein_mol = plf.Molecule.from_mda(protein_u, NoImplicit=False)

        true_rd = Chem.MolFromPDBFile(true_ligand_pdb, sanitize=True, removeHs=False)
        if true_rd is None:
            rows.append({"complex_id": cid, "plif_status": "true_ligand_rdkit_load_failed", "n_true_interactions": None, "n_recovered": None, "recovery": None})
            continue
        true_mol = plf.Molecule.from_rdkit(true_rd)

        pred_supplier = Chem.SDMolSupplier(pred_sdf, sanitize=True, removeHs=False)
        pred_rd = pred_supplier[0]
        if pred_rd is None:
            rows.append({"complex_id": cid, "plif_status": "pred_ligand_rdkit_load_failed", "n_true_interactions": None, "n_recovered": None, "recovery": None})
            continue
        pred_mol = plf.Molecule.from_rdkit(pred_rd)

        true_ifp = fp.generate(true_mol, protein_mol, metadata=False)
        pred_ifp = fp.generate(pred_mol, protein_mol, metadata=False)

        # true_ifp / pred_ifp: dict-like {(ligand_resid, protein_resid): {interaction: bool/count}}
        def flatten(ifp):
            s = set()
            for key, interactions in ifp.items():
                _, presid = key
                for interaction_name in interactions:
                    s.add((str(presid), interaction_name))
            return s

        true_set = flatten(true_ifp)
        pred_set = flatten(pred_ifp)
        n_true = len(true_set)
        n_recovered = len(true_set & pred_set)
        recovery = (n_recovered / n_true) if n_true > 0 else None

        rows.append({
            "complex_id": cid, "plif_status": "ok",
            "n_true_interactions": n_true, "n_recovered": n_recovered,
            "n_predicted_interactions": len(pred_set),
            "recovery": recovery,
        })
    except Exception as e:
        rows.append({"complex_id": cid, "plif_status": f"error: {type(e).__name__}: {e}"[:200], "n_true_interactions": None, "n_recovered": None, "recovery": None})

out = pd.DataFrame(rows)
out.to_csv(f"{RESULTS_DIR}/plif_recovery_results.csv", index=False)
print(out["plif_status"].value_counts())
print()
ok = out[out["plif_status"] == "ok"]
print(f"PLIF computed OK for {len(ok)}/{len(scored)}")
if len(ok):
    print("mean recovery (per-complex):", ok["recovery"].mean())
    print("median recovery:", ok["recovery"].median())
    total_true = ok["n_true_interactions"].sum()
    total_recovered = ok["n_recovered"].sum()
    print(f"pooled recovery = {total_recovered}/{total_true} = {total_recovered/total_true if total_true else float('nan')}")
print("saved:", f"{RESULTS_DIR}/plif_recovery_results.csv")
