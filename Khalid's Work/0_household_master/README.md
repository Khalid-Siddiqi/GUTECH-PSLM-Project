# Household master file (HIES 2024-25)

This file has **one row per household**: all 30,123 surveyed households, with 234 columns built from the raw HIES files. Use it as the starting point for any household-level analysis, so you don't have to merge the 26 raw files again.

**Unit of analysis: the household.** Weight every result with `weight`, the household weight, and report "% of households" or "number of households". `pop_weight` (= weight × household size) is only for stating a population total.

| File | What it is |
|---|---|
| [`build_household_master.ipynb`](build_household_master.ipynb) | Builds the file from `../../HIES 2024_2025/`, runs the checks, and compares with Census 2023. Already run, so outputs are visible. |
| [`outputs/household_master.csv`](outputs/household_master.csv) | **The master file**: 30,123 rows × 234 columns, 37 MB |
| [`outputs/household_master_codebook.csv`](outputs/household_master_codebook.csv) | One row per column: group, source file, meaning, number of non-missing values, example value |
| [`HIES_vs_Census_2023.pdf`](HIES_vs_Census_2023.pdf) | Technical note *Benchmarking HIES 2024-25 against the 2023 Census* (2 pages). Built by `../reports/build_reports.py` |

## What is inside

| Group | Columns | Source | How |
|---|---:|---|---|
| Identifiers and weight | 11 | `section_info`, `weight` | `hhcode`, `prcode`, province (Islamabad separate), rural/urban, stratum, quarter, interview date, `weight`, `pop_weight` |
| Members | 15 | Roster (1A) | Household size, sex and age groups, dependency ratio, head's sex, age and marital status |
| Education | 9 | 2A/2B | Head's literacy and years of schooling, literate members, children 5-16 in school |
| Work | 6 | 1B | Head's employment status, number working and earning, cash income from work |
| Phones and internet | 4 | 2C | Members owning a mobile or smartphone, using the internet, with a bank or digital account |
| Interview, housing, water and sanitation, waste, food insecurity | 108 | 5M1-5M4 | **Copied as they are**: original question columns, with text answers from `CSV data/`. FIES columns start with `fies_`; `fies_score` counts the "yes" answers (0-8). |
| Spending | 21 | 6A | Total and 12 COICOP groups (Rs per month), per person, food share, in-kind parts, imputed rent, household quintile |
| Durable goods | 35 | 7 | Number of each item owned now: TV, fridge, AC, motorcycle, car, solar panel, … |
| Transfers | 9 | 8A | Remittances (domestic, abroad), BISP, assistance, zakat, totals received and paid |
| Property and savings | 9 | 9A, 9B | Rent received, profit, savings, gold, loans owed, agricultural land, owns a house |
| Farm and business | 4 | 10A, 10B, 11 | Farm household, livestock household, crop value, number of non-farm businesses |
| Income totals | 3 | derived | `income_in_kind`, `income_full`, `income_full_per_person` |

All money flows are in **Rs per month** (yearly amounts ÷ 12). Savings, gold and loans are values on the interview date.

**Not included:** the health sections (3A-3C) and women's sections (4A-4E). They describe individual children and women, not households, and belong in a person-level file.

## Checks

The notebook checks that the master file reproduces earlier results:

- **Experiment 1:** household size, weight, spending, cash income, earners, transfers, property income, income in kind and full income are identical for **100% of households**. Spending and income use the same definitions as in `../1_social_classes/HOW_CLASSES_ARE_DEFINED.md`.
- **PBS HIES 2024-25 report:**
  - **Household size:** 5.98 overall, 5.69 urban, 6.18 rural. The same as the report to two decimals.
  - **Provincial household size:** Punjab 5.77, Sindh 5.70, KP 6.83, Balochistan 7.08. All four match the report.
  - **Spending and income per household:** Rs 81,351 and Rs 84,057, against Rs 79,150 and Rs 82,179 in the report.
- **Missing heads:** 4 households have no head among their members, so their `head_*` columns are blank.

## How HIES compares with official statistics (Census 2023)

The benchmark is the **7th Population and Housing Census 2023** (PBS), counted on 1 March 2023. Like HIES, it covers the four provinces and Islamabad, but not AJK or Gilgit-Baltistan. HIES interviews ran from **1 October 2024 to 30 June 2025**; the middle date is 11 February 2025, 1.95 years after the census.

### National

| Indicator | HIES 2024-25 (weighted) | Census 2023 | Census projected to Feb 2025 |
|---|---:|---:|---:|
| **Households** | **40.12 million** | 38.29 million | 40.63 million |
| **Population** | **239.82 million** | 241.49 million | 253.66 million |
| **Average household size** | **5.98** | 6.30 | |
| **% of population rural** | **61.3%** | 61.2% | |
| % of households rural | 59.3% | not published | |
| % of households lit by grid electricity | 88.2% (grid, or grid + solar) | 84.0% | |
| % of households lit by solar only | 7.4% | 7.7% | |

The projections assume the census growth rates continue. Households grew 3.08% a year from 2017 to 2023 (31.92 → 38.29 million), and population grew 2.55% a year.

### By province

| Province | HIES households | HIES % of households | HIES population | Census population | HIES % of population | Census % of population | HIES % rural | Census % rural | HIES household size |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Punjab | 21.98 M | 54.8% | 126.7 M | 127.7 M | 52.8% | 52.9% | 59.5% | 59% | 5.76 |
| Sindh | 9.73 M | 24.3% | 55.5 M | 55.7 M | 23.1% | 23.1% | 46.2% | 47% | 5.70 |
| KP | 5.94 M | 14.8% | 40.6 M | 40.9 M | 16.9% | 16.9% | 85.1% | 85% | 6.83 |
| Balochistan | 2.08 M | 5.2% | 14.7 M | 14.9 M | 6.2% | 6.2% | 68.8% | 69% | 7.08 |
| Islamabad | 0.38 M | 1.0% | 2.3 M | 2.4 M | 1.0% | 1.0% | 53.2% | 53% | 6.10 |

The census % rural figures are rounded to whole numbers in the census releases.

### What the comparison shows

1. **The number of households agrees with the census once growth is allowed for.**
   - HIES gives 40.1 million households, 4.8% more than the census count of March 2023.
   - That gap is about two years of household growth: the census projected to the HIES mid-point gives 40.6 million.
   - So HIES is only 1.3% below the projection.
2. **Population matches the census count, but not the projection.**
   - HIES gives 239.8 million people, 0.7% below the census count, but 5.5% below the census projected to 2025.
   - The reason is household size: HIES households are smaller (5.98 people, against 6.30 in the census), so the right number of households holds fewer people.
   - Possible reasons:
     - **Who counts as a member.** HIES counts only household members (`s1aq10 = 1`).
     - **People outside households.** HIES leaves out people living in institutions such as hostels, barracks and prisons, whom the census counts.
     - **Larger households may be under-covered**, which is common in household surveys.
   - This is why the **household count is the more reliable HIES total**, and one more reason to use households as the unit of analysis.
3. **The rural/urban split is almost identical.**
   - 61.3% of people live in rural areas in HIES, against 61.2% in the census.
   - In every province the rural share is within 1 point of the census.
   - By households the rural share is lower (59.3%), because rural households are bigger (6.18 against 5.69 people).
4. **Provincial shares of the population match the census within 0.1 point.** HIES weights are built from the census sampling frame, so this is expected. It confirms that the weights are applied correctly.
5. **Electricity is about 4 points higher in HIES** (88% against 84%). A small rise is plausible two years later. The two surveys may also classify "grid + solar" differently. Solar-only lighting (7.4% against 7.7%) agrees closely.

**Caution:**
- **Census figures were transcribed by hand.** The census figures above come from PBS census releases, typed into the notebook (section 12), not read from a census data file.
- **Main sources:**
  - [PBS 7th Population and Housing Census results](https://www.pbs.gov.pk/node/1576);
  - [National Census Report 2023](https://www.pbs.gov.pk/wp-content/uploads/2020/07/National-Census-Report-2023.pdf), for households and household size;
  - [PBS national housing data](https://www.pbs.gov.pk/sites/default/files/population/2023/material/pakistan_housing_data.pdf), for lighting;
  - [Dawn, 2023 census results](https://www.dawn.com/news/1768626/population-surpasses-240m-new-census-shows).
- **Households and household size differ slightly between PBS releases** (38.29 or 38.32 million; 6.3 or 6.33 people). Neither difference changes any conclusion.

## Using the file

```python
import pandas as pd, numpy as np
m = pd.read_csv("outputs/household_master.csv", low_memory=False)

# % of households with a car, by province
car = m.own_car > 0
(m.weight * car).groupby(m.province).sum() / m.weight.groupby(m.province).sum() * 100

# add Experiment 1's social classes
classes = pd.read_csv("../1_social_classes/outputs/household_classes.csv", usecols=["hhcode", "class_A_name"])
m = m.merge(classes, on="hhcode")
```

To rebuild: from this folder, run `jupyter notebook build_household_master.ipynb` and choose "Run All". It takes under a minute. The final check reads `../1_social_classes/outputs/household_classes.csv`, so Experiment 1's output must exist.
