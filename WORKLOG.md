# Work Log

Day-by-day record of work on the PSLM project. Newest entries at the top.

<!--
Template for a new day (copy above the latest entry):

## YYYY-MM-DD
### Done
- 
### Files changed
- 
### Findings / decisions
- 
### Next steps
- 
-->

## 2026-11-01

### Done
- Collected PSLM report PDFs for rounds 2004-05, 2006-07, 2008-09, 2010-11, 2013-14, 2014-15 and 2019-20.
- Reviewed the reports: they contain aggregated district-level tables (percentages by urban/rural and male/female), not household records.
- Assessed feasibility of machine learning and social network analysis on the data.
- Ran a small SNA test: district similarity network on 21 Punjab districts using PSLM 2019-20 Table 2.1 (5 communities, modularity 0.587, communities follow north–south geography).
- Searched for other PSLM data: household-level microdata is available from PBS, opendata.com.pk (2019-20 Stata files) and the IHSN catalog.
- Added 32 individual 2019-20 district tables (`Table-*.pdf`) covering education, ICT, health, disability, migration, housing, perception and food insecurity.
- Created the Git repository and pushed it to GitHub: <https://github.com/Khalid-Siddiqi/PSLM->

### Files changed
- Added all report PDFs and `Table-*.pdf` files.
- Added `README.md` and `.gitignore`.
- Added `DATASET_INFO.md` (description of the data and possible analyses).
- Added `WORKLOG.md` (this file).

### Findings / decisions
- Unit of analysis: district (about 120 districts in 2019-20) → classical ML, not deep learning.
- Main ML question: predict out-of-school children aged 5–16 (Table 2.15) from living-condition indicators; exclude other education tables to avoid leakage.
- Table 6.1 (migration) has no origin–destination flows, so it cannot form a migration network.
- Networks will be constructed from similarity: district similarity, indicator correlation, and district–indicator two-mode networks.
- Duplicate files: `report-13-14_merged (1).pdf` and one of the two `Table-6.1-...` files.

### Next steps
- Extract all 2019-20 tables into one clean district × indicator dataset.
- Normalise district names across tables.
- Build the first ML model and the SNA networks on the merged dataset.
