---
type: thesis
status: draft
created: 2026-07-20
updated: 2026-07-20
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
failures counted as non-success), expected calibration error (ECE) is 0.203, and pooled PLIF
interaction recovery is 15.47% (138/892 reference interactions, computed over 80 of the 91
RMSD-scored complexes). We test whether confidence tracks PLIF recovery and find no
statistically significant rank correlation (Spearman rho = -0.149, n=78, t(76) = -1.31, not
significant at alpha=0.05, two-tailed). Taken together, these numbers show that top-1 success
is low, calibration is poor, and confidence shows no statistically significant relationship to
whether the selected pose reproduces the correct protein–ligand interactions (at this sample
size); whether this reflects a
selection failure — the correct pose is sampled but not chosen, which rescoring could fix — or
a sampling failure — the correct pose is never generated, which rescoring cannot fix — is not
yet established (§4.5). Building on this diagnosis, we describe (design only; not yet executed) an Interaction-Aware
Rescoring model that reranks DiffDock-L's already-sampled candidate poses using
complex-invariant ProLIF interaction-type counts, pharmacophore geometry, and ensemble
consistency, trained on PDBBind and evaluated, without retraining any part of DiffDock-L, on
the same 122-complex cross-docking set. We report the measured diagnosis in full and the
correction as a pre-registered protocol, including a mandatory oracle-headroom gate that must
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
benchmark (122 complexes with pockets dissimilar to PDBBind), and reports — for the first time
on this benchmark — PLIF interaction recovery alongside RMSD-based top-1 accuracy. We also test whether the
confidence score itself tracks PLIF recovery, the way it is trained to track RMSD, and find no
statistically significant rank correlation (Spearman rho = -0.149, n=78, t(76) = -1.31; §3.1,
§4.4). **These Phase 1 measurements are complete** and are the primary reported result of this
draft: on the 91 of 122 complexes with RMSD-scorable output, top-1 RMSD < 2 Å success is
11.48% (14/122), ECE is 0.203, pooled PLIF recovery is 15.47% (over 80 of the 91 scored
complexes), and confidence shows no significant rank correlation with PLIF recovery (§4.4).
Phase 2, building on that diagnosis,
proposes an Interaction-Aware Rescoring model that reranks DiffDock-L's already-sampled candidate
poses using PLIF-derived and pharmacophore features rather than confidence alone. **Phase 2 has
been designed in detail — including a mandatory pre-registered gate that checks whether the
candidate pose pool even contains a better answer than confidence currently selects — but has
not been executed.** We report the Phase 1 diagnosis as a measured result and the Phase 2
correction as a specified, not-yet-run protocol, and we are explicit throughout about which
numbers are measurements and which are targets.

Contributions: (i) the first reported calibration analysis (ECE) of DiffDock-L's raw confidence
score, alongside a first-reported PLIF interaction-recovery rate and a direct test of whether
confidence tracks that recovery — it does not, at a statistically significant level (Spearman
rho = -0.149, n=78, t(76) = -1.31) — on a leakage-controlled cross-docking benchmark
(DockGen-E, n=122), including an honest accounting of a substantial fraction of complexes (31/122)
for which the pipeline produces no scorable output at all; (ii) a fully specified,
not-yet-executed Interaction-Aware Rescoring protocol that reranks DiffDock-L's existing candidate
poses using complex-invariant interaction and pharmacophore features, with an oracle-headroom
gate designed to prevent the project from training a model where no improvement is possible; and
(iii) an explicit statement of what remains unmeasured — stratified (pocket-similarity)
calibration, an in-distribution ECE anchor, and every Phase 2 accuracy number — so that this draft
does not overstate what has actually been shown.

---

## 2. Related Work

**Diffusion docking and its confidence model.** DiffDock (Corso et al., ICLR 2023) recast blind
docking as generative sampling over translation, rotation, and torsion, pairing an SE(3)-
equivariant score network with a separately trained confidence model that predicts whether a
pose meets the 2 Å RMSD criterion. On in-distribution PDBBind time-splits this confidence score
attains Spearman correlation 0.68 with RMSD and lifts selective accuracy from 38% to 83% under
aggressive abstention. DiffDock-L subsequently improved generalization through confidence-bootstrapping, reported in
its source paper (Corso et al., arXiv:2402.18396, which also introduced DockGen) to raise DockGen
accuracy from roughly 7% to 23%. Unlike the other claims in this section, this specific figure was
not independently ingested into this project's literature-review corpus (`wiki/papers/`) — the
2402.18396 PDF is cited elsewhere in this draft only as the origin of the DockGen dataset, not as
a fully reviewed source — so it carries a lower evidence tier than neighboring claims and should
be re-checked against the source paper before this draft is finalized.
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
capstone 2026) finds DiffDock confidence performing at or below classical AutoDock in a
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
**The aggregate (non-stratified) ECE, the aggregate PLIF interaction-recovery rate, and the
confidence-vs-PLIF-recovery rank correlation have all been computed** (§4): the correlation is
not statistically significant (Spearman rho = -0.149, n=78, t(76) = -1.31). Stratified
reliability diagrams, AURC, and the classical/recalibration comparators remain designed but
unexecuted.

### 3.2 Phase 2 — Interaction-Aware Rescoring (design only; not executed)

Phase 2 is defined as a reranking problem, not a pose-generation problem: DiffDock-L already
samples and confidence-ranks multiple candidate poses per complex, and the project's HPC runs
retain the top-10 ranked poses per complex from the Phase 1 inference. Rather than resample,
Phase 2 reranks within this existing candidate pool of 10 poses per complex, which requires no
additional GPU inference for the evaluation benchmark and keeps the comparison to raw confidence
on an identical candidate set.

**Step 0 — oracle-headroom gate (mandatory, must run before any model is trained).** For every
complex, we compute per-rank RMSD and per-rank PLIF recovery across all 10 candidates (this
per-rank scoring itself has not yet been run; see §4). Three quantities are then compared, all on
the same 122-complex denominator: (B0) the existing raw-confidence baseline — rank-1 top-1
success, already measured at 14/122; (B2) an oracle upper bound — success if any of the 10
candidates is within 2 Å, defining the best any reranking method could possibly achieve; and (B1)
a random-choice lower sanity bound — expected success from picking one candidate at random. The
pre-registered decision rule is: if oracle ≈ baseline (headroom below roughly 5 percentage
points, i.e., fewer than about 6 complexes), rescoring is abandoned as a direction, because the
correct pose is not present in the candidate pool for reranking to find — a limitation to report,
not a rescoring failure, with the implied next step being wider pose sampling (larger N) rather
than better reranking. If headroom clears that bar, rescoring proceeds. The same oracle
computation is repeated for PLIF recovery: pooled PLIF recovery is itself low (15.47%, §4.4),
and prior work has found RMSD-based correctness to carry no measured relationship to PLIF
recovery in general (Errington et al., §2). This project's own measurement is consistent with
that pattern: DiffDock-L's confidence score shows no statistically significant rank correlation
with PLIF recovery (Spearman rho = -0.149, n=78, t(76) = -1.31; §4.4). On that basis a
PLIF-recovery headroom exceeding the RMSD headroom is plausible, but the oracle computation
itself has not been run, so the prediction remains a hypothesis, not a finding.

**Comparators, conditional on passing Step 0.** All comparators rerank within the same fixed
10-candidate pool and are evaluated on the identical 122-complex denominator used for Phase 1:
B0 (raw confidence, rank-1 — the existing baseline), B1 (random-in-candidates), B2 (oracle,
upper bound, not achievable by any method), B3 (classical rescoring of the 10 candidates by Vina
score, primary, and GNINA CNN score, secondary — a non-learned, non-PLIF contrast), M1 (the
proposed PLIF-aware learned rescorer), and M1-abl (an ablation of M1 with PLIF features removed,
isolating whether any improvement comes specifically from the interaction signal or from the
other features alone).

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
Waals radii for uncommon metal centers, and one residue-identity mismatch; §4.4). The same
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
runs, and one to be spent only after Step 0 passes. Supervision targets are RMSD < 2 Å (primary)
and PLIF recovery (secondary). No component of DiffDock-L itself — score network or confidence
network — is retrained; only the reranking step is learned.

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

### 4.4 Results (measured, 2026-07-19)

| Metric | Value | Denominator / basis |
|---|---|---|
| Top-1 RMSD < 2 Å success rate | **14/122 = 11.48%** | fixed denominator 122 (all complexes; 11 runtime failures and 20 unscored complexes counted as non-success) |
| — reference figure | 15.38% | 91 RMSD-scored complexes only (not the primary denominator) |
| — reference figure | 12.61% | 111 complexes with any usable inference output (not the primary denominator; rejected as a reporting basis, see §4.3) |
| Expected calibration error (ECE) | **0.203** | 91 scored complexes; confidence = sigmoid(raw logit) as a P(RMSD < 2 Å) estimate, consistent with DiffDock's BCE-with-logits training objective; the 20 unscored complexes are excluded from this calculation rather than treated as incorrect |
| PLIF interaction recovery (pooled) | **15.47%** (138/892 reference interactions) | pooled across 80 of the 91 scored complexes; per-complex mean 17.3%, median 0% — a heavily right-skewed distribution, most complexes recovering no reference interaction at all |
| Confidence–PLIF recovery rank correlation | **Spearman rho = -0.149** (not significant) | n=78 (of the 80 PLIF-valid complexes, 2 lack a `confidence_rank1` value); t(76) = -1.31 vs. two-tailed critical value ≈1.99 at alpha=0.05, df=76 |

The PLIF metric's own denominator is narrower than the RMSD/ECE metrics' 91: ProLIF fingerprint
computation itself fails on 11 of the 91 RMSD-scored complexes (verified directly against
`plif_recovery_results.csv`, 2026-07-20) — 7 from a numeric overflow in interaction-fingerprint
indexing (`OverflowError: Python integer ... out of bounds for uint32`), 3 from missing van der
Waals radii for metal-coordination atoms (Fe, Mo) in the interaction preset used, and 1 from a
residue-identity mismatch between the predicted and reference structures. These 11 are excluded
from the PLIF pooled/mean/median figures above (not imputed as zero recovery), leaving n=80 as the
PLIF metric's actual complex-level denominator; the 892 reference-interaction count is the sum of
per-complex reference-interaction counts over those same 80 complexes. This denominator distinction
was not previously documented in this project's session logs and should be carried into any future
reporting of this number.

**Confidence-vs-PLIF-recovery relationship.** We test whether the confidence score tracks PLIF
interaction recovery, the same relationship it is trained to have with RMSD. Restricting to the
78 complexes with both a `confidence_rank1` value and a PLIF `recovery` value (2 of the 80
PLIF-valid complexes lack a confidence score in the master table), the Spearman rank correlation
between confidence and recovery is rho = -0.149. Using the standard t-approximation for the
significance of a Spearman correlation, t(76) = rho·sqrt((n-2)/(1-rho²)) = -1.31, which falls
short of the two-tailed critical value of approximately 1.99 at df=76, alpha=0.05: confidence and
PLIF recovery show no statistically significant rank correlation. As an exploratory comparison
outside the scope of this test, the rank correlation between confidence and binary RMSD < 2 Å
success (n=91 scored complexes) is approximately +0.37, in the expected direction; this
comparison was not itself subjected to a significance test and is reported only for context, not
as a confirmed finding.

These are the only measured Phase 1 numbers in this draft. Stratified (pocket-similarity)
reliability diagrams, the PDBBind in-distribution ECE anchor, AURC/risk–coverage, and the
base-DiffDock/FlowDock/classical-scoring comparators specified in §3.1 have not been computed.
Consequently, this draft can report that DiffDock-L's confidence score is, in absolute terms,
poorly calibrated on this cross-docking benchmark, only weakly related to top-1 correctness, and
carries no statistically significant rank relationship with PLIF interaction recovery — but it
cannot yet report whether that miscalibration is *directional* (i.e., worse specifically
under distribution shift relative to an in-distribution anchor, as prior rank-correlation and
accuracy-degradation evidence would predict) or *stratified* (concentrated in low pocket-similarity
complexes), because the comparison points needed to establish either claim have not been measured
in this project. We flag both as open, not as findings.

An earlier 65-complex pilot on an overlapping but not identical set reported success rate 18.5%,
ECE 0.53, and PLIF recovery 6.0%. Its computation scripts were not preserved, so this draft treats
those figures as unverifiable background only — not as a comparison point — and adopts the n=122
result above as the project's sole reported baseline.

### 4.5 Phase 2 status

No Phase 2 number has been computed. The oracle-headroom gate (§3.2, Step 0) — the first required
step before any rescoring model is trained — has not been run: per-rank (rank 2 through 10) RMSD
and PLIF recovery have not yet been computed for the candidate pool, so neither the oracle upper
bound nor the resulting headroom is known. Until that gate is evaluated, it is not established
that rescoring can improve on the 14/122 baseline at all; we treat this as the single most
consequential open question for the project's next step, ahead of building any model.

### 4.6 Limitations

(a) The Phase 1 protocol as designed includes five comparators and a stratified analysis; only
one comparator (DiffDock-L on DockGen-E, aggregate statistics) has been executed. Claims of
directional or stratified miscalibration are not yet supported by measurement. (b) 20 of 122
DockGen-E complexes (16%) cannot be RMSD-scored under the current pipeline because of non-standard
ligand chemistry (peptide-like ligands, repeated glycine, metal ions) — a structural limitation of
the DiffDock-L/PoseBench pipeline as deployed here, not resolved without code-level changes, and a
source of missing data rather than measured failure for those complexes' correctness. (c) The
per-complex PLIF-recovery distribution is heavily skewed (median 0%), which will need to be
accounted for in how Phase 2 defines its PLIF-recovery training target rather than treated as a
simple regression or balanced-classification signal. (d) DockGen-E (n=122, 91 scored) gives low
statistical power; any Phase 2 comparison will need the PoseX-CD extension (n=1,312) before a
significance claim is defensible, per the pre-registered plan in §3.2. (e) Comparator confidence
scores (DiffDock-L's learned probability vs. Vina's empirical scoring function vs. a trained
rescorer's output) are not on a common semantic scale; where a future draft reports ECE for
multiple comparators, it must also report AURC/risk–coverage as a semantics-free alternative,
per the design in §3.1. (f) The documentation discrepancy noted in §4.3 regarding the cause of
the 11 runtime failures has been resolved in favor of the execution-log breakdown (SVD
ill-conditioning ×7, RDKit/exception-handling ×4); the project's own public README still carries
the outdated single-cause wording and needs a corrective update outside this manuscript. (g) The
PLIF pooled/mean/median recovery figures in §4.4 are computed over 80 of the 91 RMSD-scored
complexes, not all 91: ProLIF fingerprint computation itself fails on the remaining 11 (7
interaction-index overflow, 3 missing metal van der Waals radii, 1 residue-identity mismatch).
These 11 are excluded from the PLIF figures, not imputed as zero recovery, and the same failure
modes are a coverage risk for Phase 2 feature extraction (§3.2). (h) The confidence-vs-PLIF-
recovery correlation (§4.4) is computed on n=78, not the full 80 PLIF-valid complexes, because 2
complexes with a valid PLIF recovery value lack a `confidence_rank1` value in the master
evaluation table; the cause of that gap has not been separately diagnosed. With only 78 paired
observations, the null result (rho = -0.149, not significant) is likely underpowered to rule out
anything smaller than a moderate correlation; it should be read as "no significant correlation
detected at this sample size," not as strong evidence that the true relationship is zero.

---

## 5. Conclusion (interim)

This draft reports a measured diagnosis and a specified but unexecuted correction. On the
DockGen-E cross-docking benchmark, DiffDock-L's top-1 pose is correct (RMSD < 2 Å) for 14 of 122
complexes (11.48%), its confidence score has ECE 0.203 on the 91 complexes where correctness could
be scored, and its top-1 pose recovers only 15.47% of reference protein–ligand interactions
pooled across complexes, with a per-complex median of 0%. Whether an Interaction-Aware Rescoring
model can improve on this — and whether any improvement traces specifically to the PLIF features
rather than to cheaper signals such as ensemble consistency — is not yet known and is the explicit
subject of the pre-registered, not-yet-executed protocol in §3.2. The single next measurement
that determines whether Phase 2 is worth building at all is the oracle-headroom gate (§3.2,
§4.5): whether the correct pose exists anywhere in DiffDock-L's already-sampled candidate pool.

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
Reproducing these numbers from scratch currently requires manual work beyond cloning the
repository: `eval_scripts/*.py` hardcode absolute paths from the project's HPC compute environment
and will not run unmodified elsewhere, and two of the three scripts require input files not yet
tracked in the repository — `build_master_table.py` needs `diffdock_dockgen_inputs.csv`, and
`compute_plif.py` needs `data/dockgen_set/`. The tracked CSV outputs in `results/dockgen_pilot/`
can be used directly without rerunning these scripts. DockGen-E is redistributed by PoseBench
(BioinfoMachineLearning/PoseBench) and originates from Corso et al. (arXiv:2402.18396). No Phase 2
code or trained model exists yet; this section will be updated once Phase 2 is executed.

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
  the source of the confidence-bootstrapping DockGen-accuracy figure cited in §2 — see the caveat
  there, as this paper was not fully ingested into `wiki/papers/`]
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
