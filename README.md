# PSLM Machine Learning & Social Network Analysis

Master's project using data from the **Pakistan Social and Living Standards Measurement (PSLM)** survey published by the Pakistan Bureau of Statistics.

## Goals
- **Text processing:** extract district-level tables from the PSLM report PDFs into a clean dataset.
- **Machine learning:** predict district education deprivation (e.g. out-of-school children, Table 2.15) from living-condition indicators — classification, regression and ranking, plus clustering.
- **Social network analysis:** district similarity networks, indicator correlation networks and district–indicator bipartite networks; community detection and centrality.

## Data in this repository
| Files | Content |
|---|---|
| `Table-*.pdf` | Individual tables from the PSLM 2019-20 District Level report (education, ICT, health, disability, migration, housing, perception, food insecurity) |
| `PSLM_2019_20_District_Level.pdf`, `Key_Finding_Report_...2019-20.pdf` | PSLM 2019-20 district report and key findings |
| `PSLM_2014-15_...pdf`, `report-13-14_merged*.pdf` | PSLM 2014-15 and 2013-14 reports |
| `1merged_document*.pdf`, `merged_document*.pdf`, `report_pslm0*.pdf`, `pslms-2004-05.pdf` | Earlier rounds (2004-05 to 2010-11) |

Source: [Pakistan Bureau of Statistics](https://www.pbs.gov.pk/).
