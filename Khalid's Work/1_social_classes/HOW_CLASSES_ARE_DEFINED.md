# How the class cut points are defined

**Data:** HIES 2024-25 (PBS). Section 6A (consumption), the household roster, and `weight.dta`.
**Unit of analysis:** the household. Every share is a share of Pakistan's 40.1 million households, weighted by the household weight.
**Code:** [`social_classes_kmeans_knn.ipynb`](social_classes_kmeans_knn.ipynb), Steps 1-4. All numbers below are printed by the notebook.

## Spending classes (Test A): the main result

**Step 1: monthly spending of each household.** For every item in Section 6A we add the four ways it was consumed:

> `v1` bought + `v2` wages in kind + `v3` own production + `v4` gifts or assistance.

Rows with item code `itc` below 10000 are page totals; we drop them so nothing is counted twice. Each item is then converted to one month according to the period the questionnaire asked about:

| Part | Items | Period asked | Factor to one month |
|---|---|---|---|
| A | Perishable food | last 14 days | × 365 / 12 / 14 = × 2.173 |
| B | Staple food, prepared food, cleaning, personal care | last month | × 1 |
| C | Tobacco, water, electricity, gas, fuel | last month | × 1 |
| D | Clothing, rent (including the rental value of an owned home), health, education, transport, etc. | last 12 months | ÷ 12 |
| E | Durable goods | last 12 months | ÷ 12 |

Household monthly spending is the sum over all items. Our average is Rs 81,351; the PBS report gives Rs 79,150.

**Step 2: spending per person.**

> spending per person = household monthly spending ÷ number of household members

Household members are the roster rows with `s1aq10 = 1`. Spending per person is only used to **rank** households. The household remains the unit that is counted and weighted.

**Step 3: take the logarithm.**

> x = ln(spending per person)

Spending is very skewed. On a log scale, "twice as much" is the same distance at every level, so a few very rich households cannot take over a class.

**Step 4: weighted K-means with 5 classes.** K-means picks 5 centres c₁ < … < c₅ that minimise the weighted within-class spread:

> Σ over households of  weightᵢ × (xᵢ − nearest centre)²

`weightᵢ` is the household weight from `weight.dta`, i.e. the number of Pakistani households that sampled household represents. The settings are `scikit-learn KMeans(n_clusters=5, n_init=50, tol=0, max_iter=3000, random_state=42)`, with `sample_weight = weight`. Every one of the 50 random starts runs to full convergence (`tol=0`), and the start with the lowest spread is kept. Different seeds give the same classes (adjusted Rand index 0.998-1.000).

**Step 5: turn centres into cut points.** Each household joins the class whose centre is **nearest**. On one line, the boundary between two neighbouring classes is therefore exactly halfway between their centres, measured in logs:

> cut between class k and k+1 = exp( (cₖ + cₖ₊₁) / 2 ) = √( centreₖ × centreₖ₊₁ ) in rupees

That is, each cut point is the geometric mean of the two neighbouring centres.

| Class | Centre (Rs per person per month) | Cut points (Rs per person per month) | % of households | Households |
|---|---:|---|---:|---:|
| Lower | 5,439 | below 6,999 | 17.2% | 6.9 M |
| Lower-middle | 9,005 | 6,999 – 11,399 | 32.3% | 13.0 M |
| Middle | 14,431 | 11,399 – 19,120 | 29.6% | 11.9 M |
| Upper-middle | 25,332 | 19,120 – 40,282 | 16.7% | 6.7 M |
| Upper | 64,054 | above 40,282 | 4.2% | 1.7 M |

For example, the first cut is √(5,439 × 9,005) = 6,999. Applying these cut points reproduces the K-means class of **100%** of households (checked in the notebook).

**Step 6: class shares.**

> % of households in class k = Σ weight (households in class k) ÷ Σ weight (all households) × 100

The "Households" column is Σ weight for the class.

## The thresholds per day and in 2023 PPP dollars

The project standard is **2023 US dollars (PPP)**.

- **Per day** = per month ÷ (365/12) = per month ÷ 30.4.
- **$1 (2023 PPP) = 59.2849 × (393.661 ÷ 343.421) = Rs 67.96** in 2024-25 prices.
  - 59.2849 is the World Bank PPP conversion factor for private consumption, Pakistan 2023 (`PA.NUS.PRVT.PP`).
  - The ratio is the World Bank CPI (`FP.CPI.TOTL`). The survey period's index is the average of 2024 (386.80) and 2025 (400.52), because fieldwork ran from October 2024 to June 2025. The 2023 index is 343.42.

| Threshold | Rs per person per month | 2023 PPP $ per person per day |
|---|---:|---:|
| Lower \| Lower-middle | 6,999 | 3.39 |
| Lower-middle \| Middle | 11,399 | 5.51 |
| Middle \| Upper-middle | 19,120 | 9.25 |
| Upper-middle \| Upper | 40,282 | 19.49 |

## Imputed (non-cash) consumption in each class

Spending includes goods and services consumed without paying cash, valued by HIES in Section 6A:
- the rental value of an owned home (item 42101);
- own produce (column `v3`, minus that rent);
- wages in kind (`v2`);
- gifts in kind (`v4`).

The table shows each as a % of the class's total spending (household-weighted):

| Class | Home rent | Own produce | Wages | Gifts | Total imputed | Rs per household per month |
|---|---:|---:|---:|---:|---:|---:|
| Lower | 4.1 | 8.1 | 1.3 | 5.6 | **19.0** | 7,899 |
| Lower-middle | 5.0 | 8.0 | 0.8 | 4.6 | **18.4** | 10,765 |
| Middle | 6.3 | 6.9 | 0.5 | 3.7 | **17.4** | 13,916 |
| Upper-middle | 8.1 | 4.6 | 0.4 | 3.6 | **16.7** | 19,924 |
| Upper | 17.6 | 2.4 | 0.6 | 3.4 | **23.9** | 66,638 |
| All households | 7.9 | 6.1 | 0.6 | 4.0 | **18.5** | 15,081 |

**What happens without it:** with cash spending only and the same cut points, the classes would be 32.0 / 31.2 / 22.7 / 11.6 / 2.7% of households, and only 66% of households would stay in their class.

**Caution:** only 56% of households have an owned-home rent value recorded, so some owner-occupiers may have no imputed rent.

## Urban and rural households classified separately

The same weighted K-means (Steps 3-6) is run on urban households only (10,960 sampled; 16.3 million) and rural households only (19,163; 23.8 million). The table gives Rs per person per month, with 2023 PPP $ per person per day in brackets.

| Threshold | National | Urban only | Rural only | Urban ÷ rural |
|---|---:|---:|---:|---:|
| Lower \| Lower-middle | 6,999 ($3.39) | 8,854 ($4.28) | 6,237 ($3.02) | 1.42 |
| Lower-middle \| Middle | 11,399 ($5.51) | 14,736 ($7.13) | 9,661 ($4.67) | 1.53 |
| Middle \| Upper-middle | 19,120 ($9.25) | 24,986 ($12.09) | 15,076 ($7.29) | 1.66 |
| Upper-middle \| Upper | 40,282 ($19.49) | 53,085 ($25.68) | 27,600 ($13.35) | 1.92 |

| % of households | Lower | Lower-middle | Middle | Upper-middle | Upper |
|---|---:|---:|---:|---:|---:|
| Urban, own thresholds | 19.4 | 33.8 | 27.3 | 15.0 | 4.6 |
| Rural, own thresholds | 16.1 | 31.1 | 29.2 | 18.4 | 5.2 |
| Urban, national thresholds | 8.5 | 26.4 | 33.3 | 24.3 | 7.6 |
| Rural, national thresholds | 23.1 | 36.4 | 27.1 | 11.5 | 1.9 |

- **Same structure, different levels.** Each area splits about the same way as the nation, but urban thresholds are 27-32% above the national ones and rural thresholds 11-31% below.
- **The urban-rural gap widens at the top.** The ratio rises from 1.4 at the bottom threshold to 1.9 at the top. Price differences alone would shift all thresholds by a similar proportion.
- **Agreement with the national classes.** 56% of urban and 67% of rural households keep their national class when their area is classified alone; all stay within one class.
- **No regional price index.** HIES has none, so part of the gap is the higher urban cost of living.

**Imputed consumption, urban and rural** (% of spending, household-weighted):

| Area | Home rent | Own produce | Wages | Gifts | Total | $ per person per day (2023 PPP) | % of households with home rent | % with own produce |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Urban | 10.2 | 1.6 | 0.5 | 3.1 | **15.4** | 1.60 | 50 | 30 |
| Rural | 5.7 | 10.4 | 0.7 | 4.8 | **21.6** | 1.33 | 61 | 69 |
| All households | 7.9 | 6.1 | 0.6 | 4.0 | **18.5** | 1.44 | 56 | 53 |

- **Rural:** imputed consumption is mostly own produce. It stays at 21-22% of spending in every national class: richer rural households grow less of their own food, but the rental value of their homes is higher.
- **Urban:** it is mostly the rental value of owned homes. It rises from 12% of spending in the lower class to 24% in the upper class.

## Other class definitions in the project, for comparison

**Quintiles (benchmark, Step 3 of the notebook).** Households are sorted by spending per person, and the cumulative household weight is cut at 20 / 40 / 60 / 80%. Each quintile is then exactly 20% of households. The cut points fall at about Rs 7,343 / 9,953 / 13,299 / 19,538 per person per month.

**Income classes (Test C, Step 8).** These use the same Steps 3-6, applied to full income per person instead of spending per person.
- Full income = cash income from Section 1B + transfers (Section 8A) + property income (Sections 9A, 9B, 10A, 11) + income in kind (Section 6A columns `v2`, `v3`, `v4`).
- Full income per person = full income ÷ household members.
- Before clustering, values below the household-weighted 1st percentile (Rs 3,238) are raised to that value. Otherwise a few households reporting almost no income would form a class of their own.
- Resulting cut points: Rs 6,939 / 11,783 / 20,692 / 45,384 per person per month.

**Middle and Affluent Class lines (Experiment 2, `../2_mac_infographic/`).** These lines are **fixed in advance**, not found from the data. They follow the 2018 KIDE infographic: spending per person per day of $2 / $4 / $6 in **2011 PPP dollars**, a different base from the 2023 PPP dollars above, so the two sets of dollar figures are not directly comparable.
- $1 (2011 PPP) = 25.4956 × (393.66 ÷ 111.916) = **Rs 89.68** in 2024-25 prices. That is the 2011 PPP conversion factor for private consumption, multiplied by the CPI ratio between 2024-25 and 2011.
- Monthly lines = daily line × 89.68 × 365/12, which gives **Rs 5,456 / 10,911 / 16,367** per person per month.

## What the cut points are *not*

- **They are not salaries.** They are spending per person. A family of 6 needs total monthly spending above 6 × 40,282 = Rs 241,700 to be upper class.
- **They are not natural gaps in the data.** Spending per person has a single peak. K-means chooses the cut points that make the 5 classes as internally similar as possible.
- **They only apply to this survey round.** K-means cut points move from year to year. Comparisons over time should use the fixed MAC lines.
