# A Beginner's Guide to the HIES 2024-25 Stata Data

This guide explains every file in the `Stata data` folder: what it contains, how the files fit together, and how to use `weight.dta` correctly.

You do not need any background in survey statistics to read it. Technical words are explained the first time they appear, and there is a glossary at the end.

All numbers in this guide were computed directly from the files in the `Stata data/` folder.

---

## Contents

1. [What is this data?](#1-what-is-this-data)
2. [Basic ideas you need first](#2-basic-ideas-you-need-first)
3. [How the survey picked its households](#3-how-the-survey-picked-its-households)
4. [The ID variables that connect everything](#4-the-id-variables-that-connect-everything)
5. [The three shapes of files](#5-the-three-shapes-of-files)
6. [All 26 files at a glance](#6-all-26-files-at-a-glance)
7. [Each section explained](#7-each-section-explained)
8. [weight.dta in detail](#8-weightdta-in-detail)
9. [Common mistakes and traps](#9-common-mistakes-and-traps)
10. [Glossary](#10-glossary)

---

## 1. What is this data?

**HIES** stands for **Household Integrated Economic Survey**. It is run by the **Pakistan Bureau of Statistics (PBS)** as part of the PSLM programme (Pakistan Social and Living Standards Measurement).

In the 2024-25 round:

- Interviewers visited **30,123 households** between **October 2024 and June 2025**.
- They used tablets instead of paper questionnaires, for the first time.
- These households contain **184,564 people**.
- Each household answered two questionnaires: a **male questionnaire**, usually answered by a man of the household, and a **female questionnaire**, answered by a woman. Both PDFs are in this folder.
- The survey covers income, spending, assets, savings, education, health, mobile phone and internet use, housing, water and sanitation, food insecurity, and more.

**Coverage of these files:** Khyber Pakhtunkhwa (KP), Punjab, Sindh, Balochistan and Islamabad. The official report says the survey also covered Azad Jammu & Kashmir (AJK) and Gilgit-Baltistan (GB), but **those households are not in these files**.

### "Microdata" vs. report tables

The PDF report shows **summary tables**, such as "X% of households have internet". The files in `Stata data/` are **microdata**: one row for each household, each person, or each item a household bought. This is the raw material that the report's tables were calculated from.

With microdata you can produce your own tables, combine topics (for example, income and education), and build models.

---

## 2. Basic ideas you need first

### 2.1 What is a `.dta` file?

`.dta` is the file format of **Stata**, a statistics program. Each `.dta` file is one table, like one Excel sheet. Besides the data, the file stores two kinds of labels:

- **Variable labels** describe what a column means. Example: column `s1aq03` has the label "sex".
- **Value labels** describe what each number in a column means. Example: in `s1aq03`, `1 = male` and `2 = female`.

You don't need Stata to open these files:

| Tool | How to open |
|---|---|
| **Stata** | `use "plist_roster.dta", clear` |
| **Python (pandas)** | `pd.read_stata("plist_roster.dta", convert_categoricals=False)` |
| **R** | `haven::read_dta("plist_roster.dta")` |
| **SPSS** | File → Open → Data → choose the `.dta` file |

> **Python tip:** add `convert_categoricals=False` so you get the original numeric codes (1, 2, 3 …) and not text labels. Numbers are easier to filter, and some label sets in these files contain odd characters.
>
> To see what the codes mean, open the file with `pd.io.stata.StataReader(path)` and call `.value_labels()` and `.variable_labels()` on it.

### 2.2 How the column names work

Most column names follow the questionnaire, so you can always look up the exact question:

```
s 2 a q 01
│ │ │ │ └── question number 01
│ │ │ └──── "q" = question
│ │ └────── part a of the section
│ └──────── section 2
└────────── "s" = section
```

So `s2aq01` means **Section 2, Part A, Question 1**: "Can [person] read a simple statement in any language with full understanding?"

Some names have an extra digit or letter for multi-part questions. For example, `s3bq04b1` is "Penta 1" in the vaccination list.

Columns ending in **`ot`** or **`oth`** hold the free text written when someone answered "Other (specify)". They often contain the word `NULL` when empty.

### 2.3 Sample vs. population

The survey did **not** interview every household in Pakistan. It interviewed a **sample** of about 30,000 households and uses them to describe the **population** of about 40 million households.

To get from the sample to the population, you need **weights**. That is what `weight.dta` is for (see [Section 8](#8-weightdta-in-detail)).

---

## 3. How the survey picked its households

PBS used a **stratified two-stage sample design**.

```
Pakistan
 └── split into STRATA (groups), roughly by area and urban/rural
      └── Stage 1: choose some PSUs (villages / city blocks) in each stratum
           └── Stage 2: choose a fixed number of households in each PSU
                 ├── 16 households in each rural PSU
                 └── 12 households in each urban PSU
```

Each step in plain words:

- **Stratum** (plural: **strata**): a group of areas treated separately when sampling, such as "rural areas of district X". Sampling every stratum separately guarantees that every area is represented.
- **PSU (Primary Sampling Unit)**: the first thing that gets chosen. In rural areas this is a **village**. In cities it is an **enumeration block**, a small area of about 200-250 households defined by the 2023 Census.
- **PPS (Probability Proportional to Size)**: bigger PSUs had a bigger chance of being chosen at Stage 1.
- **Systematic sampling**: inside each chosen PSU, households were picked at regular intervals from a list, such as every 10th household.

What the data actually contains:

| | Rural | Urban | Total |
|---|---|---|---|
| PSUs (villages / blocks) | 1,212 | 941 | **2,153** |
| Households | 19,163 | 10,960 | **30,123** |
| Usual households per PSU | 16 | 12 | |

Fieldwork was spread over **four quarters** (`quater` / `quarter` = 1, 2, 3, 4) so that seasonal effects average out. In practice, quarter 1 households were mostly interviewed in October to December 2024, and quarter 4 households mostly in April to June 2025.

---

## 4. The ID variables that connect everything

Every file shares the same ID columns. They let you link a person's education to the same person's income, or a household's spending to its weight.

### 4.1 `prcode`: the PSU code (8 digits)

The `prcode` packs several pieces of information into one number. Here is how to read `11021001`:

```
 1   1 0   2   1   0 0 1
 │   └─┘   │   │   └───┘
 │    │    │   │     └── PSU serial number (001)
 │    │    │   └──────── quarter (1 = first quarter of fieldwork)
 │    │    └──────────── urban/rural (1 = rural, 2 = urban)  ← here: urban
 │    └───────────────── stratum code within the province (10)
 └────────────────────── province (1 = KP)
```

The first digit (province) uses the same codes as the `province` column, with one exception:

| First digit | Meaning | `province` column |
|---|---|---|
| 1 | Khyber Pakhtunkhwa | 1 = kp |
| 2 | Punjab | 2 = punjab |
| 3 | Sindh | 3 = sindh |
| 4 | Balochistan | 4 = balochistan |
| 6 | **Islamabad** | **coded as 2 (Punjab)** |

> **Islamabad:** 212 Islamabad households (prcode starting with `6`) are labelled `province = 2` (Punjab) in the data. If you want Islamabad on its own, use the first digit of `prcode`.

The **first three digits** of `prcode` (province + stratum) identify the **stratum**. There are 158 strata in the data, and each one is entirely rural or entirely urban.

### 4.2 `hhno`: household number inside the PSU

`hhno` is the household's number within its PSU. **Never use `hhno` alone.** Household 1 exists in hundreds of different PSUs.

### 4.3 `hhcode`: the unique household ID

```
hhcode = prcode × 1000 + hhno
e.g.     11021001 × 1000 + 1 = 11021001001
```

`hhcode` is unique for every one of the 30,123 households, so it is the column to use when joining files.

> It is stored as a decimal number (float). Convert it to a whole number (`astype("int64")` in pandas) before joining, or it may print as `1.102100e+10`.

### 4.4 `idc`: person ID inside the household

`idc` identifies a person within a household. The number range tells you which questionnaire the person's details came from:

| `idc` range | Who | Questionnaire |
|---|---|---|
| **1 – 15** | Males aged 10 and over | Male questionnaire, roster Part M |
| **51 – 65** | All females, and all children (boys and girls) under 10 | Female questionnaire, roster Part F |

A **person** is uniquely identified by **`hhcode` + `idc`**.

Other columns in the roster store `idc` values of related people: `s1aq07` (spouse), `s1aq08` (father) and `s1aq09` (mother). With these you can link children to their parents. In those columns, code 98 means "not alive" and 99 means "not in the household".

### 4.5 Other common columns

| Column | Meaning |
|---|---|
| `province` | 1 = KP, 2 = Punjab (includes Islamabad), 3 = Sindh, 4 = Balochistan |
| `region` | 1 = rural, 2 = urban |
| `quater` / `quarter` | Survey quarter, 1-4. The spelling differs between files. |
| `ino` | Child number in the maternity history (Section 4B) |
| `itc` / `code` | Item code in the item-level files (Sections 6-11) |

---

## 5. The three shapes of files

Before analysing a file, ask: **"What does one row represent?"** In `Stata data/` there are three answers.

### Shape 1: household files (one row = one household)

These have exactly 30,123 rows. Examples: housing, water and sanitation, waste management, the food insecurity scale (FIES), and `section_info`.

### Shape 2: person files (one row = one person)

The ID is `hhcode` + `idc`. Examples: the roster, education, employment and income, ICT use, and the health and women's sections.

Different person files cover different groups of people, because each question was only asked of certain people. For example, employment covers everyone aged 10 and over, and family planning covers only currently married women aged 15-49.

### Shape 3: item files (one row = one household × one item)

These are the "long" files. Instead of one row per household with 300 columns, there is one row per household for **each item**: wheat, sugar, electricity bill, a motorcycle, and so on. The item is identified by `itc` or `code`, and the amounts are in the remaining columns.

Examples: consumption expenditure (Section 6A), durable goods (Section 7), transfers (8A), property (9A), savings and loans (9B), agriculture (10A), livestock (10B), non-farm business (11).

> **Warning:** item files also contain **total rows** (codes such as `1000`, `2000`, `5000`, `700`, `800`, `910` …). If you add up every row you will **double count**. Either use only the total rows or exclude them. See [Section 9](#9-common-mistakes-and-traps).

---

## 6. All 26 files at a glance

| File | Topic | One row = | Rows | Households |
|---|---|---|---:|---:|
| `section_info.dta` | Interview status and date | household | 30,123 | 30,123 |
| `weight.dta` | **Sampling weight** | **PSU** | **2,153** | (all) |
| `plist_roster.dta` | Household roster: age, sex, relation, marital status | person | 184,564 | 30,123 |
| `sec_1b_emp_income.dta` | Employment and income (age 10+) | person | 134,468 | 30,123 |
| `sec_2ab_education.dta` | Literacy and schooling | person | 170,901 | 30,123 |
| `sec_02c_ict.dta` | Mobile, computer and internet use, online shopping | person | 161,203 | 30,123 |
| `Sec_03a_diarrhoea.dta` | Child diarrhoea and treatment | child | 22,934 | 13,964 |
| `Sec_03b_immunisation.dta` | Child vaccinations | child | 22,934 | 13,964 |
| `sec_03c_malaria.dta` | Malaria/dengue, hepatitis, TB | person | 183,967 | 30,123 |
| `Sec_04a_pregnancyhistory.dta` | Women's birth history summary | woman | 44,103 | 27,526 |
| `sec_04b_maternityhistory.dta` | Each child born to each woman | birth | 80,978 | 21,255 |
| `sec_04c_familyplanning.dta` | Contraception knowledge and use | married woman 15-49 | 28,567 | 24,236 |
| `Sec_04d_pre_post_natal.dta` | Pregnancy care and delivery | ever-married woman 15-49 | 29,601 | 24,897 |
| `Sec_04e_decisionmaking.dta` | Who decides about education, work, marriage, purchases | woman 15-49 | 44,155 | 27,533 |
| `sec_05m1_housingchar.dta` | Dwelling, fuel, assets, internet, roads, transport | household | 30,123 | 30,123 |
| `sec_05m2_watersanitation.dta` | Drinking water, toilets, hand washing | household | 30,123 | 30,123 |
| `sec_05m3_wastemanagment.dta` | Garbage disposal | household | 30,123 | 30,123 |
| `sec_05m4_fies.dta` | Food Insecurity Experience Scale (8 questions) | household | 30,123 | 30,123 |
| `sec_6a_consum_exp.dta` | **Consumption expenditure** (about 300 items) | household × item | 2,396,159 | 30,123 |
| `sec_7.dta` | Durable goods owned or sold (TV, fridge, car …) | household × item | 275,914 | 30,102 |
| `sec_8a.dta` | Transfers received and paid (remittances, zakat, BISP …) | household × item | 1,204,354 | 30,109 |
| `sec_9a.dta` | Property: land and buildings | household × property type | 149,868 | 29,981 |
| `sec_9b.dta` | Savings, gold, shares, loans | household × question | 632,119 | 30,108 |
| `sec_10a_agrisheet.dta` | Crop production and farm costs | household × item | 150,530 | 5,447 |
| `sec_10b_livestock.dta` | Livestock, animal products, costs | household × item | 60,704 | 5,953 |
| `sec_11ab_nonagri.dta` | Non-farm household businesses | business × item | 128,699 | 6,218 |

**About file sizes:** `sec_6a_consum_exp.dta` is 138 MB. It is stored on GitHub with Git LFS, which needs to be installed to download it properly. The same data is also inside `Stata-data-1.zip`.

---

## 7. Each section explained

### `section_info.dta`: interview details

- `fstatus`: interview status (1 = completed, 2 = partially refused, 3 = refused, 4 = not contacted). **Every household here has status 1 (completed).**
- `enum_day`, `enum_month`, `enum_year`: interview date.

### `plist_roster.dta`: who lives in the household (Section 1A)

This is the **master list of people**. Start here whenever you need age, sex or family relationships.

| Column | Meaning |
|---|---|
| `s1aq02` | Relation to head (1 head, 2 spouse, 3 son/daughter, 4 grandchild, 5 father/mother … 14 other) |
| `s1aq03` | Sex (1 male, 2 female) |
| `s1aq04` | Present (1) or temporarily absent (2) |
| `s1aq51` | Age in completed years (`s1aq52-54` = day/month/year of birth) |
| `s1aq06` | Marital status (1 never married, 2 married, 3 widowed, 4 divorced, 5 separated, 6 nikah done but rukhsati not yet) |
| `s1aq07/08/09` | `idc` of spouse / father / mother |
| `s1aq10` | Is a household member? (1 yes, 2 no). 556 people are coded "no". |
| `weight` | A copy of the household weight from `weight.dta` |

### `sec_1b_emp_income.dta`: work and income (Section 1B)

Covers everyone aged 10 and over.

- Whether the person works (`s1bq01`) and their employment status (`s1bq02`).
- Occupation and industry codes (`s1bq03`, `s1bq04`).
- **Cash earnings**: last month (`s1bq06`), last year (`s1bq08`), second job (`s1bq10`), other jobs (`s1bq11`), pensions (`s1bq13`).
- Gig and digital platform work, such as Uber, Careem, Daraz or TikTok (`s1bq14`-`s1bq16`).

### `sec_2ab_education.dta`: literacy and schooling (Sections 2A, 2B)

- Literacy: can read (`s2aq01`), can write (`s2aq02`), can do simple sums (`s2aq03`).
- School history: never attended, attended in the past, or currently attending (`s2bq01`), why never attended (`s2bq02`), highest grade completed (`s2bq05`), why they left (`s2bq06`), current school type and grade (`s2bq07`, `s2bq10`), distance to school (`s2bq11`).

### `sec_02c_ict.dta`: phones, computers and internet (Section 2C)

- Used or owns a mobile phone (`s2cq01`, `s2cq02`), used a computer (`s2cq03`).
- Used the internet (`s2cq05`), where (`s2cq06x`), on what device (`s2cq07x`), and how often (`s2cq08`).
- What the internet was used for (`s2cq09x`), online purchases (`s2cq10x`), how they paid (`s2cq11x`), and reasons for not using the internet (`s2cq14x`).
- Has a bank or digital account (`s2cq15`).

Many questions are **"tick all that apply"**, so each option gets its own column: `s2cq091`, `s2cq092`, … `s2cq0927`.

### Health: Sections 3A, 3B, 3C

- **3A Diarrhoea** (`Sec_03a`): for each young child, whether they had diarrhoea in the last 15 days, who was consulted, whether ORS was given, and feeding during the illness.
- **3B Immunisation** (`Sec_03b`): has a vaccination card, plus each vaccine (BCG, Penta 1-3, Pneumococcal 1-3, Polio 0-3, Rota, IPV, Typhoid, Measles 1-2), cost and distance.
- **3C** (`sec_03c_malaria`): for everyone, malaria/dengue in the last year, knowledge of symptoms, hepatitis testing and prevention, and TB history and knowledge.

### Women's sections: 4A to 4E (female questionnaire)

- **4A Pregnancy history:** marital status, age at marriage, number of sons and daughters born, living, and died, miscarriages and stillbirths.
- **4B Maternity history:** **one row per child ever born.** Sex, birth month and year, whether alive, and age at death if the child died. `ino` numbers the children of each woman.
- **4C Family planning:** for 10 methods (`a` to `j`), whether she has heard of it (`s4cq1x`), ever used it (`s4cq2x`), or uses it now (`s4cq3x`); reasons for not using any method, and satisfaction.
- **4D Pre- and post-natal care:** antenatal visits, tetanus injections, place of delivery (`s4dq09`), who assisted (`s4dq10`), post-natal check-up, and breastfeeding.
- **4E Decision making:** who decides on her education, paid work, marriage, birth control, and household purchases.

### Household conditions: Section 5 (4 files)

- **5M1 Housing** (`sec_05m1_housingchar`): ownership, dwelling type, rooms, floor/roof/wall materials, cooking, heating and lighting fuel. Ownership of internet, mobile, smartphone, computer, TV, radio (column `…a` = yes/no, `…b` = how many). Reasons for no internet, Lady Health Worker visits, distance to an all-season road and public transport.
- **5M2 Water and sanitation:** drinking water source (`s5m2q01`), water treatment, payment for water, toilet type (`s5m2q10`), shared toilet, sewerage connection, and hand washing.
- **5M3 Waste management:** how garbage is disposed of, distance to a bin, how often bins are emptied, and payment.
  > This file has **no `hhcode` column**. Create it with `prcode * 1000 + hhno`.
- **5M4 FIES (Food Insecurity Experience Scale):** 8 yes/no questions about the last 12 months (`q1` to `q8`), from "worried about not having enough food" to "went a whole day without eating". Codes are 1 = yes, 2 = no, 98 = don't know, 99 = refused. This is the standard international measure behind SDG indicator 2.1.2.

### Section 6A: consumption expenditure (`sec_6a_consum_exp.dta`)

This is the **largest and most important economic file**. It is used to measure spending, living standards and poverty.

Each row is one household and one item code `itc`. The codes follow the international **COICOP** classification of consumption items:

| `itc` starts with | Group | Example items |
|---|---|---|
| 111xx | Food: cereals, pulses, bakery | 11101 wheat, 11102 wheat flour, 11103 rice |
| 112xx, 113xx | Meat, fish | 11201 beef, 11203 chicken |
| 114xx | Milk, cheese, eggs | 11401 fresh milk, 11409 eggs |
| 115xx – 119xx | Oils, fruit, vegetables, sugar, spices | 11504 cooking oil, 11701 potato |
| 12xxx | Non-alcoholic drinks | 12101 tea |
| 220xx | Tobacco | 22001 cigarettes |
| 31xxx – 32xxx | Clothing and footwear | |
| 41xxx – 45xxx | Rent, water, electricity, gas, fuel | 45101 electricity, 45201 gas |
| 5xxxx | Furniture, appliances, household goods | |
| 6xxxx | Health | 61101 medicines, 62101 doctor fees |
| 7xxxx | Transport | 72201 petrol |
| 8xxxx | Communication | 83001 mobile bills |
| 9xxxx | Recreation and culture | |
| 10xxxx | Education fees | |
| 11xxxx | Restaurants and hotels | |
| 12xxxx | Personal care and miscellaneous | |

**What the columns mean** (from the questionnaire):

| Column | Meaning |
|---|---|
| `pp` | Where it was bought: 1 = retail shop, 2 = wholesale/sabzi mandi, 3 = online |
| `unit` | Unit of quantity |
| `q1`, `v1` | **Paid and consumed**: quantity and value (Rs) of what was **bought** |
| `q2`, `v2` | Received as **wages in kind** (for example, food given by an employer) |
| `q3`, `v3` | **Own production**: grown or made by the household and consumed |
| `q4`, `v4` | Received as **gift, assistance, dowry, inheritance** or other sources |

Total consumption of an item = `v1 + v2 + v3 + v4`.

**Different items use different time periods.** You must convert them to the same period, usually per month, before adding them up:

| Part | Items | Time period asked | Total row code |
|---|---|---|---|
| A | Perishable food: milk, meat, fruit, vegetables, spices, sugar | **last 14 days** | 1000 (page totals 1001-1003) |
| B | Staple food: cereals, pulses, oils, tea, etc. | **last month** | 2000 (2001-2003) |
| C | Tobacco, water, electricity, gas, fuel | **last month** | 4000 |
| D | Clothing, rent, repairs, health, education, transport, etc. | **last 12 months** | 5000 (5001-5004) |
| E | Durable goods: furniture, appliances, vehicles, jewellery | **last 12 months** | 6000 |

### Section 7: durable goods (`sec_7.dta`)

There are 35 items, such as TV, fridge, AC, washing machine, motorcycle, car, tractor and solar panel. For each:

- `s7m_a`: number owned **during the last year**
- `s7m_b`: number owned **now**
- `s7m_c`: amount received if any were sold (Rs)

Code 700 is the total row.

### Section 8A: transfers (`sec_8a.dta`)

Each row is one household and one question `code`. The amount is in **`c02`**.

- **Received (801-821):** committees, remittances from inside or outside Pakistan (and through bank, hundi or mobile banking), zakat, government and private assistance, insurance claims, inheritance, **BISP/Ehsaas** (820). Code 800 is the total.
- **Paid out (831-847):** committees, remittances sent, zakat paid, insurance premiums, dowry given. Code 850 is the total.

> Some codes hold a **code instead of an amount**: 803 and 833 (district), 809 and 839 (country), 810 and 840 (relationship). Do not add them up as rupees.

### Section 9A: property (`sec_9a.dta`)

Each row is one household and one property type: 901 agricultural land, 902 non-agricultural land, 903 residential building, 904 commercial building, 910 total.

The main columns are:

- `s9aq01`: owned during the last year?
- `s9aq02b`: acres
- `s9aq03a-d`: value if sold, received, purchased or given
- `s9aq04`: rent received
- `s9aq06`: expected sale value

The `code_9xx` / `code_3a` … columns are helper copies of the same answers in "wide" form. You can usually ignore them.

### Section 9B: savings, gold, shares and loans (`sec_9b.dta`)

Each row is one household and one question `code` (951-971). The answer is in `c02`.

- 951-954: savings
- 955-957: gold, silver and jewellery
- 958-962: shares and provident fund
- 963-970: loans owed, borrowed, repaid, lent
- 971: group insurance

> The value labels on `c02` (1 = household expenditure, 2 = others) apply **only to code 967** (purpose of the loan).

### Section 10A: agriculture (`sec_10a_agrisheet.dta`)

Only farming households appear here: **5,447 households**.

- Crop production (121 wheat, 122 cotton, 123 sugarcane, 124 rice, 125 maize … 132 by-products, **135 total**).
- Farm costs (136 seeds, 137 fertiliser, 138 pesticides, 139 water and fuel … 145 other, **150 total**).
- Columns: `s10c1` unit, `s10c2` quantity, `s10c3` value of total production, `s10c4` value given to the landlord, `s10c5` value kept by the household.

Codes 101-11x have **no labels** in the file. They cover land details; see Section 10 of the male questionnaire.

### Section 10B: livestock (`sec_10b_livestock.dta`)

5,953 households.

- Animals (151 cattle, 152 buffalo … 159 poultry, **165 total**).
- Animal products (166 eggs, 167 milk … 173 wool, **180 total**).
- Livestock costs (181 green fodder … 189 labour, **195 total**).
- Agricultural equipment rented out (196-198).

The value columns `s10c1`-`s10c6` have no labels. Check Section 10 of the male questionnaire for what each one means before using them.

### Section 11: non-farm businesses (`sec_11ab_nonagri.dta`)

6,218 households run a shop, workshop, transport service or similar. A person can have more than one business; `sheetno` numbers them.

- `ind_code`: the business's industry, using the 4-digit Pakistan Standard Industrial Classification. Examples: 4711 retail shop, 4921 passenger transport.
- Codes:
  - 201-211: operating costs (220 total)
  - 221-229: raw materials (230 total)
  - 231-232: stock
  - 241-245: other costs (250 total)
  - 251-259: products (265 total)
  - 266-278: receipts and sales (285 total)
  - 286-293: business assets, and how revenue is shared
- `s11a`-`s11d` hold the amounts. In about 99% of rows, `s11c = s11a × s11b`, which suggests a monthly amount × number of months = yearly amount. Confirm this against Section 11 of the male questionnaire before relying on it.

---

## 8. `weight.dta` in detail

This is the most important small file in the folder. If you skip it, **most of your results will be slightly wrong**, and some will be very wrong.

### 8.1 What is inside the file

It has two columns and 2,153 rows, one row per PSU:

| prcode | weight |
|---|---|
| 11021001 | 439.7 |
| 11021005 | 439.7 |
| 11021009 | 439.7 |
| 11022002 | 479.6 |
| … | … |

- `prcode`: the PSU code (see [Section 4.1](#41-prcode-the-psu-code-8-digits)).
- `weight`: the **sampling weight** for every household in that PSU.

All households in the same PSU share the same weight. The roster file has a copy of the same weight in its own `weight` column, and the values are identical.

### 8.2 What does the number mean?

> **A weight of 439.7 means: "this one household represents about 440 households in Pakistan."**

Think of it as a vote count. When you calculate an average, a household with weight 2,000 counts **ten times** as much as a household with weight 200, because it stands in for ten times as many real households.

Weights are always:

- **positive**, and usually much bigger than 1;
- **not normalised**: they do not add up to 1 or to the sample size. They add up to the **size of the population**.

### 8.3 Why do we need weights at all?

Because the sample is **not a mini copy of Pakistan**. PBS deliberately sampled some areas more heavily than others, so that small provinces and rural/urban groups have enough households to give reliable results on their own.

Here is the effect in this data:

| Province | Share of **sample** households/people (unweighted) | Share of **population** (weighted) |
|---|---:|---:|
| KP | 20.6% | 16.9% |
| Punjab (incl. Islamabad) | 42.6% | **53.9%** |
| Sindh | 26.1% | 23.1% |
| Balochistan | **10.7%** | 6.1% |
| **Rural** | 64.5% | 61.3% |
| **Urban** | 35.5% | 38.7% |

Balochistan makes up about 6% of Pakistan's population but 11% of the sample. Punjab is 54% of the population but only 43% of the sample.

If you compute a plain average over all households, **Balochistan counts almost twice as much as it should and Punjab too little**. The weights correct this.

### 8.4 Where does the weight come from?

PBS does not ship the exact formula with this file, but every survey weight is built from the same basic idea.

**Step 1: the chance of being picked.** Each household's probability of selection is:

```
P(household selected) = P(its PSU was chosen) × P(household chosen | PSU chosen)
```

**Step 2: weight = 1 ÷ that probability.**

```
weight = 1 / P(household selected)
```

**Example:** if a household had a 1-in-440 chance of being picked, its weight is 440. It "stands in" for itself and about 439 similar households that were not picked.

**Step 3: adjustments.** Survey agencies usually adjust the basic weight for households that could not be interviewed, and so that totals match known census counts.

The data confirms the weights are built this way. Adding up the weights gives totals very close to the **2023 Census**:

| | Sum of weights in this data | 2023 Census (approx.) |
|---|---:|---:|
| **Households** (sum over 30,123 households) | **40.1 million** | — |
| **Population** (sum over 184,564 people) | **240.6 million** | 241.5 million |
| KP population | 40.7 million | 40.9 million |
| Punjab + Islamabad population | 129.7 million | 130.0 million |
| Sindh population | 55.5 million | 55.7 million |
| Balochistan population | 14.8 million | 14.9 million |

This is a strong check that the weights work as expected.

### 8.5 What the weights look like

| Statistic | Value |
|---|---:|
| Number of PSUs | 2,153 |
| Smallest weight | 222.2 (urban KP) |
| Median weight | 1,499.2 |
| Average weight | 1,354.1 |
| Largest weight | 4,294.2 (rural Balochistan) |
| Different weight values | 269 |

Average weight by province and area:

| Province | Rural avg. weight | Urban avg. weight |
|---|---:|---:|
| KP | 1,444 | **431** |
| Punjab (incl. Islamabad) | 1,477 | **2,012** |
| Sindh | 841 | 1,708 |
| Balochistan | 844 | 645 |

How to read this:

- **A small weight means an area was over-sampled**: many interviews relative to its population. Urban KP is the most over-sampled.
- **A big weight means an area was under-sampled**: few interviews relative to its population. Urban Punjab is the most under-sampled.
- Weights differ within a stratum because of PPS selection, updated household lists, and adjustments.

### 8.6 How to use the weight, step by step

**Step 1: attach the weight.** Join `weight.dta` to your file using `prcode`. Every file has `prcode`, so this always works.

**Step 2: use the weight in every calculation that describes the population.**

| You want… | Unweighted (wrong for population) | Weighted (correct) |
|---|---|---|
| A **percentage** | count of "yes" ÷ number of rows | sum of weights of "yes" rows ÷ sum of all weights |
| An **average** | Σ x ÷ n | Σ (weight × x) ÷ Σ weight |
| A **total** (e.g. number of households) | n | Σ weight |

**Step 3: for person-level files, use the same household weight.** Every person gets their household's weight. That is why the sum over all people gives the population (about 241 million).

#### Example in Python

```python
import pandas as pd
import numpy as np

D = "HIES 2024_2025/Stata data/"
w = pd.read_stata(D + "weight.dta")
h = pd.read_stata(D + "sec_05m1_housingchar.dta", convert_categoricals=False)

h = h.merge(w, on="prcode", how="left")      # Step 1: attach weight
has_net = (h["s5m1q111a"] == 1)              # 1 = yes, household has internet

print(has_net.mean())                              # unweighted: 0.675
print(np.average(has_net, weights=h["weight"]))    # weighted:   0.697
print(h.loc[has_net, "weight"].sum())              # number of households with internet
```

#### Example in Stata

```stata
use "sec_05m1_housingchar.dta", clear
merge m:1 prcode using "weight.dta", keep(match) nogenerate

gen has_net = (s5m1q111a == 1)
mean has_net [pweight = weight]          // weighted estimate

* Better: declare the survey design once, then use svy: for correct standard errors
gen stratum = floor(prcode / 100000)     // first 3 digits = province + stratum
svyset prcode [pweight = weight], strata(stratum)
svy: mean has_net
svy: mean has_net, over(region)
```

#### Example: a person-level indicator (literacy)

```python
r = pd.read_stata(D + "plist_roster.dta", convert_categoricals=False)
e = pd.read_stata(D + "sec_2ab_education.dta", convert_categoricals=False)

e = e.merge(r[["hhcode", "idc", "s1aq51"]], on=["hhcode", "idc"])   # add age
e = e.merge(w, on="prcode")                                          # add weight
e10 = e[e["s1aq51"] >= 10]                                           # age 10+

literate = (e10["s2aq01"] == 1) & (e10["s2aq02"] == 1)               # can read AND write
print(np.average(literate, weights=e10["weight"]))
```

### 8.7 How much difference does weighting make?

All of these were computed from this data:

| Indicator | Unweighted | **Weighted** | Difference |
|---|---:|---:|---:|
| Households with internet (Pakistan) | 67.5% | **69.7%** | +2.2 points |
| Households with internet (Sindh) | 59.6% | **66.7%** | **+7.1 points** |
| Literacy, age 10+, can read and write | 59.7% | **63.1%** | +3.4 points |
| Average household size | 6.11 | **5.98** | −0.13 people |

The differences are biggest within provinces where the sample was spread very unevenly between rural and urban areas, such as Sindh.

### 8.8 When to use the weight, and when not to

| Situation | Use weight? |
|---|---|
| Percentages, averages, totals describing Pakistan or a province | **Yes, always** |
| Comparing groups (rural vs urban, men vs women) | **Yes** |
| Tables meant to match the official PBS report | **Yes** |
| Counting how many **interviews** you have ("n = 30,123") | No |
| Data cleaning and checking (looking for errors) | No |
| Regression or machine learning | Usually yes for describing the population. Many researchers report both weighted and unweighted results. Discuss with your supervisor. |

### 8.9 Standard errors and confidence intervals

The weight alone gives correct **estimates** (the numbers themselves). To get correct **margins of error**, the software also needs to know about the **strata** and **PSUs**.

Households in the same village tend to be similar, so the sample contains less independent information than 30,123 separate random households would. If you ignore this, your margins of error will be too small.

- In Stata, use `svyset prcode [pweight=weight], strata(stratum)` as shown above, then put `svy:` in front of your commands.
- In R, use the `survey` package: `svydesign(ids = ~prcode, strata = ~stratum, weights = ~weight, data = ...)`.
- In Python, use the `samplics` package, or use the weights directly if you only need the estimates.

---

## 9. Common mistakes and traps

1. **Forgetting the weight.** See [Section 8](#8-weightdta-in-detail). This is the most common mistake.
2. **Joining on `hhno` alone.** It is not unique. Use `hhcode`, or `prcode` + `hhno`.
3. **Joining persons on `idc` alone.** Use `hhcode` + `idc`.
4. **Adding up total rows in item files.** Remove or use only the total codes:
   - Section 6A: 1000, 1001-1003, 2000, 2001-2003, 4000, 5000, 5001-5004, 6000, plus group headers ending in `000`.
   - Section 7: 700. Section 8A: 800 and 850. Section 9A: 910.
   - Section 10A: 135 and 150. Section 10B: 165, 180 and 195.
   - Section 11: 220, 230, 250, 265 and 285.
5. **Mixing time periods in Section 6A.** Convert 14-day, monthly and yearly items to the same period before adding them.
6. **Treating codes as amounts.** For example, district or country codes in Section 8A, or the loan purpose in Section 9B.
7. **"Don't know" codes.** Codes like 98 and 99 mean "don't know" or "refused" (for example in FIES, and in parent IDs). Exclude them before calculating averages.
8. **Missing values have a meaning.** A blank often means "question not asked because it did not apply" (a skip). It does not mean zero. Check the questionnaire's skip instructions ("→ Go to Q…").
9. **Islamabad is inside Punjab.** Use the first digit of `prcode` = 6 to separate it.
10. **`quater` vs `quarter`.** The column name is spelled differently in different files.
11. **`sec_05m3_wastemanagment.dta` has no `hhcode`.** Build it from `prcode*1000 + hhno`.
12. **`hhcode` is stored as a float.** Convert it to an integer before joining or exporting, so it doesn't turn into `1.1021e+10` in Excel.
13. **Two label errors in the original files.** The numbers are fine, but some text labels are wrong:
    - In `Sec_04e_decisionmaking.dta`, the `region` labels are reversed (1 = "urban", 2 = "rural"). The values themselves follow the normal coding (1 = rural, 2 = urban), as `prcode` confirms.
    - In `sec_05m4_fies.dta`, the labels say 98 = refused and 99 = don't know. The questionnaire says **98 = don't know, 99 = refused**. Questions q6-q8 have no labels for 98/99 at all.

    The CSV versions (see below) correct both.

---

## CSV versions of these files

The folder `CSV data/` has a readable CSV copy of every file in `Stata data/`, made by `stata_to_csv.py`:

- Coded answers are replaced by their text (e.g. `male`, `currently married`, `yes`).
- Item codes (`itc`, `code`, `ind_code`) keep the number and get an extra `_label` column with the item name.
- `_codebook.csv` lists every column of every file with its description and the meaning of each code.

**Excel limit:** Excel can show at most 1,048,576 rows. `sec_6a_consum_exp.csv` (2.4 million rows) and `sec_8a.csv` (1.2 million rows) are too long for Excel. Open them with Python, R, or a text editor instead.

---

## 10. Glossary

| Term | Meaning |
|---|---|
| **HIES** | Household Integrated Economic Survey, run by PBS |
| **PSLM** | Pakistan Social and Living Standards Measurement, the survey programme HIES belongs to |
| **PBS** | Pakistan Bureau of Statistics |
| **Microdata** | Data with one row per unit (household or person), as opposed to summary tables |
| **Sample** | The households actually interviewed (30,123) |
| **Population** | Everyone the survey describes (about 40 million households, about 241 million people) |
| **Stratum / strata** | Groups of areas sampled separately so that each is represented |
| **PSU** | Primary Sampling Unit: a village (rural) or enumeration block (urban), chosen at the first stage |
| **Enumeration block** | A small census area in a city, about 200-250 households |
| **PPS** | Probability Proportional to Size: bigger PSUs are more likely to be chosen |
| **Sampling weight** | How many population units one sampled unit represents; 1 ÷ probability of selection, with adjustments |
| **Weighted estimate** | A result where each row counts in proportion to its weight |
| **Design effect / clustering** | The loss of precision because sampled households are grouped in PSUs |
| **Value label** | Text attached to a numeric code (e.g. 1 = "male") |
| **Long format** | One row per household × item (the Section 6-11 files) |
| **COICOP** | International classification of consumption items, used for Section 6A codes |
| **FIES** | Food Insecurity Experience Scale, 8 yes/no questions on food hardship |
| **BISP** | Benazir Income Support Programme (cash transfers), code 820 in Section 8A |
| **Recall period** | The time window a question asks about (14 days, 1 month, 1 year) |

---

## Where to look for more detail

All of these are in this folder (`HIES 2024_2025/`):

| File | Use it for |
|---|---|
| `Male-Questionnaire-HIES-2024-25-English.pdf` | Exact wording and answer codes for the roster (males), Sections 1B, 2, 5, 6 (Parts C-E), 7, 8, 9, 10, 11 |
| `Female-Questionnaire-HIES-2024-25-English.pdf` | Roster (females and children), Sections 3, 4, 6 (Parts A-B) |
| `Manual-of-Instruction-HIES-2024-25.pdf` | Definitions and interviewer instructions for every question |
| `HIES-2024-25-Report-Final-2.pdf` | Official results, to check your own numbers against |
| `CODING-HIES-2024-25.doc`, `Coding-Scheme-HIES-2024-25-RUralUrban.xlsx` | Code lists (occupations, industries, areas) |
