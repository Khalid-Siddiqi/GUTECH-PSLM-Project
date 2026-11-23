# Khalid's Work

Two experiments on who is rich, middle or poor in Pakistan, using the HIES 2024-25 survey (`../HIES 2024_2025/`) and its weights.

**Unit of analysis: the household.** After weighting, the survey represents **40.1 million households** and **239.8 million people** (average household size 5.98; AJK and Gilgit-Baltistan are not covered).

| Folder | What's inside | Main output |
|---|---|---|
| [`0_household_master/`](0_household_master/) | **Household master file:** one row per household (30,123 × 234 columns) built from all household, person and item files, plus a comparison of HIES totals with Census 2023 | [household_master.csv](0_household_master/outputs/household_master.csv) + [codebook](0_household_master/outputs/household_master_codebook.csv) |
| [`1_social_classes/`](1_social_classes/) | **Experiment 1:** machine learning (weighted K-means and KNN) splits the population into 5 classes by spending, then checks the classes against income | [5 classes chart](1_social_classes/outputs/test_a_classes.png) |
| [`2_mac_infographic/`](2_mac_infographic/) | **Experiment 2:** a 2024-25 update of the 2018 KIDE "Middle and Affluent Class" infographic, using fixed dollar-a-day lines | [2-page report](2_mac_infographic/outputs/MAC_report_2024_25.pdf) |

Each folder has its own README with the results, its notebook, an `outputs/` folder, and instructions for re-running.

**PDF reports:**
- [Benchmarking HIES 2024-25 against the 2023 Census](0_household_master/HIES_vs_Census_2023.pdf)
- [Consumption-Based Social Classes in Pakistan](1_social_classes/HOW_CLASSES_ARE_DEFINED.pdf)

To rebuild them, run `python reports/build_reports.py`. It recomputes every number from the output files, draws the charts, and prints the pages to PDF with Microsoft Edge.

## How the two fit together

1. **Experiment 1 comes first.** It adds up every household's monthly spending from Section 6A and saves it to `1_social_classes/outputs/household_classes.csv`.
2. **Experiment 2 reuses that file.** It converts the same spending into dollars a day and applies the infographic's fixed lines.

| | Experiment 1 | Experiment 2 |
|---|---|---|
| Class lines come from | the data (K-means finds them) | fixed in advance ($2 / $4 / $6 a day) |
| Number of classes | 5 | 4 (Poor, LC, LMC, MAC) |
| Good for | describing society today | comparing years |
| Headline | 4% of households are upper class; 62% are lower-middle or middle | 22% of people are Middle and Affluent Class (still population-based, see below) |

**Still to convert:** Experiment 2 still reports shares of **people**, because the 2018 KIDE infographic it updates uses population shares. Converting it to households is pending a decision on how to handle the earlier years taken from that infographic.
