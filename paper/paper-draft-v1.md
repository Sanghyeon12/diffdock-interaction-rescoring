---
type: thesis
status: draft
created: 2026-07-20
updated: 2026-07-21
tags: [thesis, manuscript, calibration, rescoring, plif, dockgen-e]
---

# Manuscript Draft v1 — Interaction-Aware Rescoring for DiffDock-L under Cross-Docking Distribution Shift

> Draft status note (2026-07-20): this is a from-scratch rewrite, not a restoration of the
> earlier `paper-draft-v1.md` (deleted at user request in a prior session). Source material:
> [[team-report-2026-07-16]] (lit review, experiment design, and an earlier full-draft version
> of Introduction–Experiments), [[phase2-rescoring-design-2026-07-19]] (the current, more
> concrete Phase 2 protocol), and the measured Phase 1 results confirmed in [[log]] and [[hot]]
> (2026-07-19). All numbers below are traceable to
> `results/dockgen_pilot/master_eval_table_n122_with_plif.csv` and the accompanying
> `eval_scripts/` in the `diffdock-interaction-rescoring` repository. **Phase 2 (the rescoring
> model itself) has not been executed** — every Phase 2 number in this draft is a design
> specification or a hypothesis, never a result, and is labeled as such throughout.
>
> Target venue (per [[team-report-2026-07-16]] §5.2, unchanged): ICML workshop track, 4–6 pages.
> This draft is longer than that budget and will need trimming (mainly Related Work) once
> Phase 2 results exist and the two phases are confirmed to share one submission.

---

> **ERRATUM (2026-07-21): the PLIF interaction-recovery rate and the confidence-vs-PLIF-recovery
> correlation originally reported in this draft (pooled recovery 15.47%, 138/892, n=80; Spearman
> rho = -0.149, n=78) are INVALIDATED. Do not cite these two numbers.** A code audit
> (cross-checking `eval_scripts/compute_plif.py` — this project's "V1" PLIF pipeline — against
> `diffdock_dockgen_inputs.csv`) found that V1 scores every predicted ligand pose's interaction
> fingerprint against the **crystal protein file** (`protein_processed.pdb`) rather than the
> **ESMFold-predicted protein file DiffDock-L actually docked into**
> (`holo_aligned_predicted_protein.pdb`). Every complex's PLIF fingerprint was therefore computed
> in a structural context DiffDock-L never used, which invalidates the resulting numbers
> regardless of how correctly the downstream pooling and correlation arithmetic were done. Every
> occurrence of the retracted numbers below is marked **[INVALIDATED — see §4.4a]** and left in
> place rather than deleted, to keep an honest record of what was measured and later retracted.
> **Not affected:** top-1 RMSD < 2 Å success (14/122 = 11.48%) and ECE (0.203) — these come from a
> separate computation path (`build_master_table.py`, `compute_ece.py`) that does not depend on
> which protein file PLIF scoring used.
>
> **Update (2026-07-21, hybrid recomputation complete): the manuscript now has a valid replacement
> PLIF recovery number.** A hybrid pipeline combining V2's correct protein-file handling (scoring
> against the ESMFold-predicted protein DiffDock-L actually docked into) with V1's non-redundant
> 9-type ProLIF interaction list was run over the matched n=82 subset of DockGen-E. Rank-1
> (confidence-selected) pooled PLIF interaction recovery is **47/509 = 9.23%** (per-complex mean
> 8.82%, median 0%); the rank1–10 oracle (best of the 10 retained candidates per complex) is
> **64/509 = 12.57%** (per-complex mean 11.86%, median 0%), an oracle headroom of **+3.34
> percentage points pooled (+3.05 points per-complex mean)**. One complex (`2wwc_1_CHT_2`) has zero
> true interactions under this 9-type list, so its per-complex recovery is undefined (NaN); it
> contributes 0/0 to the pooled figures and is excluded from the mean/median (n=81 non-null). These
> two numbers (9.23% baseline, 12.57% oracle) are this draft's reported PLIF recovery figures,
> replacing the retracted 15.47%. Source: `hybrid_plif_baseline_matched82.csv` and
> `hybrid_plif_oracle_matched82.csv` (scripts `hybrid_plif_baseline.py`, `hybrid_plif_oracle.py`),
> under `results/dockgen_pilot_eval/` on the project's HPC environment. The confidence-vs-PLIF-
> recovery correlation against these hybrid values was still unmeasured at this point in the
> project — see the next update below, which reports it. An interaction between the two
> oracle-headroom results (RMSD: +6.56 points; PLIF: +3.34 points) also now informs the Phase 2
> framing — see §3.2 and §4.5. Full detail in §4.4a.
>
> **Update (2026-07-21, confidence-vs-PLIF-recovery correlation now computed): no significant
> relationship found.** All 82 hybrid baseline rows matched a `confidence_rank1` value; the one
> complex with zero true interactions and undefined recovery (`2wwc_1_CHT_2`) was excluded, leaving
> n=81. Spearman rho = 0.046167845505, two-sided p = 0.682340974058; an independent average-rank
> Pearson calculation reproduced the same rho exactly. **The previous V1-derived rho = -0.149
> remains INVALIDATED and was not reused.** As with that earlier, now-retracted result, we read
> this only as a limited, non-causal statement: no statistically significant monotonic relationship
> between DiffDock-L's confidence score and this corrected PLIF-recovery rate was observed in this
> sample. Source: `eval_scripts/correlate_hybrid_plif.py`,
> `results/dockgen_pilot_eval/hybrid_plif_confidence_spearman.json`. Full detail in §4.4a.

---

> **ERRATUM (2026-07-23/24): the 1,500-complex PDBBind subset drawn for M1/M1-abl training data
> (§3.2, §4.6(j)/(k)) is INVALIDATED as a training-data source — do not train M1 on it.**
> Independent verification found that all 1,500 sampled complexes are contained in DiffDock-L's
> own training split (`timesplit_no_lig_overlap_train`, 16,379 IDs) — the same split DiffDock-L's
> score and confidence networks were fit on. Every number computed from this subset so far (the
> feature-extraction success rate and the two successive GPU-inference-completion counts,
> 1,440/1,500 = 96.0% and, after a later dedup-bug fix, 1,397/1,500 = 93.1%; §3.2, §4.6(j)) is
> therefore not usable as training data for M1: poses and confidence scores sampled for structures
> DiffDock-L has already seen in training are not representative of its behavior on unseen
> complexes, which is the same memorization concern this manuscript's own Related Work section
> (§2, citing PoseBench's accuracy/training-similarity correlation) raises against DiffDock-L's
> raw accuracy claims elsewhere. No M1/M1-abl training or evaluation was ever run on this subset —
> only data preparation reached completion — so no reported accuracy number is affected; only the
> training-data preparation narrative in §3.2 and §4.6(j)/(k) is invalidated. **Superseded plan:**
> M1/M1-abl training data will instead be drawn from DiffDock-L's own held-out validation split
> (`timesplit_val_filter`, 585 complexes, confirmed not used in DiffDock-L training); DiffDock-L's
> test split (363 complexes) is reserved for a possible future, separate evaluation of M1 itself
> rather than reused as training data. GPU docking of the 585-complex validation split was in
> progress, not complete, as of this draft. The §3.2/§4.6(j)/(k) prose below is left in place
> rather than deleted, per this project's practice of recording invalidated work rather than
> erasing it, and should be read as a record of the abandoned 1,500-complex approach, not as a
> description of M1's actual training data.

---

## Abstract

DiffDock-L selects its output pose using a learned confidence score trained to predict whether
a sampled pose falls within 2 Å RMSD of the native structure. This score has been validated
only as a ranking signal on in-distribution (PDBBind) data; no published study has measured its
formal calibration under cross-docking distribution shift, and no study has measured whether it
predicts recovery of the specific protein–ligand interactions (hydrogen bonds, halogen bonds,
π-stacking) that determine whether a pose is chemically, not just geometrically, correct. We
run DiffDock-L on all 122 complexes of the DockGen-E cross-docking benchmark and evaluate the
raw confidence score directly. Of 122 complexes, 91 produced RMSD-scorable poses; on this
subset, top-1 RMSD < 2 Å success is 14/122 (11.48%, denominator fixed at 122 with runtime
failures counted as non-success) and expected calibration error (ECE) is 0.203. An earlier
reported pooled PLIF interaction recovery of 15.47% (138/892, n=80) and its confidence-vs-PLIF-
recovery rank correlation (Spearman rho = -0.149, n=78) **were computed against the wrong
(crystal, not ESMFold-predicted) protein file and are INVALIDATED [see §4.4a].** A hybrid
recomputation using the correct protein file and a non-redundant 9-type interaction list gives a
valid replacement: pooled PLIF interaction recovery of the confidence-selected rank-1 pose is
**9.23%** (47/509, matched n=82), against a rank1–10 oracle upper bound of **12.57%** (64/509) —
an oracle headroom of +3.34 percentage points. A recomputed Spearman correlation between
confidence and this corrected PLIF-recovery rate finds no statistically significant monotonic
relationship (rho = 0.046, two-sided p = 0.682, n=81); the previous, now-invalidated rho = -0.149
was not reused. Taken together, the valid results show low top-1 RMSD success, poor calibration,
and low PLIF recovery with only modest room to improve it by reranking alone, and no statistically
significant relationship (at this sample size) between confidence and this chemical-correctness
signal. An oracle-headroom analysis of
DiffDock-L's already-sampled candidate pool helps explain why the two correctness criteria give
such different pictures. RMSD headroom is substantial (14/122 to 22/122, +6.56 percentage points):
a better-RMSD pose is often already sitting in the candidate pool, and confidence simply is not
picking it, a selection problem reranking could fix. PLIF headroom is small (+3.34 points): the
candidate pool rarely contains a chemically much better alternative in the first place, so no
amount of reranking recovers much there (§4.5). Building on this diagnosis, we describe (design
only; not yet executed) an Interaction-Aware Rescoring model that reranks DiffDock-L's
already-sampled candidate poses using complex-invariant ProLIF interaction-type counts,
pharmacophore geometry, and ensemble consistency, trained on PDBBind and evaluated without
retraining any part of DiffDock-L, on the same 122-complex cross-docking set. The RMSD-side
headroom alone is our justification for building this model; we do not claim it will meaningfully
improve PLIF-based chemical correctness, and treat any PLIF-recovery gain it shows as a secondary,
exploratory finding rather than a headline result. We report the measured diagnosis in full and
the correction as a pre-registered protocol, including a mandatory oracle-headroom gate that must
pass before the rescoring model is trained at all.

---

## 1. Introduction

Diffusion-based generative models have reframed blind molecular docking from a regression
problem into a sampling problem over a product manifold of ligand translation, rotation, and
torsion angles. DiffDock, and its larger successor DiffDock-L, pair this generative sampler with
a separately trained confidence model that predicts whether a sampled pose satisfies the
conventional 2 Å RMSD success criterion. In practice this confidence score has become the
default mechanism for pose selection: DiffDock-L returns the pose its confidence model ranks
first, and downstream virtual-screening pipelines use the same score to triage predictions. That
use rests on two assumptions that, to our knowledge, no published study has tested directly:
first, that the confidence estimate stays informative when the model is applied outside the
distribution it was trained on; second, that RMSD-based correctness — the only target the
confidence model was ever trained to predict — is itself a sufficient proxy for the properties a
downstream user actually cares about, such as whether a pose reproduces the key hydrogen bonds
and other contacts that determine binding.

Two bodies of evidence expose the first assumption as untested. DiffDock's confidence score has
been validated as a ranking quantity — via Spearman rank correlation with RMSD and via
selective-prediction accuracy gains — exclusively on in-distribution PDBBind time-splits.
Separately, a growing set of cross-docking and out-of-distribution benchmarks documents that
DiffDock-L's raw pose accuracy is highly protocol-dependent, with reported top-1 success rates
ranging from roughly 5% to 55% depending on dataset, sampling budget, and self- vs. cross-docking
setup. No source in either body of evidence connects the two: nobody has measured whether the
confidence score degrades in a calibrated, predictable way as accuracy collapses under
distribution shift, or whether it instead stays silently overconfident. A third, independent line
of work exposes the second assumption. Errington et al. (arXiv:2409.20227) show that RMSD-based
pose correctness carries no measured relationship to whether a pose reproduces the reference
protein–ligand interaction fingerprint (PLIF) — yet no study we are aware of feeds that
chemically orthogonal signal back into a docking model's own pose-selection mechanism.

This project addresses both gaps with a diagnose-then-correct structure. Phase 1 measures the
calibration of DiffDock-L's raw confidence score under cross-docking shift, using the DockGen-E
benchmark (122 complexes with pockets dissimilar to PDBBind), and reports — for the first time on
this benchmark — PLIF interaction recovery alongside RMSD-based top-1 accuracy. An earlier reported
version of the PLIF recovery rate (15.47%) and a test of whether confidence tracks it (Spearman rho
= -0.149, n=78, t(76) = -1.31) **[INVALIDATED — see §4.4a]: both were computed by a pipeline that
scored the predicted ligand against the wrong (crystal, not ESMFold-predicted) protein file.** A
hybrid recomputation against the correct protein file now gives a valid pooled PLIF recovery rate
for the confidence-selected pose of 9.23% (47/509, matched n=82), against a rank1–10 oracle upper
bound of 12.57% (64/509); a recomputed correlation between confidence and this corrected recovery
rate finds no statistically significant monotonic relationship (Spearman rho = 0.046, two-sided
p = 0.682, n=81). The RMSD-based Phase 1 measurements remain complete and valid and
are the primary reported result of this draft: on the 91 of 122 complexes with RMSD-scorable
output, top-1 RMSD < 2 Å success is 11.48% (14/122) and ECE is 0.203.
Phase 2, building on that diagnosis,
proposes an Interaction-Aware Rescoring model that reranks DiffDock-L's already-sampled candidate
poses using PLIF-derived and pharmacophore features rather than confidence alone. **Phase 2's
mandatory pre-registered oracle-headroom gate (Step 0) has now been run** on the retained
rank1–10 candidate pool: the RMSD gate clears the pre-registered +5-percentage-point bar (14/122 to
22/122, +6.56 points), while the PLIF gate does not (9.23% to 12.57%, +3.34 points). We read this
as two different diagnoses, not a contradiction — the RMSD headroom indicates a *selection*
failure that reranking can address, while the small PLIF headroom indicates a *sampling*
limitation that reranking cannot — and we proceed to build and evaluate the rescoring model on
RMSD-selection grounds alone, without claiming that it will materially improve PLIF-based chemical
correctness (§3.2, §4.5). We report the Phase 1 diagnosis and the Phase 2 gate outcome as measured
results and the Phase 2 model itself as a specified, not-yet-run protocol, and we are explicit
throughout about which numbers are measurements and which are targets.

Contributions: (i) the first reported calibration analysis (ECE) of DiffDock-L's raw confidence
score on a leakage-controlled cross-docking benchmark (DockGen-E, n=122), including an honest
accounting of a substantial fraction of complexes (31/122) for which the pipeline produces no
scorable output at all — plus a PLIF interaction-recovery rate (9.23% rank-1, 12.57% oracle, after
a hybrid recomputation correcting an earlier protein-file bug, §4.4a) and its recomputed
correlation with confidence (Spearman rho = 0.046, two-sided p = 0.682, n=81 — no statistically
significant monotonic relationship, §4.4a) — **an earlier version of both numbers (15.47% recovery,
rho = -0.149 correlation) [INVALIDATED — see §4.4a] was computed against the wrong (crystal, not
ESMFold-predicted) protein file and has been superseded by the hybrid recomputation above**;
(ii) a mandatory pre-registered oracle-headroom gate, now executed, showing that the RMSD-based
candidate pool has meaningful headroom (+6.56 points) while the PLIF-based pool does not
(+3.34 points) — used here to justify Phase 2 on RMSD-selection grounds while explicitly not
claiming a PLIF-correctness improvement — together with two executed non-learned reranking
comparators (B1 random, B3 classical affinity) that all cluster within an 11.12–12.30% band
indistinguishable from raw confidence (§3.2, §4.5), plus a fully specified, not-yet-executed
Interaction-Aware Rescoring protocol that reranks DiffDock-L's existing candidate poses using
complex-invariant interaction and pharmacophore features; and (iii) an explicit statement of what
remains unmeasured — stratified (pocket-similarity) calibration, an in-distribution ECE anchor,
and every Phase 2 learned-model (M1/M1-abl) accuracy number — so that this draft does not overstate
what has actually been shown.

---

## 2. Related Work

**Diffusion docking and its confidence model.** DiffDock (Corso et al., ICLR 2023) recast blind
docking as generative sampling over translation, rotation, and torsion, pairing an SE(3)-
equivariant score network with a separately trained confidence model that predicts whether a
pose meets the 2 Å RMSD criterion. On in-distribution PDBBind time-splits this confidence score
attains Spearman correlation 0.68 with RMSD and lifts selective accuracy from 38% to 83% under
aggressive abstention. The same source paper (Corso et al., arXiv:2402.18396, which also introduced
DockGen) shows that Confidence Bootstrapping applied to **DiffDock-S** (not DiffDock-L) raises
DockGen-clusters accuracy from **9.8% to 24.0%** (Table 1, Fig. 4-D). This claim was independently
verified against the arXiv:2402.18396 source PDF (PMC10925391) on 2026-07-22; the earlier draft
had misattributed the improved model as DiffDock-L and misreported the figures as roughly 7% to
23%, both now corrected.
DiffDock-PP (Ketata et al., ICLR 2023 workshop, arXiv:2304.03889) extends the same
top-1-plus-confidence paradigm to protein–protein docking and reports a large gap between
oracle-selected and confidence-selected poses. In every case we are aware of, the confidence
estimate is validated as a ranking or selective-prediction signal, never through a formal
calibration metric such as ECE, and never re-examined once a richer feature set — interaction
fingerprints, pharmacophores — is available at inference time.

**Cross-docking and out-of-distribution generalization.** A second line of work documents the
fragility of deep-learning docking under distribution shift but measures pose accuracy, not
confidence. PoseX (Jiang et al., ICLR 2026, arXiv:2505.01700), a leakage-controlled self- and
cross-docking benchmark, reports a negative correlation (r ≈ −0.50) between DiffDock-L's pocket
similarity to training data and its pose RMSD, but evaluates only top-1 RMSD and does not assess
the confidence score itself. FlowDock (Morehead & Cheng, arXiv:2412.10966) reports DiffDock-L
accuracy collapsing to 4.8% on DockGen-E under its own evaluation protocol. A comparative study
on SARS-CoV-2 and MERS-CoV main proteases (Liu et al., J. Chem. Inf. Model. 2026) finds vanilla
DiffDock confidence-selected top-1 accuracy of 12.3%, below classical Glide, on novel viral
protease targets. A large-scale LIT-PCBA virtual-screening evaluation (Abo-Dahab et al., UCSF
capstone 2026, arXiv:2605.01681) finds DiffDock confidence performing at or below classical AutoDock in a
single-pose screening setting. PoseBench (Morehead et al., Nature Machine Intelligence 8, 32–41,
2026) ties these degradations to a mechanism, reporting a strong negative correlation between
deep-learning accuracy and training-set similarity — consistent with memorization — that is
absent for classical, non-learned docking. Reported DiffDock-L success rates therefore vary by
roughly an order of magnitude (≈5–55%) with benchmark protocol; any calibration or rescoring
result must fix and report its exact protocol to be comparable to prior numbers at all, and we do
so in §4.

**Calibration, confidence, and interaction recovery in adjacent settings.** Formal calibration
analysis exists in this literature mainly for co-folding models, not pose-sampling docking
models. AlphaFold3 (Abramson et al., Nature 630, 493–500, 2024) reports the only
reliability-diagram-style analysis we found in this corpus, and it varies sharply by interaction
category — a caution against treating a single aggregate calibration number as representative.
ACER (ICML 2026 workshop submission) reports that co-folding confidence correlates weakly with
success on out-of-distribution and allosteric targets. An agentic LLM-based pose reranker
(Khiari et al., 2026) finds self-reported verbalized confidence inversely correlated with
accuracy in its small evaluation. Most directly motivating this work, Errington et al.
(arXiv:2409.20227) show that RMSD-based pose correctness — the exact target DiffDock-L's
confidence model is trained on — carries no measured relationship to whether a pose reproduces
the reference protein–ligand interactions computed via ProLIF. We are not aware of prior work
that closes this loop by feeding interaction-fingerprint or pharmacophore information back into a
trained reranking mechanism for diffusion-docking poses; existing pose-rescoring work — GNINA's
CNN scoring (Buccheri & Rescifina, Molecules 2025), MC-GNNAS-Dock's multi-criteria selection
(Cao et al., arXiv:2509.26377) — reranks with classical or graph-based scoring functions, not by
augmenting a diffusion model's own learned confidence output with chemically orthogonal features.
The closest adjacent precedent we found is DiffDock-NMDN (Xia, Gu & Zhang, *J. Chem. Inf. Model.*
65(3), 1101–1114, 2025), which does rerank DiffDock's sampled poses with a separately trained
model, but that model (NMDN) learns a continuous protein-residue–ligand-atom distance-likelihood
potential via a mixture density network over ESM-2/sPhysNet embeddings — purely geometric
supervision, with no discrete interaction-type label (hydrogen bond, hydrophobic contact,
π-stacking) or pharmacophore directional constraint anywhere in its inputs or loss. This is
architecturally distinct from the interaction-fingerprint/pharmacophore features this work
proposes to feed back into reranking, and an independent large-scale evaluation of this exact
pipeline (Abo-Dahab et al., arXiv:2605.01681) reports that DiffDock-NMDN underperforms the
unscored DiffDock baseline on LIT-PCBA (median EF1% 0.67 vs. 1.17), which we read as evidence
that a purely distance-based rescorer does not obviously substitute for the discrete interaction
signal this work targets.

**Positioning.** The confidence-related evidence in this literature splits into three parts that
do not overlap: in-distribution ranking evidence for DiffDock-family confidence, out-of-
distribution accuracy-degradation evidence that never measures confidence, and
interaction-recovery evidence with no link to confidence or rescoring. This work first measures
the missing link between the first two (calibration under cross-docking shift, reported below),
then specifies — as a not-yet-executed follow-on — the missing link to the third (a rescoring
model that explicitly uses the interaction signal raw confidence ignores).

---

## 3. Method

### 3.1 Phase 1 — calibration diagnosis (executed on DockGen-E; broader protocol only partly run)

The object under evaluation is the calibration of DiffDock-L's own confidence output, not its
raw accuracy. For each complex, DiffDock-L samples N candidate poses and emits a confidence
logit per pose, trained under a binary cross-entropy-with-logits objective to predict RMSD < 2 Å.
We take sigmoid(logit) of the top-ranked pose as a probability estimate P(RMSD < 2 Å), consistent
with that training objective, and evaluate it against two ground-truth labels: the conventional
RMSD < 2 Å criterion (primary), and ProLIF-computed PLIF interaction recovery against the
reference structure (secondary, chemically orthogonal).

The full designed protocol specifies five comparators: DiffDock-L on PDBBind (in-distribution
anchor), base DiffDock on the same cross-docking complexes (within-family contrast), FlowDock's
plDDT-style confidence (deep-generative comparator), classical docking scores (AutoDock Vina
primary, GNINA CNN score secondary, as non-learned, non-memorization contrasts), and post-hoc
recalibration (temperature/isotonic scaling, to separate a simple scale problem from a directional
failure). **Of these five, only DiffDock-L on DockGen-E has been run and evaluated as of this
draft** (§4). The PDBBind anchor, base DiffDock, FlowDock, and the classical-scoring and
recalibration comparators are installed and functional on the project's compute environment (SDSU
HPC "Innovator" cluster) but have not yet been executed on this benchmark; we report this
explicitly rather than assume their outcome.

Metrics are ECE, adaptive-binning ECE, Brier score, and reliability diagrams — planned aggregate
and stratified by pocket similarity to training data (max TM-score for PoseX-CD, PLINDER SuCOS for
DockGen-E) — plus risk–coverage / AURC as a comparator-semantics-free cross-model metric, and the
confidence-vs-PLIF-recovery relationship as the second, chemically orthogonal evaluation axis.
**The aggregate (non-stratified) ECE has been computed and remains valid** (§4). An aggregate PLIF
interaction-recovery rate and its correlation with confidence were also computed early on (pooled
recovery 15.47%; Spearman rho = -0.149, n=78, t(76) = -1.31), but **[INVALIDATED — see §4.4a]:
both were computed against the wrong (crystal, not ESMFold-predicted) protein file.** A hybrid
recomputation against the correct protein file, using a non-redundant 9-type ProLIF interaction
list, now gives a valid pooled PLIF recovery rate: 9.23% (47/509, matched n=82) for the
confidence-selected rank-1 pose against a rank1–10 oracle upper bound of 12.57% (64/509, §4.4a).
The confidence-vs-PLIF-recovery correlation has since been recomputed against this corrected data
and finds no statistically significant monotonic relationship (Spearman rho = 0.046, two-sided
p = 0.682, n=81; §4.4a). Stratified reliability diagrams, AURC, and the classical/recalibration
comparators remain designed but unexecuted.

### 3.2 Phase 2 — Interaction-Aware Rescoring (oracle gate and non-learned comparators B1/B3 executed; learned rescorer M1/M1-abl design only, not trained)

Phase 2 is defined as a reranking problem, not a pose-generation problem: DiffDock-L already
samples and confidence-ranks multiple candidate poses per complex, and the project's HPC runs
retain the top-10 ranked poses per complex from the Phase 1 inference. Rather than resample,
Phase 2 reranks within this existing candidate pool of 10 poses per complex, which requires no
additional GPU inference for the evaluation benchmark and keeps the comparison to raw confidence
on an identical candidate set.

**Step 0 — oracle-headroom gate (mandatory, run before any model is trained).** For every complex,
we compute per-rank RMSD and per-rank PLIF recovery across all 10 candidates and compare three
quantities, all on the same 122-complex denominator: (B0) the existing raw-confidence baseline —
rank-1 top-1 success; (B2) an oracle upper bound — success if any of the 10 candidates clears the
criterion, defining the best any reranking method could possibly achieve; and (B1) a random-choice
lower sanity bound. The pre-registered decision rule is: if oracle ≈ baseline (headroom below
roughly 5 percentage points, i.e., fewer than about 6 complexes), rescoring is abandoned as a
direction for that criterion, because the correct pose is not present in the candidate pool for
reranking to find — a limitation to report, not a rescoring failure. If headroom clears that bar,
rescoring proceeds on that criterion. **This gate has now been run for both RMSD and PLIF, and the
two criteria disagree.** RMSD: baseline 14/122 (11.48%) to oracle 22/122 (18.03%), headroom +6.56
percentage points — clears the bar, **PASS**. PLIF (hybrid-recomputed, §4.4a): baseline 9.23%
(47/509) to oracle 12.57% (64/509), headroom +3.34 percentage points — below the bar, **FAIL**.
We read this pair of results as measuring two different failure modes, not as a contradiction.
The RMSD headroom shows a *selection* problem: a better-RMSD pose already exists in the
confidence-ranked candidate pool for a meaningful number of complexes, and DiffDock-L's confidence
score is simply not choosing it — exactly the failure a learned rescorer is built to fix. The
small PLIF headroom shows a *sampling* limitation instead: even an oracle that always chose the
single best-PLIF-recovery candidate out of 10 barely improves over confidence's rank-1 choice,
which means the candidate pool itself rarely contains a chemically much-better alternative to
rerank toward. No reranking method — including the one proposed here — can recover interactions
that were never sampled in the first place. Applying the decision rule per-criterion (an
effective logical OR across the two gates, since either criterion clearing the bar is sufficient
justification to proceed) means **Phase 2 proceeds**, justified by the RMSD-side headroom alone.
We do not extend that justification to PLIF: this draft does not claim, and explicitly disclaims,
that Interaction-Aware Rescoring will materially improve PLIF-based chemical correctness, since
the ceiling for that improvement is measured here at +3.34 points regardless of how good the
reranker is. The PLIF-derived features in M1 below (interaction-type counts, pharmacophore
geometry) are accordingly justified only as auxiliary signal that may help RMSD-based selection —
consistent with Errington et al.'s finding that RMSD-based correctness and PLIF recovery are not
the same axis (§2) — not as a mechanism expected to close the small PLIF gap itself. Any
PLIF-recovery improvement M1 shows is reported as a secondary, exploratory result, not a claimed
contribution.

**Comparators (Step 0 passed, on RMSD-selection grounds).** All comparators rerank within the same fixed
10-candidate pool and are evaluated on the identical 122-complex denominator used for Phase 1:
B0 (raw confidence, rank-1 — the existing baseline), B1 (random-in-candidates), B2 (oracle,
upper bound, not achievable by any method), B3 (classical rescoring of the 10 candidates by Vina
score, primary, and GNINA CNN score, secondary — a non-learned, non-PLIF contrast), M1 (the
proposed PLIF-aware learned rescorer), and M1-abl (an ablation of M1 with PLIF features removed,
isolating whether any improvement comes specifically from the interaction signal or from the
other features alone).

**B1 and B3 have since been executed (2026-07-21); M1 and M1-abl remain unexecuted.** B1
(random-in-candidates) is inherently probabilistic, so it is reported as an expected success rate
rather than a single random draw: summing each complex's fraction of the 10 candidates with
RMSD < 2 Å (`n_ranks_lt2A`/`n_ranks` in `rank_oracle_rmsd.csv`) over the 98 of 122 complexes with
per-rank RMSD available gives an expected 13.5667/122 = 11.12%, on the same fixed 122-complex
denominator — 0.36 percentage points below B0's observed 14/122 = 11.48%, a difference too small
to read as meaningful given B1 is an expectation, not an integer observation. B3 (classical
rescoring) used GNINA 1.3.3 (`--score_only --cnn_scoring none`) to score each of DiffDock-L's
retained rank1–10 candidates against the same ESMFold-predicted protein structure used at
inference, selecting the lowest-affinity pose per complex; all 111 complexes with usable
candidates were processed with zero task failures (SLURM array job 12508307), of which 98 are
RMSD-evaluable. B3 succeeds on 15/122 = 12.30% of complexes, one complex more than B0
(+0.82 percentage points); a paired comparison shows both methods succeeding on the same 11
complexes, with 3 B0-only and 4 B3-only successes — only 7 discordant pairs out of 122 — so this
one-complex difference is not read as a clear improvement. B0, B1, and B3 therefore all fall
within a narrow 11.12–12.30% band: neither a random reranking nor a classical affinity-based
reranking of the same candidate pool moves the needle materially over raw confidence. This
motivates M1 as a learned alternative, but it also sets the bar M1 must clear by a defensible
margin — evaluated with the same paired statistics specified below — for Phase 2 to represent a
genuine improvement rather than a restatement of this band.

**Features.** Because inference-time candidates have no reference structure, the model cannot
use PLIF *recovery* (which requires a native pose) as an input feature — only the absolute
interaction fingerprint each candidate pose itself forms. ProLIF's per-residue interaction
bits are not transferable across complexes with different binding-site residues, so features are
aggregated into complex-invariant quantities: counts of each ProLIF interaction type (hydrogen
bond donor/acceptor, hydrophobic, π-stacking, π-cation/cation-π, halogen bond, ionic, metal
coordination) formed by the candidate pose; pharmacophore geometry summaries (donor/acceptor/
aromatic-center distance and alignment statistics); the raw DiffDock-L confidence logit; and an
ensemble-consistency feature counting how many of the other 9 candidates fall within 2 Å RMSD of
this one (a near-zero-cost signal independent of PLIF). These feature dimensions are identical
across PDBBind and DockGen-E, enabling cross-complex training and evaluation.

ProLIF fingerprint computation itself is not universally reliable: in Phase 1 it failed outright
on 11 of 91 (~12%) RMSD-scored complexes (uint32 interaction-index overflow, missing van der
Waals radii for uncommon metal centers, and one residue-identity mismatch; §4.4). This
failure-rate figure comes from the same V1 pipeline now found to score against the wrong protein
file (§4.4a); it is plausible but not confirmed that these outright computation crashes are
independent of that bug and will recur unchanged after recomputation. The same
failure modes are expected to recur when computing per-candidate PLIF features for Phase 2, since
they arise from the same ProLIF call applied to structurally similar poses. Phase 2's feature
extraction and the rescorer itself must therefore treat missing PLIF features as a first-class
case (e.g., a missingness indicator plus fallback to the non-PLIF features) rather than assume
every candidate pose yields a usable fingerprint.

**Training and leakage control.** M1 and M1-abl are gradient-boosted trees (shallow depth, strong
regularization given expected small effective sample size) trained exclusively on a PDBBind
in-distribution split, disjoint from all cross-docking evaluation data. Training requires running
DiffDock-L inference on PDBBind to obtain the same candidate-pose and feature representation used
at evaluation time — the only additional GPU cost Phase 2 introduces beyond the existing Phase 1
runs, justified now that Step 0 has passed on RMSD-selection grounds. Supervision targets are
RMSD < 2 Å (primary) and PLIF recovery (secondary, exploratory given the small PLIF-oracle
headroom found in Step 0). No component of DiffDock-L itself — score network or confidence
network — is retrained; only the reranking step is learned.

**PDBBind subset data-source caveat — [INVALIDATED, see the 2026-07-23/24 erratum above: this
1,500-complex subset was itself drawn from `timesplit_no_lig_overlap_train`, DiffDock-L's own
training split, and cannot be used as M1/M1-abl training data; superseded by a 585-complex
validation-split plan].** For tractable inference cost, M1/M1-abl training uses a
1,500-complex PDBBind subset drawn (seed=42, random sample) from the project's 16,379-ID PDBBind
train list, rather than the full training set. While provisioning it, the data source cited in
DiffDock's own GitHub README (Zenodo record 6408497, EquiBind-processed complexes) was confirmed
deleted (Zenodo API, checked 2025-01-13) — a pre-existing defect in the upstream DiffDock
repository, not introduced by this project. A substitute, Zenodo record 7014096 (different
uploader, CC-BY-4.0, PDBBind v2020 refined+general set), was adopted; it uses the same complex IDs
and the standard `<PDBID>_protein.pdb`/`_ligand.sdf`/`_pocket.pdb` file layout DiffDock/PoseBench
expects, but was prepared with a different structure-preparation pipeline (Schrödinger Protein Prep
Wizard) than the original (EquiBind's own processing), so protonation states and exact coordinates
may differ slightly between the two sources. This has not been empirically checked (e.g., via a
backbone-RMSD spot check between overlapping complex IDs) and is disclosed here as an open
reproducibility caveat on M1/M1-abl's training data, to be resolved before those results are
reported as findings. M1/M1-abl themselves remain unexecuted as of this draft.

**Failure exclusions in the training subset — [the underlying 1,500-complex subset is INVALIDATED
as training data, see the 2026-07-23/24 erratum above; the counts below describe abandoned data
preparation, not M1's actual training set].** GPU inference for M1/M1-abl over this 1,500-complex
subset is now complete. DiffDock-L's inference path has no fixed random seed (no `--seed` argument
and no `torch.manual_seed` call; the one fixed seed present in `conformer_matching.py` is used only
by a training-time function, confirmed unused at inference), so many inference failures are
stochastic and were retried across multiple rounds before this final accounting. After all
retries, code-level fixes (an OpenBabel fallback for RDKit-unparsable ligands, a
conformer-embedding fallback for chirality-sensitive ligands, and a backbone-atom-selection fix for
non-standard-residue receptors), and a full merge-and-recount of all output directories,
**1,440/1,500 (96.0%) complexes yielded valid outputs**. The remaining 60 (4.0%) were
re-classified by reading each complex's individual log section directly (a whole-log keyword
search was found to misclassify some cases and was discarded as unreliable): 37
SVD-ill-conditioned (non-convergent Kabsch alignment), 12 RDKit ligand-parsing failures that
resisted the OpenBabel fallback, 6 TorchScript `radius.py` `RuntimeError` failures (confirmed
fatal, not a benign warning, by inspecting each complex's log for an explicit `Failed for 1
complexes` line), 4 receptor-too-large skips (pipeline's 3,000-residue threshold), and 1 CSV-field
`AttributeError` (a complex-name field parsed as `float` rather than `str`, newly identified this
pass) — 37+12+4+6+1=60, and 1,440+60=1,500. These 60 complexes are excluded from M1/M1-abl's
training data. The RDKit-parsing failures overlap with a previously characterized list of 236
PDBBind ligands with the same defect (consistent with PDBBind's own reported ~16% RDKit-parsing
failure rate across the full dataset, arXiv:2411.01223), a list previously found to concentrate
disproportionately in polysaccharide- and peptide-like ligands rather than being spread uniformly
across chemotypes (§4.6(j)). **RMSD self-consistency against the PDBBind-subset ground truth has
not yet been recomputed for this final 1,440-complex sample**; the previously reported 1,043/1,500
(69.5%) figure was computed against the earlier, superseded 1,343-complex accounting and is stale
— it is not restated here, and should not be rescaled by proportion to approximate a
1,440-complex figure; a fresh computation is required before this sanity check can be reported.

**Evaluation and statistics.** M1/M1-abl are compared against B0/B1/B2/B3 on the same 122-complex
DockGen-E denominator and the same RMSD < 2 Å and PLIF-recovery correctness definitions used in
Phase 1, so Phase 2 numbers are directly comparable to the Phase 1 baseline reported in §4.
Comparisons are planned to be paired at the complex level (same 122 complexes across all methods),
using McNemar's exact test for paired top-1 correctness plus bootstrap confidence intervals for
the success-rate delta, given the small expected effective sample size (91 scored complexes, 14
baseline successes) and correspondingly low statistical power. Effect sizes (the number of
complexes gained or lost) are to be reported alongside any p-value, not in place of it. DockGen-E
is treated as a pilot; PoseX-CD (1,312 leakage-controlled complexes) is the designated
confirmatory extension once directionality and effect size are established on DockGen-E.

---

## 4. Experiments

### 4.1 Datasets

**DockGen-E** (122 complexes, curated by PoseBench as a bioassembly-aware refinement of the
original 189-complex DockGen cross-docking generalization benchmark, Corso et al.,
arXiv:2402.18396): complexes with binding pockets dissimilar to PDBBind training data, used here
as the sole cross-docking test set for the measured Phase 1 results below. **PoseX-CD** (1,312
leakage-controlled cross-docking complexes, 2022–2025, from CataAI/PoseX, arXiv:2505.01700) is
designated as a planned confirmatory extension and has not been run. **PDBBind** serves as the
in-distribution anchor for the full designed Phase 1 protocol and as the exclusive training split
for the Phase 2 rescoring model; neither role has been executed yet.

### 4.2 Environment and executed protocol

DiffDock-L inference ran on the SDSU HPC "Innovator" SLURM cluster (`gpu` partition), using
PoseBench's official inference and evaluation pipeline
(BioinfoMachineLearning/PoseBench, tag v1.1.0-1-gc5d728d) with N=10 sampled poses per complex.
ProLIF 2.2.0 computed PLIF interaction fingerprints. Base DiffDock, FlowDock, GNINA, and AutoDock
Vina are installed and verified functional in the same environment but have not been run on this
benchmark for the present draft.

### 4.3 Denominator methodology

We fix the evaluation denominator at all 122 DockGen-E complexes and count every complex that does
not produce a scorable pose as non-success, rather than restricting the denominator to complexes
with successfully computed output. An earlier plan to report success rate over only the 111
complexes with any usable inference output was rejected during this project as a methodological
error that would inflate the reported success rate; we instead follow the convention, attributed
in the project's working notes to PocketVina (arXiv:2506.20043), of retaining the original sample
size as the denominator even when a method fails outright on some inputs.

Of 122 complexes: **11 produced no output at all** (runtime failures during inference or
downstream RMSD-alignment, which failed reproducibly across 2 independent retry rounds
(2026-07-18, 2026-07-19) — traced in this
project's execution logs to two distinct causes, 7 numerically ill-conditioned SVD failures during
Kabsch alignment and 4 RDKit ligand-conformer or downstream exception-handling failures);
**20 produced poses but could not be RMSD-scored**, owing to non-standard ligand chemistry that
the current DiffDock-L/PoseBench pipeline does not parse correctly (peptide-like ligands, ligands
with repeated glycine residues, and metal-ion ligands); and **91 were fully scored**. We flag one
documentation discrepancy for the record and resolve it in favor of the primary source: this
project's GitHub repository README attributes all 11 runtime failures to a single
"group-aggregation bug in PoseBench's fork of `inference.py`," while the more granular HPC
execution log — which records the exact error text and complex ID for each of the 11 failures
(e.g., `linalg.svd: ... ill-conditioned or has too many repeated singular values` for the 7 SVD
cases; `'ValueError' object has no attribute 'RemoveAllConformers'` and
`inference.py:449: NameError: name 'idx' is not defined` for two of the 4 RDKit/exception-handling
cases) — attributes them to the two causes above. No occurrence of "group-aggregation" or a
matching failure signature appears anywhere in the execution log's record of these 11 complexes;
the log's only group-aggregation-related issue is a separate, already-fixed bug (trailing `_N`
suffix stripping in output directory names, symlink-patched, log entry 2026-07-19) that affected
13 *different*, already-successfully-scored complexes, not these 11 failures. We therefore treat
the execution-log breakdown as the correct account per this project's evidence-priority order
(primary run logs over a summary README) and flag the README wording as incorrect, to be corrected
in a follow-up pass rather than left as an open discrepancy.

### 4.4 Results (measured, 2026-07-19; PLIF figures superseded and correlation recomputed 2026-07-21, see §4.4a)

| Metric | Value | Denominator / basis |
|---|---|---|
| Top-1 RMSD < 2 Å success rate | **14/122 = 11.48%** | fixed denominator 122 (all complexes; 11 runtime failures and 20 unscored complexes counted as non-success) |
| — reference figure | 15.38% | 91 RMSD-scored complexes only (not the primary denominator) |
| — reference figure | 12.61% | 111 complexes with any usable inference output (not the primary denominator; rejected as a reporting basis, see §4.3) |
| Expected calibration error (ECE) | **0.203** | 91 scored complexes; confidence = sigmoid(raw logit) as a P(RMSD < 2 Å) estimate, consistent with DiffDock's BCE-with-logits training objective; the 20 unscored complexes are excluded from this calculation rather than treated as incorrect |
| PLIF interaction recovery (pooled, rank-1 confidence baseline) — original computation **[INVALIDATED, §4.4a]** | ~~15.47%~~ (138/892) | pooled across 80 of the 91 scored complexes; **computed against the wrong (crystal, not ESMFold-predicted) protein file — see §4.4a** |
| PLIF interaction recovery (pooled, rank-1 confidence baseline) — **hybrid recomputation, valid** | **47/509 = 9.23%** | matched n=82; per-complex mean 8.82%, median 0%; correct (ESMFold-predicted) protein file + non-redundant 9-type interaction list; one complex (`2wwc_1_CHT_2`) has 0 true interactions and is undefined (NaN), excluded from mean/median (n=81 non-null), contributes 0/0 to pooled figure; see §4.4a |
| PLIF interaction recovery (pooled, rank1–10 oracle) — **hybrid recomputation, valid** | **64/509 = 12.57%** | same matched n=82 basis as above; per-complex mean 11.86%, median 0%; oracle headroom over the baseline row above is +3.34 points pooled (+3.05 points per-complex mean); see §4.4a and §4.5 |
| Confidence–PLIF recovery rank correlation — original computation **[INVALIDATED, §4.4a]** | ~~Spearman rho = -0.149~~ (not significant) | n=78 (of the 80 PLIF-valid complexes in the original, now-superseded computation); computed against the wrong protein file — see §4.4a |
| Confidence–PLIF recovery rank correlation — **hybrid recomputation, valid** | **Spearman rho = 0.046 (two-sided p = 0.682), not significant** | n=81 of the matched n=82 hybrid subset (one complex excluded, undefined recovery); independent average-rank Pearson calculation reproduced the same rho exactly; see §4.4a |

#### 4.4a Post-hoc invalidation of the original PLIF result, a valid hybrid replacement, and the recomputed correlation (2026-07-21)

The PLIF recovery rate and the confidence-vs-PLIF-recovery correlation originally reported for
this manuscript were computed by `eval_scripts/compute_plif.py` (this project's "V1" PLIF
pipeline) and were originally verified as *reproducible* from `plif_recovery_results.csv` and
`master_eval_table_n122_with_plif.csv`. A subsequent code audit found that reproducibility is not
the same as methodological validity: V1 scores each predicted ligand pose's interaction
fingerprint against the **crystal protein file** (`protein_processed.pdb`) rather than the
**ESMFold-predicted protein file DiffDock-L actually used at inference time**
(`holo_aligned_predicted_protein.pdb`), confirmed by cross-checking V1's protein-file inputs
against `diffdock_dockgen_inputs.csv`. Every complex's PLIF fingerprint was therefore computed in
a structural context DiffDock-L never saw, which invalidates the resulting recovery numbers
regardless of how carefully the downstream pooling, denominator, or correlation arithmetic was
done.

**Invalidated.** Pooled PLIF interaction recovery 15.47% (138/892, computed over 80 of the 91
RMSD-scored complexes; per-complex mean 17.3%, median 0%), and the confidence-vs-PLIF-recovery
Spearman rank correlation (rho = -0.149, n=78, t(76) = -1.31, not significant). Neither number is
cited as a finding anywhere in this draft; both are retained only as a transparent record of what
was measured and later retracted.

For denominator bookkeeping only (not a validity claim about the retracted V1 numbers): ProLIF
fingerprint computation itself failed outright on 11 of the 91 RMSD-scored complexes regardless of
protein file (7 from a numeric overflow in interaction-fingerprint indexing, `OverflowError:
Python integer ... out of bounds for uint32`; 3 from missing van der Waals radii for
metal-coordination atoms Fe/Mo; 1 from a residue-identity mismatch), leaving 80 as the denominator
for the retracted V1 pooled figure and 78 for the retracted V1 correlation (2 of the 80 lack a
`confidence_rank1` value, cause undiagnosed).

**Not affected.** Top-1 RMSD < 2 Å success rate (14/122 = 11.48%) and ECE (0.203) are computed by
a separate pipeline (`build_master_table.py`, `compute_ece.py`) that does not involve the
ground-truth protein file used for PLIF scoring and is untouched by this bug. Similarly, an
exploratory (not significance-tested) rank correlation between confidence and binary RMSD < 2 Å
success (n=91 scored complexes) of approximately +0.37, in the expected direction, does not depend
on PLIF or the protein-file bug and is reported only for context, not as a confirmed finding.

**Hybrid recomputation (complete).** A second, independently written pipeline ("V2",
`dockgen_pilot_eval/`) uses the correct protein file but a broader ProLIF interaction-type list
(`interactions="all"`, 15 types, which double-counts π-stacking as both EdgeToFace and
FaceToFace) and reported pooled recovery 7.47% (86/1151, matched n=82) — never adopted as a
replacement for 15.47%, since its interaction-list redundancy is itself a methodological problem.
The required combination — V2's correct protein-file handling with V1's non-redundant 9-type
interaction list — has now been run over the matched n=82 subset. Results:

- **Baseline (rank-1, confidence-selected pose):** pooled recovery 47/509 = **9.23%**;
  per-complex mean 8.82%, median 0%. Source: `hybrid_plif_baseline_matched82.csv`, script
  `hybrid_plif_baseline.py`.
- **Oracle (best of rank1–10 candidates per complex):** pooled recovery 64/509 = **12.57%**;
  per-complex mean 11.86%, median 0%. Source: `hybrid_plif_oracle_matched82.csv`, script
  `hybrid_plif_oracle.py`.
- **Headroom:** +3.34 percentage points pooled, +3.05 points per-complex mean (see §4.5 for the
  gate interpretation alongside the RMSD-side headroom).
- **Denominator note:** one complex (`2wwc_1_CHT_2`) has zero true interactions under this 9-type
  list, making its per-complex recovery undefined (NaN); it contributes 0/0 to the pooled figures
  (no effect on the pooled percentages) and is excluded from the per-complex mean/median, which are
  therefore computed over n=81 non-null complexes.
- Both files live under `~/docking_project/PoseBench/forks/DiffDock/results/dockgen_pilot_eval/`
  on the project's HPC environment.

These two numbers (9.23% baseline, 12.57% oracle) are this manuscript's reported PLIF recovery
figures, superseding the retracted 15.47%.

**Confidence-vs-PLIF-recovery correlation (complete).** The correlation itself — a distinct
computation from the recovery-rate recomputation above — has also now been run against these
hybrid values. All 82 hybrid baseline rows matched a `confidence_rank1` value from
`master_eval_table_n122_with_plif.csv`; the one complex with zero true interactions and therefore
undefined recovery (`2wwc_1_CHT_2`) was excluded, leaving n=81. Spearman rho = 0.046167845505,
two-sided p = 0.682340974058; an independent average-rank Pearson calculation reproduced the same
rho exactly. **The retracted rho = -0.149 (computed from the invalidated V1 data) remains
INVALIDATED and was not reused in any part of this computation.** As with that earlier result, we
read this only as a limited, non-causal statement: no statistically significant monotonic
relationship between DiffDock-L's confidence score and this corrected PLIF-recovery rate was
observed in this sample. Source: `eval_scripts/correlate_hybrid_plif.py`,
`results/dockgen_pilot_eval/hybrid_plif_confidence_spearman.json`.

The RMSD-based success rate and ECE, the hybrid-recomputed PLIF recovery rate and its oracle
headroom, and the confidence-vs-PLIF-recovery correlation (rho = 0.046, p = 0.682, n=81, not
significant) are the measured Phase 1 numbers this draft can report as findings. Stratified
(pocket-similarity) reliability diagrams, the PDBBind in-distribution ECE anchor, AURC/risk–coverage,
and the base-DiffDock/FlowDock/classical-scoring comparators specified in §3.1 have not been
computed. Consequently, this draft can report that DiffDock-L's confidence score is, in absolute
terms, poorly calibrated on this cross-docking benchmark, only weakly related to top-1 correctness,
paired with a candidate pool whose chemical (PLIF) correctness is low and has only modest headroom
to improve by reranking, and shows no measured monotonic relationship to that chemical correctness
— but it cannot yet report whether the observed miscalibration is *directional* (i.e., worse
specifically under distribution shift relative to an in-distribution anchor, as prior
rank-correlation and accuracy-degradation evidence would predict) or *stratified* (concentrated in
low pocket-similarity complexes), because the comparison points
needed to establish either claim have not been measured in this project. We flag both as open, not
as findings.

An earlier 65-complex pilot on an overlapping but not identical set reported success rate 18.5%,
ECE 0.53, and PLIF recovery 6.0%. Its computation scripts were not preserved, so this draft treats
those figures as unverifiable background only — not as a comparison point — and adopts the n=122
result above as the project's sole reported baseline.

### 4.5 Phase 2 status — oracle-headroom gate and non-learned baselines (B1, B3) executed; learned rescorer not yet trained

The oracle-headroom gate (§3.2, Step 0) — the first required step before any rescoring model is
trained — has now been run over per-rank RMSD and per-rank PLIF recovery for the retained
rank1–10 candidate pool, on the same 122-complex denominator as Phase 1.

| Gate | Baseline (rank-1, confidence-selected) | Oracle (best of rank1–10) | Headroom | Result vs. +5pp bar |
|---|---:|---:|---:|---|
| RMSD < 2 Å | 14/122 = 11.48% | 22/122 = 18.03% | **+6.56 points** | **PASS** |
| PLIF recovery (pooled, hybrid-recomputed, §4.4a) | 47/509 = 9.23% | 64/509 = 12.57% | **+3.34 points** | **FAIL** |

The two gates measure different things and disagree. RMSD headroom of +6.56 points means a
better-RMSD pose already exists, unchosen, in the confidence-ranked candidate pool for a
non-trivial number of complexes — a *selection* problem that a learned rescorer is directly built
to address. PLIF headroom of +3.34 points means that even an oracle that always picked the
single most chemically-correct candidate out of 10 barely improves over confidence's own choice —
a *sampling* limitation: the candidate pool itself rarely contains a much better chemical match to
select toward, so no reranking method, however good at selection, can recover much there.

Applying the pre-registered decision rule per criterion, and treating either criterion clearing
the bar as sufficient to proceed (an effective logical OR across the two gates), **Phase 2
proceeds**, justified by the RMSD-side headroom alone. This draft does not extend that
justification to PLIF: no claim is made, and none should be inferred, that Interaction-Aware
Rescoring will materially improve PLIF-based chemical correctness — the measured ceiling for that
improvement is +3.34 points regardless of rescorer quality. PLIF-derived features in the proposed
M1 model (§3.2) are correspondingly framed as auxiliary signal for improving RMSD-based selection,
and any PLIF-recovery gain M1 shows in evaluation is to be reported as a secondary, exploratory
result rather than a headline contribution.

**Non-learned comparators B1 and B3 (executed, 2026-07-21).** Beyond the oracle gate (B2) above,
the two non-learned rerankers specified in §3.2 have also been run on the same fixed 122-complex
denominator, on the same retained rank1–10 candidate pool:

| Comparator | Success rate | vs. B0 (14/122 = 11.48%) | Basis |
|---|---:|---:|---|
| B0 — raw confidence (rank-1) | 14/122 = 11.48% | — | existing baseline |
| B1 — random-in-candidates (expected value) | 13.5667/122 = 11.12% | -0.36 points | expected value from per-rank RMSD, 98/122 complexes evaluable; not an integer observation |
| B3 — GNINA/Vina affinity rerank | 15/122 = 12.30% | +0.82 points (+1 complex) | 111/122 processed (SLURM array 12508307, 0 failures), 98/122 RMSD-evaluable; paired vs. B0: both-success 11, B0-only 3, B3-only 4 |

B0, B1, and B3 all fall within an 11.12–12.30% band on this benchmark. B3's one-complex gain over
B0 is not read as a clear improvement, given only 7 discordant pairs out of 122. This narrow spread
across a random baseline, the raw confidence baseline, and a classical affinity-based reranker
indicates that neither randomness nor classical scoring meaningfully exploits the RMSD-side
headroom identified by the oracle gate above. It motivates M1 as a learned alternative, but it also
sets a modest bar (~12%) that M1 must clear by a defensible margin for Phase 2 to represent more
than a restatement of this band. M1 and M1-abl remain unexecuted; the single most consequential
open step, now that the gate and non-learned comparators are in hand, is the actual training and
evaluation of M1/M1-abl against B0/B1/B2/B3 as specified in §3.2.

### 4.6 Limitations

(a) The Phase 1 protocol as designed includes five comparators and a stratified analysis; only
one comparator (DiffDock-L on DockGen-E, aggregate statistics) has been executed. Claims of
directional or stratified miscalibration are not yet supported by measurement. (b) 20 of 122
DockGen-E complexes (16%) cannot be RMSD-scored under the current pipeline because of non-standard
ligand chemistry (peptide-like ligands, repeated glycine, metal ions) — a structural limitation of
the DiffDock-L/PoseBench pipeline as deployed here, not resolved without code-level changes, and a
source of missing data rather than measured failure for those complexes' correctness. (c) The
per-complex PLIF-recovery distribution is heavily skewed (median 0% in both the now-invalidated V1
computation and the valid hybrid recomputation, §4.4a, for baseline and oracle alike); Phase 2 will
need to account for this in how it defines a PLIF-recovery training target rather than treating it
as a simple regression or balanced-classification signal. (d) DockGen-E (n=122, 91 scored) gives low
statistical power; any Phase 2 comparison will need the PoseX-CD extension (n=1,312) before a
significance claim is defensible, per the pre-registered plan in §3.2. (e) Comparator confidence
scores (DiffDock-L's learned probability vs. Vina's empirical scoring function vs. a trained
rescorer's output) are not on a common semantic scale; where a future draft reports ECE for
multiple comparators, it must also report AURC/risk–coverage as a semantics-free alternative,
per the design in §3.1. (f) The documentation discrepancy noted in §4.3 regarding the cause of
the 11 runtime failures has been resolved in favor of the execution-log breakdown (SVD
ill-conditioning ×7, RDKit/exception-handling ×4); the project's own public README still carries
the outdated single-cause wording and needs a corrective update outside this manuscript. (g) **(A
historical denominator note about the now-retracted V1 PLIF computation, §4.4a; kept for the
record, not for reuse.)** The retracted V1 pooled/mean/median recovery figures were computed over
80 of the 91 RMSD-scored complexes, not all 91, because ProLIF fingerprint computation itself
failed outright on the remaining 11 (7 interaction-index overflow, 3 missing metal van der Waals
radii, 1 residue-identity mismatch). The valid hybrid recomputation (§4.4a) uses a different
denominator (matched n=82, one further complex with an undefined/NaN recovery value) inherited from
the V2 pipeline's matching procedure, not this 80/91 breakdown; the two denominators should not be
conflated. The same fingerprint-computation failure modes remain a coverage risk for Phase 2
per-candidate feature extraction (§3.2). (h) **The confidence-vs-PLIF-recovery correlation has now
been recomputed against the valid hybrid PLIF values (§4.4a).** The only earlier correlation
computed (n=78, rho = -0.149) used the now-retracted V1 PLIF pipeline (scored against the crystal,
not ESMFold-predicted, protein file) and remains uncited as a finding. The hybrid-value
recomputation (n=81, Spearman rho = 0.046167845505, two-sided p = 0.682340974058, independently
reproduced via an average-rank Pearson calculation) finds no statistically significant monotonic
relationship — a distinct analysis from the recovery-rate recomputation itself, and one that should
be read only as "no clear rank relationship observed in this sample," not as evidence that
confidence and PLIF recovery are causally related or unrelated. (i) **The original PLIF recovery
measurement was invalidated by a ground-truth protein-file bug** (scored the predicted ligand pose
against the crystal protein file rather than the ESMFold-predicted protein file DiffDock-L actually
used); a hybrid recomputation against the correct protein file has since produced valid replacement
figures (9.23% baseline, 12.57% oracle, §4.4a). The confidence-vs-PLIF-recovery correlation, the one
other PLIF-derived quantity from the original computation, has also now been recomputed against the
corrected data (rho = 0.046, n=81, not significant; see (h) above). (j) **PDBBind training-subset
(M1/M1-abl) exclusion bias — [subset itself now INVALIDATED as training data, 2026-07-23/24
erratum above; this bullet describes an abandoned data-preparation pass, kept as a record].** Of
the 1,500-complex PDBBind subset drawn for M1/M1-abl training
(§3.2), after all retries and code-level fixes 1,440/1,500 (96.0%) complexes yielded valid outputs;
the remaining 60 (4.0%) were excluded from the final training data: 37 SVD-ill-conditioned, 12
RDKit ligand-parsing failures (overlapping a previously identified 236-complex list
disproportionately containing polysaccharide- and peptide-like ligands, consistent with PDBBind's
own known ~16% RDKit defect rate, arXiv:2411.01223), 6 TorchScript `radius.py` `RuntimeError`
failures, 4 receptor-size-limit skips, and 1 CSV-field `AttributeError` (§3.2). The direction of
this bias, not its magnitude, is the operative concern for the RDKit-related subset: M1 has
systematically fewer training examples on large, peptide-like ligands than a uniformly random 4%
reduction would imply, and any accuracy comparison involving this chemotype should be read with
that caveat. **RMSD self-consistency for this final 1,440-complex sample has not yet been
recomputed** (§3.2) — this is a missing sanity check, not a null result, and should not be
inferred from the earlier, now-superseded 1,343-complex figure. (k) **PDBBind data-source
substitution — [written against the now-abandoned 1,500-complex train-split subset; whether the
same Zenodo substitution applies unchanged to the superseded 585-complex validation-split plan has
not been confirmed as of this draft].** M1/M1-abl's training structures come from a substitute Zenodo record (7014096)
rather than the source cited in DiffDock's own README (record 6408497, confirmed deleted; §3.2),
because the original is no longer available. The substitute was prepared with a different
structure-preparation pipeline (Schrödinger Protein Prep Wizard vs. the original EquiBind
processing), so protonation states and coordinates may differ slightly from what DiffDock-L's
original authors used; this has not been empirically checked (e.g., via a backbone-RMSD spot check
between overlapping complex IDs) and is disclosed as an open reproducibility caveat, not a resolved
non-issue.

---

## 5. Conclusion (interim)

This draft reports a measured diagnosis, a measured oracle-headroom gate, and a specified but
not-yet-trained correction. On the DockGen-E cross-docking benchmark, DiffDock-L's top-1 pose is
correct (RMSD < 2 Å) for 14 of 122 complexes (11.48%), and its confidence score has ECE 0.203 on
the 91 complexes where correctness could be scored. An earlier reported PLIF recovery figure
(15.47%, pooled) **is INVALIDATED (§4.4a)**: it was computed against the wrong (crystal, not
ESMFold-predicted) protein file. A hybrid recomputation against the correct protein file now gives
a valid figure — the top-1 pose recovers 9.23% of reference protein–ligand interactions pooled
across the matched n=82 subset (47/509), against a rank1–10 oracle upper bound of 12.57% (64/509).
A recomputed correlation between confidence and this corrected recovery rate finds no statistically
significant monotonic relationship (Spearman rho = 0.046, two-sided p = 0.682, n=81) — a limited,
non-causal null result, not evidence that confidence and chemical correctness are unrelated in any
deeper sense.

The oracle-headroom gate (§3.2 Step 0, §4.5) that determines whether Phase 2 is worth building has
now been run, and it delivers two different verdicts depending on which correctness criterion is
used. On RMSD, headroom is substantial (14/122 to 22/122, +6.56 points): a better-RMSD pose often
already sits, unchosen, in DiffDock-L's own candidate pool, which is a selection failure a learned
rescorer can plausibly fix. On PLIF recovery, headroom is small (9.23% to 12.57%, +3.34 points):
even a perfect oracle over the same 10 candidates recovers little more chemical correctness than
confidence already does, which is a sampling limitation no reranking method can fix. We take the
RMSD-side result alone as sufficient grounds to proceed to Phase 2, and we are explicit that this
draft does not claim, and will not claim without new evidence, that Interaction-Aware Rescoring
materially improves PLIF-based chemical correctness — any such improvement the trained model shows
would be a secondary, exploratory finding, not the paper's central contribution. Two non-learned
rerankers run on the same candidate pool — B1 (random-in-candidates, expected 11.12%) and B3
(GNINA/Vina affinity reranking, 12.30%) — both land within about a percentage point of confidence's
own 11.48% (§3.2, §4.5), indicating that neither randomness nor classical scoring exploits the
RMSD-side headroom on its own; this sets a modest bar the proposed learned rescorer must clear.
Whether the proposed rescoring model in fact improves on the RMSD-based baseline by a margin beyond
this band — and whether any improvement traces specifically to the PLIF-derived features rather
than to cheaper signals such as ensemble consistency — is not yet known and remains the explicit
subject of the pre-registered, not-yet-executed training and evaluation protocol in §3.2.

---

## Code and Data Availability

Code, configuration, and result tables for the measured Phase 1 results are available at
`diffdock-interaction-rescoring`. This draft's §4.3–4.4 numbers match the CSVs and execution log
in the repository, but not the repository README's failure-cause narrative: as of this draft, the
README still attributes all 11 runtime failures to a single group-aggregation bug, which §4.3 and
§4.6(f) below identify as incorrect (the primary execution log shows 7 SVD ill-conditioning
failures and 4 RDKit/exception-handling failures instead). This is an outdated-documentation issue
in the public repository, not a discrepancy in the numbers reported here, and has not yet been
corrected outside this manuscript. Result files, including the main evaluation table
(`master_eval_table_n122_with_plif.csv`), ECE/reliability-diagram data (`ece_reliability_bins_n91.csv`,
`reliability_diagram_n91.png`), and PLIF recovery results (`plif_recovery_results.csv`), are under
`results/dockgen_pilot/`, with reproduction scripts under `results/dockgen_pilot/eval_scripts/`.
**`plif_recovery_results.csv` and the PLIF columns of `master_eval_table_n122_with_plif.csv` are
invalidated (§4.4a):** `compute_plif.py` scores the predicted ligand pose against the crystal
protein file rather than the ESMFold-predicted protein file DiffDock-L actually used at inference
time. These files are retained in the repository as a record, not as a source of valid PLIF
numbers. **The valid replacement PLIF figures reported in §4.4/§4.4a (9.23% baseline, 12.57%
oracle) come from a separate hybrid pipeline**: `hybrid_plif_baseline_matched82.csv` and
`hybrid_plif_oracle_matched82.csv` (scripts `hybrid_plif_baseline.py`, `hybrid_plif_oracle.py`),
under `results/dockgen_pilot_eval/` — not yet cross-referenced against the public repository's
directory layout at the time of this draft; confirm the path before final submission. **The
confidence-vs-PLIF-recovery correlation against these hybrid values has since been recomputed
(§4.4a, §4.6(h)):** `results/dockgen_pilot_eval/hybrid_plif_confidence_spearman.json`, script
`eval_scripts/correlate_hybrid_plif.py`.
Reproducing these numbers from scratch currently requires manual work beyond cloning the
repository: `eval_scripts/*.py` hardcode absolute paths from the project's HPC compute environment
and will not run unmodified elsewhere, and two of the three scripts require input files not yet
tracked in the repository — `build_master_table.py` needs `diffdock_dockgen_inputs.csv`, and
`compute_plif.py` needs `data/dockgen_set/`. The tracked CSV outputs in `results/dockgen_pilot/`
can be used directly without rerunning these scripts. DockGen-E is redistributed by PoseBench
(BioinfoMachineLearning/PoseBench) and originates from Corso et al. (arXiv:2402.18396). The
oracle-headroom gate and the two non-learned comparators B1 and B3 (§4.5) have been executed —
result files `random_baseline_rmsd.json` and `gnina_b3_selected.csv`/`gnina_b3_summary.json` under
`results/dockgen_pilot_eval/` — but no Phase 2 learned rescoring model (M1/M1-abl) code or trained
artifact exists yet; this section will be updated once that model is trained and evaluated.
**M1's originally planned training data (a 1,500-complex PDBBind subset, seed=42) is INVALIDATED
(2026-07-23/24 erratum above): all 1,500 complexes were found to be contained in DiffDock-L's own
training split (`timesplit_no_lig_overlap_train`), making them unusable as an out-of-distribution
training source for M1.** The revised plan draws M1/M1-abl training data from DiffDock-L's own
held-out validation split (`timesplit_val_filter`, 585 complexes) instead, with DiffDock-L's test
split (363 complexes) reserved for a possible future evaluation of M1 rather than reused as
training data; GPU docking of the 585-complex split was in progress, not complete, as of this
draft. The Zenodo substitution disclosed in §3.2 (record 6408497, confirmed deleted, replaced by
7014096) was made for the now-abandoned 1,500-complex subset; whether it applies unchanged to the
585-complex plan has not been confirmed and must be re-checked before that data is released.

---

## References

(Working list; author-year inline style used in text above. Assembled from vetted entries in
`wiki/papers/` — see each entry there for the full ingested summary. Not yet converted to a
formal bibliography format; venue/arXiv identifiers below are taken directly from those source
notes and have not been independently re-verified in this pass.)

- Corso, G., Stärk, H., Jing, B., Barzilay, R., Jaakkola, T. *DiffDock: Diffusion Steps, Twists,
  and Turns for Molecular Docking*. ICLR 2023. arXiv:2210.01776.
- Ketata, M.A., Laue, C., Mammadov, R., Stärk, H., Wu, M., Corso, G., Marquet, C., Barzilay, R.,
  Jaakkola, T.S. *DiffDock-PP: Rigid Protein-Protein Docking with Diffusion Models*. ICLR 2023
  MLDD Workshop. arXiv:2304.03889.
- Jiang, Y., Li, X., Zhang, Y., Han, J., Xu, Y., et al. *PoseX: AI Defeats Physics-based Methods
  on Protein Ligand Cross-Docking*. ICLR 2026. arXiv:2505.01700.
- Morehead, A., Cheng, J. *FlowDock: Geometric Flow Matching for Generative Protein-Ligand
  Docking and Affinity Prediction*. arXiv:2412.10966.
- Morehead, A., Giri, N., Liu, J., Neupane, P., Cheng, J. *Assessing the Potential of Deep
  Learning for Protein-Ligand Docking*. Nature Machine Intelligence 8, 32–41 (2026).
  doi:10.1038/s42256-025-01160-1. [PoseBench; DockGen-E curation]
- Corso, G. et al. *DockGen benchmark*. arXiv:2402.18396 (2024). [original DockGen dataset; also
  the source of the Confidence Bootstrapping / DiffDock-S DockGen-clusters figure cited in §2
  (9.8%→24.0%, Table 1, Fig. 4-D) — independently verified against the source PDF (PMC10925391)
  on 2026-07-22]
- Liu, Tang, Niu, Wang. *A Comparative Study of Deep Learning and Classical Modeling Approaches
  for Protein-Ligand Binding Pose and Affinity Prediction in Coronavirus Main Proteases*.
  J. Chem. Inf. Model. 2026, 66, 731–743.
- Errington, D., Schneider, C., Bouysset, C., Dreyer, F.A. *Assessing interaction recovery of
  predicted protein-ligand poses*. arXiv:2409.20227 (2024).
- Abramson, J. et al. *Accurate structure prediction of biomolecular interactions with
  AlphaFold 3*. Nature 630, 493–500 (2024). doi:10.1038/s41586-024-07487-w.
- Anonymous. *ACER: Towards Generalizable Protein-ligand Co-folding*. ICML 2026 Workshop on
  Generative and Agentic AI for Biology (submission; authorship anonymized in source).
- Khiari, S., Mahmoud, A.H., Lill, M.A. *AgenticPosesRanker: An Agentic AI Framework for
  Physically Grounded Ranking of Protein–Ligand Docking Poses*. University of Basel (2026;
  venue not specified in the source document available to this project).
- Abo-Dahab, Y., Xiang, X., Chun, J., Zhao, L. *Benchmarking Single-Pose Docking, Consensus
  Rescoring, and Supervised ML on the LIT-PCBA Library: A Critical Evaluation of DiffDock,
  AutoDock-GPU, GNINA, and DiffDock-NMDN*. UCSF AICD3 capstone project, 2026.
- Cao, S., Wu, H., Wang, J.B., Yuan, Y., Misir, M. *MC-GNNAS-Dock: Multi-criteria GNN-based
  Algorithm Selection for Molecular Docking*. arXiv:2509.26377 (2025).
- Buccheri, R., Rescifina, A. *High-Throughput, High-Quality: Benchmarking GNINA and AutoDock
  Vina for Precision Virtual Screening Workflow*. Molecules 2025, 30, 3361.
- Trott, O., Olson, A.J. *AutoDock Vina: improving the speed and accuracy of docking with a new
  scoring function, efficient optimization and multithreading*. J. Comput. Chem. 2010, 31(2),
  455–461. doi:10.1002/jcc.21334.
- Vu, T.N.L., Fooladi, H., Kirchmair, J. *Integrating Machine Learning-Based Pose Sampling with
  Established Scoring Functions for Virtual Screening*. J. Chem. Inf. Model. 2025, 65, 4833–4843.
  doi:10.1021/acs.jcim.5c00380.
- *PocketVina*. arXiv:2506.20043. [cited only for the fixed-denominator evaluation convention
  used in §4.3; full bibliographic detail not available in this project's source material and not
  invented here]
