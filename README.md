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
(ligand parsing failures - dipeptides, metal ions), 11 crashed at runtime. Root cause of the
11 crashes: 7 SVD/Kabsch numerical instability (`torch.linalg.svd` ill-conditioned, upstream
DiffDock issue) + 4 RDKit conformer / exception-handling code bugs — reproducible across 3
independent retries. (Note: an earlier version of this README attributed these 11 crashes to a
group-aggregation bug in PoseBench's fork of `inference.py`; that group-aggregation bug is real
but affects a *different*, already-resolved issue — 13 result directories with truncated names,
fixed via symlinks — not these 11 crashes. Corrected 2026-07-20, see `paper/paper-draft-v1.md`
§4.3/§4.6(f) for the full trace.)

## Structure

```
paper/                    paper draft (Intro/Related Work/Method/Experiments)
environment/              conda environment exports (diffdock, dockeval)
results/dockgen_pilot/
  <complex_id>/                           per-complex DiffDock-L pose outputs
  eval_scripts/                           RMSD/ECE/PLIF computation scripts
  diffdock_dockgen_inputs.csv             the 122 canonical complex IDs (input manifest)
  master_eval_table_n122_with_plif.csv    main results table
  bust_results.csv                        PoseBusters validity checks
  ece_reliability_bins_n91.csv + reliability_diagram_n91.png
  plif_recovery_results.csv
```

## Pipeline

DiffDock-L inference and evaluation run via [BioinfoMachineLearning/PoseBench](https://github.com/BioinfoMachineLearning/PoseBench)
(`main`, tag v1.1.0-1-gc5d728d) on SDSU's Innovator HPC cluster. DockGen-E benchmark from
[DockGen (Corso et al.)](https://arxiv.org/abs/2402.18396). Sampling parameters used the
repo's default `default_inference_args.yaml` (e.g. `sigma_schedule: expbeta`,
`initial_noise_std_proportion: 1.46`); the exact `python -m inference` CLI invocation (job
submission script) was not preserved separately from the HPC job logs.

**End-to-end flow** (HPC run → local repo → paper):

1. Submit/monitor GPU inference jobs on Innovator (`srun`/`sbatch`, PoseBench's `forks/DiffDock`).
2. Pull results to this repo: `scp -r` the per-complex output directories, the input manifest
   (`diffdock_dockgen_inputs.csv`), and `eval_scripts/*.py` outputs (`master_eval_table_*.csv`,
   `bust_results.csv`, `ece_reliability_bins_*.csv`, `plif_recovery_results.csv`) into
   `results/dockgen_pilot/`.
3. Re-run `eval_scripts/` locally if needed (see Reproduction below) to regenerate tables/plots
   from the raw per-complex outputs, or trust the pulled CSVs directly.
4. Update `paper/paper-draft-v1.md` with any new/changed numbers; keep Results table above in
   sync.
5. `git add`, commit, push.

## Reproduction

`results/dockgen_pilot/eval_scripts/` (`build_master_table.py`, `compute_ece.py`,
`compute_plif.py`) default to reading/writing relative to their own location (i.e. this
repo's `results/dockgen_pilot/`), so they run as-is against the per-complex output
directories and `diffdock_dockgen_inputs.csv` already in this repo. Override with the
`DOCKGEN_RESULTS_DIR` / `DOCKGEN_INPUT_CSV` / `DOCKGEN_GT_DIR` environment variables to point
at a different results tree or ground-truth directory.

`compute_plif.py` additionally needs the DockGen-E ground-truth structures
(`<complex_id>_protein_processed.pdb`, `<complex_id>_ligand.pdb`), which are **not** included
in this repo (~2.5GB on the HPC cluster, `PoseBench/data/dockgen_set/`) — obtain them by
running PoseBench's own DockGen-E data-preparation step, then point `DOCKGEN_GT_DIR` at the
resulting directory.

`environment/*.environment.yml` are `conda env export` snapshots of the two conda
environments used (`diffdock`, `dockeval`); recreate with
`conda env create -f environment/diffdock.environment.yml`.
