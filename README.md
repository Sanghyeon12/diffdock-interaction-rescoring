# diffdock-interaction-rescoring

Interaction-aware confidence rescoring for DiffDock-L pose predictions, evaluated on DockGen-E.

## Status

Pilot evaluation complete on DockGen-E (122 complexes). Rescoring stage (Phase 2) not yet run.

## Results (n=122, PoseBench pipeline, DiffDock-L)

| Metric | Value | Notes |
|---|---|---|
| RMSD < 2A success rate | 14/122 = 11.48% | denominator fixed at 122; runtime crashes counted as failures |
| ECE | 0.203 | computed on 91 scored complexes |
| PLIF recovery | 15.47% | pooled 138/892, highly skewed distribution |

Denominator methodology: failed/crashed complexes are kept in the denominator and counted as
non-success, following PocketVina (arXiv:2506.20043) convention for DockGen-full evaluation.

Of the 122 complexes: 91 scored (RMSD computable), 20 produced poses but RMSD unscorable
(ligand parsing failures - dipeptides, metal ions), 11 crashed at runtime (reproducible across
3 independent retries - traced to a group-aggregation bug in PoseBench's fork of DiffDock's
`inference.py`, not an upstream DiffDock bug).

## Structure

```
results/dockgen_pilot/
  <complex_id>/           per-complex DiffDock-L pose outputs
  eval_scripts/           RMSD/ECE/PLIF computation scripts
  master_eval_table_n122_with_plif.csv   main results table
  bust_results.csv        PoseBusters validity checks
  ece_reliability_bins_n91.csv + reliability_diagram_n91.png
  plif_recovery_results.csv
```

## Pipeline

DiffDock-L inference and evaluation run via [BioinfoMachineLearning/PoseBench](https://github.com/BioinfoMachineLearning/PoseBench)
(`main`, tag v1.1.0-1-gc5d728d) on SDSU's Innovator HPC cluster. DockGen-E benchmark from
[DockGen (Corso et al.)](https://arxiv.org/abs/2402.18396).

## Reproduction

See `results/dockgen_pilot/eval_scripts/` (`build_master_table.py`, `compute_ece.py`,
`compute_plif.py`).
