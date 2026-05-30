# REAP

**REAP**: **R**obust **E**nergy **A**ssessment and **P**lanning

REAP is a decision-analytic framework for robust and resilient energy planning
under uncertainty. It pairs a capacity expansion model ([PREP-SHOT](https://prep-next.github.io/PREP-SHOT))
with a scenario-design layer (factorial + Latin-Hypercube sampling) to
quantify how candidate plans perform across thousands of plausible futures.

A typical REAP study has three stages, covered by this repository:

1. **Design** the scenarios (factorial + LHS over uncertain drivers).
2. **Generate** one input set per scenario.
3. **Solve** each scenario with PREP-SHOT.

Downstream aggregation of the netCDF results into robustness metrics is
left to the analyst — REAP is agnostic to the post-processing toolchain.

This repository contains the PREP-SHOT capacity expansion model, the
scenario-generation pipeline, and runners for single-scenario and
MPI-parallel batch execution.

## Citation

This repository accompanies the manuscript:

> Shuyue Yan, Zhanwei Liu, and Xiaogang He.
> **Singapore's pathways to a net-zero power sector in 2050** (Under Review).
> Department of Civil and Environmental Engineering, National University of
> Singapore.

---

## Table of contents

- [Installation](#installation)
- [Project layout](#project-layout)
- [Quick start](#quick-start)
- [Workflow](#workflow)
  - [1. Design scenarios](#1-design-scenarios)
  - [2. Generate inputs](#2-generate-inputs)
  - [3. Run scenarios](#3-run-scenarios)
    - [Single scenario](#single-scenario)
    - [MPI batch](#mpi-batch)
- [References](#references)
- [License](#license)

---

## Installation

REAP targets Python 3.9+. Install via conda using the environment file:

```bash
conda env create -f environment.yml
conda activate prep-shot
```

The default solver is [Gurobi](https://www.gurobi.com/) (a license is
required; free academic licenses are available). To use a different solver,
edit `config.json` and set `solver_parameters.solver` to any Pyomo-
compatible backend (`highs`, `cbc`, [`cuopt`](https://developer.nvidia.com/cuopt)
for GPU, …) and install it separately.

For MPI batches, also install `mpi4py` (`pip install mpi4py`) and an MPI
runtime such as Open MPI.

## Project layout

```
prepshot/                          Model package (data loading, model, solver, rules)
data/                              Source data (templates, sample input, scenario design)
├── default_parameters/            Parameter Excel files copied verbatim into every scenario
├── full_factorial_parameters/     Pre-baked variants picked by factorial level (e.g. demand_0.028.xlsx)
├── lhs_parameters/                Templates whose cells get filled with each scenario's LHS sample
├── full_factorial_template_prep_shot.csv               Factorial-level definitions
├── exp_design_FF_LHS_template_prep_shot_20251024.csv   Per-variable LHS bounds + flags
└── experimental_design.csv         Generated design table — one row per scenario
config.json                        Solver + general-parameter configuration
params.json                        Mapping from internal names to Excel input files
environment.yml                    Conda environment specification
generate_scenarios.R               Step 1 — builds the factorial × LHS design table
generate_inputs.py                 Step 2 — builds per-scenario input folders from templates
run.py                             Step 3 — single-scenario solver
run_batch.py                       Step 3 — MPI batch solver
```

## Quick start

```bash
# 1. Activate environment
conda env create -f environment.yml
conda activate prep-shot

# 2. Generate the per-scenario input folders under generated_inputs/
Rscript generate_scenarios.R    # writes data/experimental_design.csv (needs install.packages("lhs"))
python generate_inputs.py       # writes generated_inputs/input_s1_…/, etc.

# 3. Solve one scenario
python run.py
# → results land in output/year.nc
```

`run.py` defaults to solving
`generated_inputs/input_s1_diversified_0.028/`. Override with `-i <path>`
to solve a different scenario, or set `input_folder` in `config.json`. For
multi-scenario sweeps see [Workflow](#workflow).

## Workflow

```
  Step 1 ─ Design scenarios
  ─────────────────────────────────────────────────
      data/full_factorial_template_prep_shot.csv
      data/exp_design_FF_LHS_template_prep_shot_*.csv
                          │
                          ▼
                generate_scenarios.R
                          │
                          ▼
            data/experimental_design.csv

  Step 2 ─ Generate inputs
  ─────────────────────────────────────────────────
      data/experimental_design.csv
      data/default_parameters/
      data/full_factorial_parameters/
      data/lhs_parameters/
                          │
                          ▼
                generate_inputs.py
                          │
                          ▼
            generated_inputs/input_s1_…/
            generated_inputs/input_s2_…/
                          ⋮

  Step 3 ─ Solve
  ─────────────────────────────────────────────────
                          │
                          ▼
                run.py  /  run_batch.py
                          │
                          ▼
        output/year.nc  /  output_batch/output_*/year.nc
```

### 1. Design scenarios

REAP scenarios are produced from a factorial design (discrete settings such
as technology portfolios) crossed with a Latin-Hypercube sample of continuous
uncertainties (fuel prices, carbon limits, reserve margins, …).

The design table is generated with `generate_scenarios.R`. Two template
files parameterise it:

- `full_factorial_template_prep_shot.csv` — discrete factorial levels (e.g.
  `outlook` ∈ {diversified, hydrogen, import_with_australia,
  import_without_australia}, `demand` growth rate, …).
- `exp_design_FF_LHS_template_prep_shot_20251024.csv` — for each remaining
  variable, its default, its LHS lower/upper bounds, and whether it varies in
  the factorial or LHS dimension.

The script requires R and the `lhs` package (`install.packages("lhs")` or
`conda install -c conda-forge r-lhs`). The constants at the top of
`generate_scenarios.R` default to reading templates from `data/`; edit them
only if your templates live elsewhere or you want a different LHS size:

```r
exp_dir          <- "data"
design_info_file <- file.path(exp_dir, "exp_design_FF_LHS_template_prep_shot_20251024.csv")
export_name      <- "experimental_design.csv"
n_points         <- 1000     # LHS sample size; total scenarios = factorial × n_points
```

Run from the repo root:

```bash
Rscript generate_scenarios.R
```

This produces `data/experimental_design.csv` (factorial × LHS). A pre-built
example with 1,000 LHS points × the factorial grid (12,000 rows) is already
checked in if you want to skip this step.

### 2. Generate inputs

For every row of the design table, `generate_inputs.py` composes a
per-scenario input folder under `generated_inputs/` by combining three
sources:

- `data/default_parameters/` — copied verbatim into every scenario
- `data/full_factorial_parameters/` — one variant picked per factorial level
  (e.g. `demand_0.028.xlsx` → `demand.xlsx`)
- `data/lhs_parameters/` — templates whose target cells are overwritten with
  the scenario's LHS sample values

```bash
python generate_inputs.py
# → generated_inputs/input_s0_diversified_0.028/
#   generated_inputs/input_s1_diversified_0.028/
#   ...
```

Each folder contains one complete PREP-SHOT input set (one Excel per
parameter).

### 3. Run scenarios

#### Single scenario

`run.py` solves a single scenario folder and writes `output/year.nc`. The
default input folder is set in `config.json` (`general_parameters.input_folder`,
shipped as `generated_inputs/input_s1_diversified_0.028`); override
per-invocation with `-i <path>`. Other CLI flags map onto parameter file
suffixes — run `python run.py --help` for the full list.

#### MPI batch

`run_batch.py` iterates over `generated_inputs/` and shards scenarios across
MPI ranks. Each rank `r` of `N` solves scenarios where `i % N == r`,
skipping any whose `year.nc` is already on disk — so the batch is safely
resumable after a crash.

```bash
mpirun -n 4 python run_batch.py
```

Per-rank progress is written to `log/rank_<NNN>.log`.

## References

PREP-SHOT and the broader REAP modelling effort build on the following work:

- Liu, Z. & He, X. **Balancing-oriented hydropower operation makes the clean
  energy transition more affordable and simultaneously boosts water
  security.** *Nature Water* 1, 778–789 (2023).
  [doi:10.1038/s44221-023-00126-0](https://doi.org/10.1038/s44221-023-00126-0)

- Xu, B., Liu, Z., Yan, S., Schmitt, R. J. P. & He, X. **Strategizing
  renewable energy transitions to preserve sediment transport integrity.**
  *Nature Sustainability* (2025).
  [doi:10.1038/s41893-025-01626-5](https://doi.org/10.1038/s41893-025-01626-5)

- Xie, J., Liu, Z., Yan, S., Ziegler, A. D., Shi, X., Xu, B., Srinuansom, K.,
  Peng, X., Yoshimura, K. & He, X. **Variable renewable energy pathways in
  the Lower Mekong Basin under projected river flow extremes.**
  *Communications Earth & Environment* 6, 928 (2025).
  [doi:10.1038/s43247-025-02861-6](https://doi.org/10.1038/s43247-025-02861-6)

## License

See [LICENSE](LICENSE).
