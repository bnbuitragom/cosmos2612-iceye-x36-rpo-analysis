# Analysis of the Cosmos 2612 – ICEYE-X36 RPO from Public GP Data

Reproducible analysis of the October 2026 close approach between **Cosmos 2612** (NORAD 68762) and the
commercial SAR satellite **ICEYE-X36** (NORAD 59103), based only on the public general perturbations (GP)
element history from Space-Track.org and SGP4 propagation.

The analysis is posed as a hypothesis test: can the encounter be explained by natural orbital evolution, or did it
require manoeuvres, and by which object?

## Main results

- Time of closest approach (TCA): **18 October 2026, 06:33:14 UTC**. The separation was **below 0.79 km** (95th percentile
  of the empirical SGP4 error); the minimum distance cannot be resolved below TLE accuracy.
- Local relative velocity at TCA ≈ 0.08 m/s; the objects stayed continuously within 5 km for 41.4 h and within 1 km for 14.6 h.
- The null hypothesis (natural evolution) is rejected in all 18 parameter combinations tested. The encounter required
  manoeuvres by Cosmos 2612; no manoeuvres by ICEYE-X36 are needed to reproduce the observations.
- Identified sequence for Cosmos 2612: plane match (May), phasing drift from an orbit ≈47 km higher, orbit matching
  (10–12 October) ≈454 km behind the target, approach (15–16 October), proximity (16–18 October) and a manoeuvred
  retreat to ≈480 km (18–20 October), with a minimum cumulative Δv of 174–180 m/s.
- Kinematic data cannot establish whether the operation was cooperative, nor its purpose.

## Repository structure

```
├── cosmos2612_iceye-x36_proximity_analysis.ipynb   # complete analysis (all figures and tables)
├── src/download_data.py                             # downloads the GP history from Space-Track
├── data/                                            # empty: the downloaded CSV is written here (not versioned)
├── outputs/                                         # figures (PNG; vector PDF in outputs/pdf) and derived result tables
├── requirements.txt
└── LICENSE                                          # MIT
```

## Data availability

> **Note:** Due to Space-Track.org User Agreement restrictions regarding data redistribution, raw TLE datasets are not
> stored directly in this repository. To reproduce the analysis, please register a free account at
> [Space-Track.org](https://www.space-track.org), set your credentials as environment variables, and run
> `python src/download_data.py` to fetch the required ephemerides automatically.

The script queries the `gp_history` class for both objects with epochs between 1 April and 28 October 2026. By default it
only requests element sets created before 2026-10-27 10:15 UTC, so that the dataset matches the one used in the analysis
(1408 records before removing duplicate epochs). Use `--created-before none` to fetch all element sets currently available.

The files in `outputs/` contain only derived results (distances, velocities, detected manoeuvres, test statistics), not
raw element sets.

## How to reproduce

```bash
git clone https://github.com/bnbuitragom/cosmos2612-iceye-x36-rpo-analysis.git
cd cosmos2612-iceye-x36-rpo-analysis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export SPACETRACK_USER="your_email"
export SPACETRACK_PASSWORD="your_password"
python src/download_data.py

jupyter notebook cosmos2612_iceye-x36_proximity_analysis.ipynb
```

Run the notebook from the repository root (it reads `data/tle_gp_history_59103_68762.csv` and writes to `outputs/`).
It was executed with Python 3.11 and `sgp4` 2.27.

## Method in brief

1. Mean elements and SGP4 propagation (TEME frame, 60 s sampling, causal TLE selection).
2. Empirical SGP4 prediction error (95th percentile) as a function of propagation time, measured for each object over a
   manoeuvre-free reference period (before 1 September 2026).
3. Manoeuvre detection with robust z-scores (median/MAD) on changes in semi-major axis, inclination and propagation
   residual, applied identically to both objects; impulsive Δv lower bounds.
4. Relative motion in the local RIC frame of ICEYE-X36 and closest-approach refinement at 1 s.
5. Hypothesis test with manoeuvre-free (ballistic) counterfactual propagations: need for manoeuvres (R1), direction of
   the effect (R3) and per-object attribution (R2).
6. Bias assessment: parameter sensitivity (K, proximity threshold, error percentile), negative controls and a
   synthetic-data check with known truth (natural passes and manoeuvre-induced approaches). The original
   and the revised decision rules are both kept in the notebook, and the revision is declared explicitly.

## License

The code is released under the MIT License (see `LICENSE`). The Space-Track data are not covered by this license and
remain subject to the Space-Track.org User Agreement.

## Author

Brayan Nicolas Buitrago Montenegro — PhD student in Sciences (Astronomy), Universidad Nacional de Colombia
· brbuitragom@unal.edu.co · ORCID [0009-0004-8742-171X](https://orcid.org/0009-0004-8742-171X)
