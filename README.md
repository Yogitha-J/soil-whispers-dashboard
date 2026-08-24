# Soil Whispers

An agribusiness data visualization platform concept, developed as a 4-week internship project for the YuvaIntern program.

## Project structure

```
soil-whispers-repo/
├── week1_strategic_plan/
│   └── Soil_Whispers_Strategic_Plan.docx
├── week2_data_analysis/
│   ├── Soil_Whispers_Week2_Data_Analysis.docx
│   ├── analyze.py
│   └── data/
│       ├── crop_recommendation_cleaned.csv
│       └── crops_state_yield_cleaned.csv
└── week3_dashboard/
    ├── Soil_Whispers_Week3_Dashboard_Design.docx
    ├── soil_whispers_dashboard.html   ← the actual working dashboard
    ├── aggregations.js                ← the data logic, as a standalone testable module
    ├── validate.js                    ← proves the JS logic matches the Week 2 pandas output
    └── runtime_check.js               ← runs the real dashboard code headlessly and checks it
```

## Week 3: Real Code, Not a Mockup

**`soil_whispers_dashboard.html` is a working, interactive dashboard.** Double-click it, or open it in any browser. No server, no build step, no internet connection needed. Everything (both datasets, Plotly.js, PapaParse) is bundled into that one ~5MB file.

It has two views (Farmer / Agronomist, matching the Week 1 target users), each with live dropdown filters that recompute every chart, KPI card, and table on the fly, straight from the embedded CSV data.

### Why HTML/Plotly.js instead of a native Tableau file

The internship role specifies Tableau, but the development environment used to build this had no Tableau Desktop installed. Rather than submit a static image and call it a Tableau screenshot, this dashboard is built with Plotly.js, a charting library whose feature set maps directly onto Tableau's, so the design decisions transfer directly. `week3_dashboard/Soil_Whispers_Week3_Dashboard_Design.docx` includes a full element-by-element translation table (dual-axis charts → Tableau dual-axis, dashboard filter → Tableau Parameter, etc.) for building the native `.twbx` version.

### How the code was verified

`aggregations.js` contains the actual data-processing functions used by the dashboard (Pearson correlation, yearly trend, state ranking, quantiles for box plots). Before wiring them into the UI, they were tested in Node.js (`validate.js`) against numbers already independently verified by pandas in the Week 2 analysis:

| Metric | Week 2 (pandas) | Dashboard (JavaScript) |
|---|---|---|
| Rice yield growth, 2010→2017 | +20.9% | +20.9% |
| Top state, avg rice yield | Tamil Nadu, ~3,940 kg/ha | Tamil Nadu, 3,942 kg/ha |
| Bottom state, avg rice yield | Maharashtra, ~1,400 kg/ha | Maharashtra, 1,400 kg/ha |
| Rice mean rainfall requirement | ~236.2 mm | 236.2 mm |
| Strongest soil/climate correlation | P–K, r ≈ 0.74 | P–K, r = 0.74 |

`runtime_check.js` goes a step further: it stubs out the DOM and Plotly, then actually executes the dashboard's real `init()`, `renderFarmer()`, and `renderAgro()` functions (extracted straight from the HTML file) to catch runtime errors and confirm every chart receives correctly-shaped, non-empty data, including after simulated filter changes.

To re-run the checks yourself:
```bash
cd week3_dashboard
npm install papaparse
node validate.js        # aggregation math vs. pandas
node runtime_check.js   # full dashboard logic, stubbed DOM
```

## Week 1: Strategic Plan

Defines objectives, scope, methodology, KPIs, target users, and public data strategy. Includes a scoping decision to treat plant-bioacoustics as a Year 2+ research track rather than a core Year 1 feature, since the science is currently lab-validated only.

## Week 2: Data Gathering, Cleaning, and Preliminary Analysis

Two real public datasets:

1. **Crop Recommendation Dataset** (2,200 records): soil nutrients (N, P, K), temperature, humidity, pH, rainfall across 22 crops.
2. **District-Level Crop Yield Dataset, India (2010–2017)**: area, production, and yield for rice, wheat, cotton, and other crops across 20 states.

`analyze.py` reproduces the full cleaning and analysis pipeline (duplicate checks, structural-zero handling, IQR outlier flagging). The cleaned CSVs in `data/` are its actual output.

```bash
cd week2_data_analysis
pip install pandas numpy
python analyze.py
```

## Data Sources

- Crop Recommendation Dataset, mirrored at: https://github.com/AbhishekKandoi/Crop-Yield-Prediction-based-on-Indian-Agriculture
- Crop Datasets for All Indian States (2010–2017): https://github.com/nileshely/Crop-Datasets-for-All-Indian-States

## Status

- [x] Week 1: Strategic Plan
- [x] Week 2: Data Gathering, Cleaning, and Preliminary Analysis
- [x] Week 3: Visualization Design and Dashboard Development (working code)
- [ ] Week 4: Evaluation, Refinement, and Presentation
