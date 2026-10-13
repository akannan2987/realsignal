[Phase 4 guide](../05-phase-4-exploration.md) · [Handbook](../HANDBOOK.md) · [Glossary](../GLOSSARY.md)

# Data-quality report

Written by `scripts/make_quality_report.py` from the warehouse. Don't edit it by hand: run the script again. Every number comes from a query on the marts, through `src/realsignal/exploration.py`, so a changed source or a changed choice in `dbt/dbt_project.yml` shows up here the next time the script runs. [`docs/05-phase-4-exploration.md`](../05-phase-4-exploration.md) explains each section and what it means for the models.

| What | Value |
|---|---|
| Warehouse | `data/warehouse/realsignal.duckdb`, 20 tables, 13,908 rows loaded |
| Source files' fingerprint | `0e6ad6442e90` (a checksum of the checksums the load log records for the archive's tables and the two journal workbooks) |
| Outcome | `pathogen_log10_cfu_per_g` (the dbt setting `outcome_measurement`) |
| Undecided (TBD) plants in the modelling table | 120 |
| Test plants | counted, values never read: sealed until Phase 5 |

## The plants

| Group | Plants | Used for modelling | Communities used |
|---|---|---|---|
| training | 544 | 531 | 134 |
| test (sealed) | 280 | 277 | 70 |
| between-round reference | 16 | 0 | 0 |
| no strains, infected | 84 | 0 | 0 |
| no strains, not infected | 24 | 0 | 0 |
| whole library | 12 | 0 | 0 |

## 1. The shape of the outcome

Training plants only: 531 plants in 134 communities, rounds Exp1 and Exp2. Picture: [`figures/outcome_shape.png`](../../figures/outcome_shape.png).

| Statistic | Value |
|---|---|
| Median | 6.97 |
| Middle half (first to third quartile) | 5.50 to 7.93 |
| Spread of the middle half (IQR) | 2.43 |
| Lowest and highest | 3.39 and 9.37 |
| Mean | 6.70 |
| Standard deviation | 1.44 |

A smoothed histogram (kernel density estimate) has two humps, near **4.91** and **7.81**, and its lowest point between them at **5.71**.

Back on the ordinary scale (pathogen per gram of leaf) the median plant holds 9.4 million and the mean is 102.1 million: on the log scale that mean is 8.01, higher than 77 % of the plants. The tenth of plants with the most pathogen hold 68 % of all the pathogen counted. The counts run from 2,472 to 2.4 billion per gram.

**Class balance.** How many training plants have at least this much less pathogen than the median of their own round's infected plants with no strains (that median: Exp1 9.00, Exp2 8.91).

| Reduction | Plants | Share | Exp1 | Exp2 |
|---|---|---|---|---|
| 1 log10 (10 times fewer) | 401 | 76 % | 78 % | 73 % |
| 2 log10 (100 times fewer) | 262 | 49 % | 51 % | 47 % |
| 3 log10 (1,000 times fewer) | 175 | 33 % | 33 % | 32 % |

Below the dip (5.71): 151 of 531 plants (28 %).

## 2. How much the rounds differ

The outcome per round for the plants that got the same treatment in more than one round. Controls and reference plants count unless marked FALSE. The reference communities' plants in the test round are test plants, so they stay sealed. The training rows are different communities in each round. Picture: [`figures/rounds_compared.png`](../../figures/rounds_compared.png).

| Group | Round | Plants | Median | Middle half |
|---|---|---|---|---|
| no strains, infected | Exp1 | 28 | 9.00 | 8.77 to 9.20 |
| no strains, infected | Exp2 | 28 | 8.91 | 8.73 to 9.23 |
| no strains, infected | Exp3 | 28 | 9.30 | 9.23 to 9.45 |
| whole library | Exp1 | 4 | 3.64 | 3.59 to 3.71 |
| whole library | Exp2 | 4 | 4.88 | 4.07 to 5.70 |
| whole library | Exp3 | 4 | 5.12 | 4.29 to 6.16 |
| Mix69 (SynCom-High) | Exp1 | 4 | 7.24 | 7.13 to 7.62 |
| Mix69 (SynCom-High) | Exp2 | 4 | 8.33 | 7.84 to 8.52 |
| Mix70 (SynCom-Low) | Exp1 | 4 | 4.51 | 4.48 to 4.77 |
| Mix70 (SynCom-Low) | Exp2 | 4 | 5.52 | 5.31 to 5.70 |
| training (different communities) | Exp1 | 263 | 6.94 | 5.61 to 7.88 |
| training (different communities) | Exp2 | 268 | 6.98 | 5.19 to 7.96 |

How far each median moved from the group's first round:

| Group | Rounds | Change |
|---|---|---|
| no strains, infected | Exp1 to Exp2 | -0.09 |
| no strains, infected | Exp1 to Exp3 | +0.30 |
| whole library | Exp1 to Exp2 | +1.24 |
| whole library | Exp1 to Exp3 | +1.49 |
| Mix69 (SynCom-High) | Exp1 to Exp2 | +1.10 |
| Mix70 (SynCom-Low) | Exp1 to Exp2 | +1.02 |
| training (different communities) | Exp1 to Exp2 | +0.04 |

Fresh weight per round (mg):

| Group | Round | Plants | Median | Middle half |
|---|---|---|---|---|
| no strains, not infected | Exp1 | 8 | 35.3 | 34.0 to 42.5 |
| no strains, not infected | Exp2 | 8 | 27.4 | 23.0 to 29.7 |
| no strains, not infected | Exp3 | 8 | 41.4 | 38.7 to 47.8 |
| no strains, infected | Exp1 | 28 | 18.4 | 13.8 to 22.6 |
| no strains, infected | Exp2 | 28 | 13.0 | 10.8 to 15.4 |
| no strains, infected | Exp3 | 28 | 12.7 | 9.9 to 16.2 |

**The authors' normalised values, worked out from the numbers.** Checked on every plant outside the test set; Phase 6 reads the authors' code and confirms or corrects this.

- `pathogen_log10_normalised` is the log10 count minus the median of the round's infected plants with no strains (Exp1 9.00, Exp2 8.91, Exp3 9.30): 655 of 655 plants match to the ninth decimal place.
- `fresh_weight_normalised` is every plant's weight divided by one number, 35.30 mg (680 plants checked). That's the median weight of the plants with neither strains nor pathogen in Exp1; the same median in each round is Exp1 35.30, Exp2 27.42, Exp3 41.35 mg, so the weights aren't adjusted round by round the way the pathogen counts are.

## 3. The design

35 strains, communities of 5, 134 training and 70 test communities with plants for modelling. Counting which strains a community holds reads no measurement, so test communities are included. Picture: [`figures/strain_frequency.png`](../../figures/strain_frequency.png).

- Each strain is in 13 to 24 training communities (average 19.1).
- Each strain is in 6 to 16 test communities (average 10.0).
- Pairs of strains that never share a training community: 53 of 595. The most training communities one pair shares: 8.
- Test communities by the most strains they share with any one training community: 13 share 2, 54 share 3, 3 share 4.

| Strain | Training communities | Test communities |
|---|---|---|
| Leaf15 | 17 | 6 |
| Leaf21 | 17 | 10 |
| Leaf32 | 20 | 8 |
| Leaf68 | 19 | 15 |
| Leaf70 | 20 | 10 |
| Leaf76 | 23 | 13 |
| Leaf82 | 19 | 10 |
| Leaf88 | 18 | 13 |
| Leaf122 | 16 | 10 |
| Leaf126 | 21 | 6 |
| Leaf161 | 19 | 10 |
| Leaf168 | 21 | 8 |
| Leaf176 | 21 | 10 |
| Leaf182 | 20 | 14 |
| Leaf183 | 21 | 6 |
| Leaf187 | 14 | 11 |
| Leaf189 | 23 | 8 |
| Leaf203 | 22 | 8 |
| Leaf220 | 18 | 10 |
| Leaf225 | 24 | 7 |
| Leaf226 | 19 | 9 |
| Leaf254 | 19 | 11 |
| Leaf289 | 17 | 7 |
| Leaf299 | 16 | 6 |
| Leaf314 | 16 | 14 |
| Leaf337 | 19 | 10 |
| Leaf339 | 22 | 15 |
| Leaf354 | 16 | 16 |
| Leaf361 | 18 | 7 |
| Leaf371 | 23 | 10 |
| Leaf380 | 23 | 14 |
| Leaf405 | 13 | 6 |
| Leaf416 | 19 | 11 |
| Leaf454 | 21 | 10 |
| Leaf466 | 16 | 11 |

## 4. Missing values, undecided plants and outliers

Plants with each measurement, by group. Picture: [`figures/missing_values.png`](../../figures/missing_values.png).

| Measurement | training | test (sealed) | between-round reference | no strains, infected | no strains, not infected | whole library |
|---|---|---|---|---|---|---|
| plants in the group | 544 | 280 | 16 | 84 | 24 | 12 |
| `pathogen_cfu_per_g` | 543 | 279 | 16 | 84 | 0 | 12 |
| `pathogen_log10_cfu_per_g` | 543 | 279 | 16 | 84 | 0 | 12 |
| `pathogen_log10_normalised` | 543 | 279 | 16 | 84 | 0 | 12 |
| `fresh_weight` | 544 | 280 | 16 | 84 | 24 | 12 |
| `fresh_weight_normalised` | 544 | 280 | 16 | 84 | 24 | 12 |
| `commensal_cfu_per_g` | 543 | 279 | 16 | 0 | 0 | 12 |
| `commensal_log10_cfu_per_g` | 543 | 279 | 16 | 0 | 0 | 12 |
| `strain_cfu_per_g` | 531 | 277 | 16 | 0 | 0 | 0 |
| `strain_log10_cfu_per_g` | 531 | 277 | 16 | 0 | 0 | 0 |

Among the 808 plants used for modelling, missing values: 0. Plants with fewer strain counts than their community has strains: 0. Strain counts that two strains share (they couldn't be told apart on the plate), training plants: 255 of 2,655.

**The undecided (TBD) plants**, from boxes that were dropped, against the rest of their round (median outcome, plants in brackets):

| Round | Group | TRUE | TBD | Box to box |
|---|---|---|---|---|
| Exp1 | training | 6.80 (188) | 7.20 (75) | n/a |
| Exp1 | no strains, infected | 9.16 (12) | 8.94 (16) | 7 boxes, medians 8.59 to 9.53 |

**Outliers.** Training plants more than 2 log10 units (100 times) from the median of the other plants of their community: 22, in 17 communities. They're listed, not removed. By the usual rule for a whole column (beyond 1.5 times the middle half, here 1.85 to 11.58), 0 plants would count as outliers.

| Plant | Community | Round | Outcome | Others' median | Distance |
|---|---|---|---|---|---|
| 103_4 | Mix85 | Exp2 | 4.70 | 9.12 | 4.42 |
| 155_4 | Mix137 | Exp2 | 3.95 | 7.86 | 3.91 |
| 51_4 | Mix42 | Exp1 | 3.39 | 7.18 | 3.79 |
| 106_1 | Mix88 | Exp2 | 7.68 | 4.24 | 3.44 |
| 106_3 | Mix88 | Exp2 | 4.09 | 7.49 | 3.40 |
| 139_3 | Mix121 | Exp2 | 8.28 | 4.89 | 3.39 |
| 40_2 | Mix31 | Exp1 | 8.86 | 5.51 | 3.35 |
| 106_2 | Mix88 | Exp2 | 7.49 | 4.24 | 3.24 |
| 106_4 | Mix88 | Exp2 | 4.24 | 7.49 | 3.24 |
| 153_1 | Mix135 | Exp2 | 6.97 | 3.90 | 3.07 |
| 134_3 | Mix116 | Exp2 | 7.01 | 4.18 | 2.83 |
| 54_4 | Mix45 | Exp1 | 7.27 | 4.53 | 2.73 |
| 39_1 | Mix30 | Exp1 | 7.95 | 5.22 | 2.73 |
| 49_1 | Mix40 | Exp1 | 4.94 | 7.67 | 2.73 |
| 52_2 | Mix43 | Exp1 | 8.32 | 5.60 | 2.72 |
| 113_1 | Mix95 | Exp2 | 7.43 | 4.99 | 2.44 |
| 40_4 | Mix31 | Exp1 | 4.96 | 7.31 | 2.35 |
| 52_4 | Mix43 | Exp1 | 4.55 | 6.90 | 2.35 |
| 98_4 | Mix80 | Exp2 | 6.97 | 4.64 | 2.33 |
| 137_4 | Mix119 | Exp2 | 6.86 | 4.75 | 2.11 |
| 119_4 | Mix101 | Exp2 | 7.01 | 4.92 | 2.09 |
| 73_1 | Mix64 | Exp1 | 6.56 | 4.54 | 2.02 |

## 5. How much plants of one community differ

| Statistic | Value |
|---|---|
| Standard deviation, all training plants | 1.44 |
| Standard deviation within a community | 0.81 |
| Share of the variation between communities (intraclass correlation) | 0.69 |
| Plants per community | 4 plants: 130, 3 plants: 3, 2 plants: 1 |

Communities with plants on both sides of the dip (5.71): 47 of 134. All plants below it: 15; all above it: 72.

## 6. One strain at a time

For each strain, the mean outcome of the 134 training communities that hold it minus the mean of those that don't, community by community (each community's plants averaged first). Below zero: less pathogen where the strain was. Shuffling the community means 1,000 times (seed 2026), the largest difference of any strain reached **1.01** in 95 % of the shuffles; a strain stands out only beyond that. A first look, not a model: strains share communities, so one strain's difference carries some of its partners'. Picture: [`figures/one_strain_at_a_time.png`](../../figures/one_strain_at_a_time.png).

| Strain | Communities with it | Mean with it | Difference | Stands out |
|---|---|---|---|---|
| Leaf76 | 23 | 5.32 | -1.68 | yes |
| Leaf68 | 19 | 5.32 | -1.61 | yes |
| Leaf15 | 17 | 5.45 | -1.44 | yes |
| Leaf337 | 19 | 6.10 | -0.71 |  |
| Leaf371 | 23 | 6.25 | -0.55 |  |
| Leaf203 | 22 | 6.43 | -0.33 |  |
| Leaf220 | 18 | 6.44 | -0.31 |  |
| Leaf361 | 18 | 6.53 | -0.21 |  |
| Leaf405 | 13 | 6.54 | -0.18 |  |
| Leaf82 | 19 | 6.59 | -0.14 |  |
| Leaf32 | 20 | 6.61 | -0.12 |  |
| Leaf189 | 23 | 6.64 | -0.08 |  |
| Leaf354 | 16 | 6.65 | -0.07 |  |
| Leaf88 | 18 | 6.69 | -0.03 |  |
| Leaf182 | 20 | 6.70 | -0.01 |  |
| Leaf161 | 19 | 6.76 | +0.07 |  |
| Leaf176 | 21 | 6.76 | +0.07 |  |
| Leaf168 | 21 | 6.83 | +0.14 |  |
| Leaf183 | 21 | 6.94 | +0.28 |  |
| Leaf339 | 22 | 6.94 | +0.28 |  |
| Leaf122 | 16 | 6.98 | +0.31 |  |
| Leaf126 | 21 | 6.97 | +0.32 |  |
| Leaf21 | 17 | 7.00 | +0.33 |  |
| Leaf254 | 19 | 7.00 | +0.34 |  |
| Leaf454 | 21 | 7.00 | +0.34 |  |
| Leaf466 | 16 | 7.01 | +0.35 |  |
| Leaf299 | 16 | 7.03 | +0.37 |  |
| Leaf70 | 20 | 7.03 | +0.37 |  |
| Leaf187 | 14 | 7.06 | +0.39 |  |
| Leaf314 | 16 | 7.17 | +0.52 |  |
| Leaf225 | 24 | 7.16 | +0.55 |  |
| Leaf289 | 17 | 7.20 | +0.57 |  |
| Leaf380 | 23 | 7.25 | +0.65 |  |
| Leaf416 | 19 | 7.31 | +0.70 |  |
| Leaf226 | 19 | 7.36 | +0.76 |  |

## 7. How the other layers relate

Spearman's rank correlation between each strain property and the differences of section 6 (1: the two orders agree, -1: reversed, 0: no relation). Shuffling the differences 1,000 times, the largest correlation of any property reached **0.45** in 95 % of the shuffles.

| Property | Strains | Correlation | Stands out |
|---|---|---|---|
| genome length (Layer 2) | 34 | -0.49 | yes |
| GC content (Layer 2) | 34 | +0.31 |  |
| gene clusters (Layer 3) | 34 | +0.00 |  |
| possibly inhibitory clusters (Layer 3) | 34 | -0.02 |  |
| strains it held back (Layer 4) | 35 | -0.25 |  |
| strains that held it back (Layer 4) | 35 | +0.39 |  |

Plant by plant, the total commensal load (all the community's bacteria, log10 per gram, median 8.38, middle half 8.17 to 8.62) against the outcome: rank correlation +0.43, 531 training plants.
