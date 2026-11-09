# PSLM Machine Learning & Social Network Analysis

Master's project using data from the **Pakistan Social and Living Standards Measurement (PSLM)** survey published by the Pakistan Bureau of Statistics.

## Goals
- **Text processing:** extract district-level tables from the PSLM report PDFs into a clean dataset.
- **Machine learning:** predict district education deprivation (e.g. out-of-school children, Table 2.15) from living-condition indicators — classification, regression and ranking, plus clustering.
- **Social network analysis:** district similarity networks, indicator correlation networks and district–indicator bipartite networks; community detection and centrality.

## Data in this repository
All source PDFs are in `data/raw/`, with one folder per survey round. The folder name says whether the round is **district** level or **provincial** level.

```
data/raw/
├── pslm_2019-20_district/          ← main dataset
│   ├── reports/                    full district report + key findings
│   └── tables/                     individual district tables, by topic
│       ├── 02_education/
│       ├── 03_ict/
│       ├── 04_health/
│       ├── 05_disability/
│       ├── 06_migration/
│       ├── 07_housing_utilities/
│       ├── 08_perception_satisfaction/
│       └── 09_food_insecurity/
├── pslm_2014-15_district/
├── pslm_2013-14_provincial/
├── pslm_2010-11_district/
├── pslm_2008-09_district/          district report + national/provincial report
├── pslm_2006-07_district/          district report + national/provincial report
└── pslm_2004-05_district/          district report + national/provincial report
```

See [DATASET_INFO.md](DATASET_INFO.md) for a full description of the data and what can be done with it.

Source: [Pakistan Bureau of Statistics](https://www.pbs.gov.pk/).
