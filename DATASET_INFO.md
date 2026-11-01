# Dataset Overview: What Is Possible

This document describes the PSLM data in this repository, its limitations, and what can be done with it for the three project components: **text processing**, **machine learning** and **social network analysis (SNA)**.

---

## 1. What the data is

The **Pakistan Social and Living Standards Measurement (PSLM)** survey is run by the Pakistan Bureau of Statistics (PBS). It measures social indicators (education, health, housing, water and sanitation, ICT, food security) at national, provincial and district level.

This repository contains **published report PDFs**, not raw household records. Every number is an aggregated percentage for a province or district, usually split by **urban/rural** and **male/female**.

### Files

| Group | Files | Content |
|---|---|---|
| **2019-20 district tables** (main dataset) | `Table-*.pdf` (31 distinct tables) | One table per indicator, about 120 districts across Punjab, Sindh, Khyber Pakhtunkhwa and Balochistan |
| 2019-20 full report | `PSLM_2019_20_District_Level.pdf`, `Key_Finding_Report_...2019-20.pdf` | Full district report and key findings |
| 2013-14 and 2014-15 | `PSLM_2014-15_...pdf`, `report-13-14_merged.pdf` | National/provincial/district reports |
| Earlier rounds | `pslms-2004-05.pdf`, `merged_document.pdf` (2004-05), `report_pslm06_07.pdf`, `merged_document-2.pdf` (2006-07), `report_pslm08_09.pdf`, `1merged_document.pdf` (2008-09), `1merged_document-1.pdf` (2010-11) | Older rounds for comparisons over time |

Duplicates: `report-13-14_merged (1).pdf` is identical to `report-13-14_merged.pdf`, and the two `Table-6.1-...` files are identical.

### Topics in the 2019-20 tables

| Topic | Tables | Indicators |
|---|---|---|
| Education | 2.1, 2.3a, 2.6a, 2.10a, 2.11a, 2.12a, 2.13a, 2.14b, 2.15 | Ever attended school, gross/net enrolment (primary, middle, matric), adult literacy, **out-of-school children aged 5–16**, district rank |
| ICT | 3.1, 3.2, 3.3 | Households with computer/smartphone/internet, mobile ownership, internet use |
| Health | 4.4, 4.5, 4.6, 4.8, 4.9, 4.11, 4.12 | Immunization, child diarrhoea and its treatment, antenatal/postnatal care, place of delivery and who assisted |
| Disability | 5.2, 5.3 | Functional limitation, overall and by age group |
| Migration | 6.1 | Native vs. migrated population (within and between provinces) |
| Housing and utilities | 7.1, 7.2, 7.3, 7.8, 7.9 | Drinking water source, toilet type, solid waste disposal, lighting and cooking fuel |
| Perception and satisfaction | 8.2, 8.3 | Economic situation compared with last year, satisfaction with health units, schools, police and other services |
| Food insecurity | 9.1 | Moderate/severe food insecurity (FIES scale), with margins of error |

---

## 2. Limitations

- **Aggregated, not household-level.** The unit of analysis is the **district**. With about 120 districts in 2019-20, the dataset is small: suited to classical ML, not deep learning.
- **No built-in relationships.** There are no ties between people or districts. Any network has to be **constructed** from the data (see Section 5).
- **Table 6.1 has no origin–destination flows.** It gives the percentage of migrants per district, not where they came from, so it cannot form a migration network.
- **PDF extraction is messy.** In several tables (e.g. 6.1, 7.2, 8.2) numbers shift into the wrong columns or rows when the PDF is converted to text.
- **District names and boundaries change.** Spellings differ between tables (e.g. "Bhawal Nagar" / "Bahawalnager" / "Bahawalnagar", "Jehlum" / "Jhelum"), and some districts were split or created between rounds (e.g. Karachi into Korangi and others).

---

## 3. Text processing

Text processing is required before any analysis, because all the data sits inside PDFs.

1. **Table extraction.** Convert each PDF table into rows and columns, using each number's position on the page (pdftotext `-bbox`, pdfplumber or camelot) to fix the column drift.
2. **Structure handling.** Separate Urban/Rural sub-rows, and flatten nested tables (e.g. Table 4.11 lists delivery place and assistant under each district).
3. **Name normalisation.** Match district names across tables and survey rounds with fuzzy string matching plus a manual lookup table.
4. **Merging.** Join all tables into one **district × indicator** dataset (about 120 rows × 100+ columns).
5. *(Optional)* **Narrative mining.** Extract statements like *"Lahore with 34 percent is at bottom"* from the report text and check them against the extracted tables.

---

## 4. Machine learning

### Main prediction problem
**Can a district's living conditions predict its education deprivation?**

- **Target:** percentage of out-of-school children aged 5–16 (Table 2.15).
- **Features:** ICT, health, housing and utilities, food insecurity, migration, satisfaction and disability indicators.
- **Leakage rule:** exclude the other education tables (2.1–2.14). They nearly mirror the target and would inflate accuracy.

| Task type | Formulation | Label |
|---|---|---|
| **Classification** | High / Medium / Low deprivation | Tertiles of the out-of-school percentage |
| **Regression** | Predict the exact out-of-school percentage | The value itself |
| **Ranking** | Predict a district's rank | The **RANK** column already printed in Table 2.15 |
| **Unsupervised** | Cluster districts into development types (K-means, hierarchical); build a composite index (PCA) | None |

**Alternative targets:** food insecurity (Table 9.1), full immunization (Table 4.5), adult literacy (Table 2.14b).

**Suggested models:** logistic/linear regression, Random Forest, XGBoost, SVM. Use cross-validation because the dataset is small, and use feature importance (or SHAP values) to show which conditions matter most.

### Over time (optional extension)
The older rounds share several indicators (enrolment, immunization, toilet, water). After matching districts, a model could predict **2019-20 status from 2014-15 values**.

---

## 5. Social network analysis

The networks are built from similarities in the data.

### 5.1 District similarity network
- **Nodes:** districts. **Edges:** each district links to its *k* most similar districts (distance over the indicators).
- **Analysis:** community detection (Louvain), degree and betweenness centrality, modularity.

**Example (already tested):** PSLM 2019-20 Table 2.1 (% ever attended school), 21 Punjab districts, *k* = 3:

```
Nodes: 21  Edges: 38  Density: 0.181
Bridge districts (betweenness): Layyah 0.57, Bhakhar 0.39, Attock 0.36, Gujranwala 0.27

Communities (Louvain), modularity 0.587:
  avg female schooling 72%  -> Chakwal, Gujranwala, Gujrat, Jehlum            (north)
  avg female schooling 62%  -> Attock, Faisalabad, Hafizabad, M.Bahauddin
  avg female schooling 53%  -> Jhang, Kasur, Khanewal, Layyah, Multan
  avg female schooling 44%  -> Khushab, Mianwali
  avg female schooling 40%  -> Bahawalnagar, Bahawalpur, Bhakhar, Chiniot, DG Khan, Lodhran  (south)
```

The communities follow geography (north ahead, south behind) even though the network was never given location data.

### 5.2 Indicator correlation network
- **Nodes:** indicators. **Edges:** strong correlation across districts (e.g. internet use, female literacy and flush toilets rising together).
- **Analysis:** centrality identifies the "hub" indicators of deprivation; communities show which indicators form bundles.

### 5.3 District–indicator two-mode network
- **Nodes:** districts and indicators. **Edges:** a district links to the indicators where it is badly deprived.
- **Analysis:** project onto districts to find districts with the same problems, or onto indicators to find deprivations that occur together.

### 5.4 Change over time (optional)
Build the similarity network for each round and track which districts move between communities from 2004 to 2019.

---

## 6. Proposed pipeline

```
PDF tables ──► Text processing ──► District × indicator dataset
                                         │
                       ┌─────────────────┴─────────────────┐
                       ▼                                   ▼
              Social network analysis              Machine learning
         (similarity / correlation networks,   (classification, regression,
          communities, centrality)              ranking, clustering)
                       │                                   ▲
                       └──── community & centrality ───────┘
                             used as extra ML features
```

Using SNA results (community membership, centrality) as ML features ties the components together and lets us test whether network structure improves prediction.

---

## 7. Other PSLM data (household-level microdata)

PBS also publishes the raw survey records, which allow person/household-level ML (hundreds of thousands of rows, e.g. "is this child out of school?") and kinship networks from household rosters (relationship to household head).

- PSLM District Level 2019-20 microdata (Stata): <https://opendata.com.pk/dataset/pslm-district-level-survey-2019-20>
- PBS microdata and data requests: <https://www.pbs.gov.pk/>
- Variable dictionaries for several rounds: <https://catalog.ihsn.org/catalog/9548>

Access terms should be checked for each source before use.
