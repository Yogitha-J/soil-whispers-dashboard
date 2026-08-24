import pandas as pd
import numpy as np
import json

pd.set_option('display.width', 140)

# ============================================================
# DATASET 1: Crop Recommendation (soil + climate -> crop label)
# ============================================================
df1 = pd.read_csv("data/crop_recommendation.csv")
report = {}

report['ds1_shape_raw'] = df1.shape
report['ds1_dtypes'] = df1.dtypes.astype(str).to_dict()
report['ds1_missing'] = df1.isnull().sum().to_dict()
report['ds1_duplicates'] = int(df1.duplicated().sum())
report['ds1_crops'] = df1['label'].nunique()
report['ds1_rows_per_crop_min_max'] = (int(df1['label'].value_counts().min()), int(df1['label'].value_counts().max()))

# Cleaning: drop exact duplicate rows, check impossible values (e.g. negative N/P/K, humidity>100, ph out of 0-14)
before = len(df1)
df1_clean = df1.drop_duplicates().copy()
impossible = df1_clean[
    (df1_clean['N'] < 0) | (df1_clean['P'] < 0) | (df1_clean['K'] < 0) |
    (df1_clean['humidity'] < 0) | (df1_clean['humidity'] > 100) |
    (df1_clean['ph'] < 0) | (df1_clean['ph'] > 14) |
    (df1_clean['rainfall'] < 0)
]
report['ds1_impossible_value_rows'] = int(len(impossible))
df1_clean = df1_clean.drop(impossible.index)

# Outlier flagging via IQR on rainfall and temperature (flag, not drop -- agronomically real extremes exist)
def iqr_outliers(s):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
    return ((s < lo) | (s > hi)).sum()

report['ds1_rainfall_outliers_iqr'] = int(iqr_outliers(df1_clean['rainfall']))
report['ds1_temperature_outliers_iqr'] = int(iqr_outliers(df1_clean['temperature']))
report['ds1_rows_after_cleaning'] = len(df1_clean)

report['ds1_describe'] = df1_clean.describe().round(2).to_dict()

# Preliminary analysis: mean N/P/K/rainfall by crop, for a few key crops farmers commonly ask about
key_crops = ['rice', 'maize', 'cotton', 'coffee', 'banana', 'chickpea']
summary_by_crop = df1_clean[df1_clean['label'].isin(key_crops)].groupby('label')[
    ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
].mean().round(1)
report['ds1_summary_by_key_crop'] = summary_by_crop.to_dict(orient='index')

corr1 = df1_clean[['N','P','K','temperature','humidity','ph','rainfall']].corr().round(2)
report['ds1_correlation'] = corr1.to_dict()

df1_clean.to_csv("data/crop_recommendation_cleaned.csv", index=False)

# ============================================================
# DATASET 2: State/District crop yield time series (2010-2017)
# ============================================================
df2 = pd.read_csv("data/crops_state_yield.csv")
report['ds2_shape_raw'] = df2.shape
report['ds2_states'] = df2['State Name'].nunique()
report['ds2_years'] = sorted(df2['Year'].unique().tolist())
report['ds2_missing_top'] = df2.isnull().sum().sort_values(ascending=False).head(8).to_dict()

# Focus on RICE and WHEAT and COTTON yield/production -- most widely grown, matches business questions
cols_keep = ['Dist Code','Year','State Name','Dist Name',
             'RICE AREA (1000 ha)','RICE PRODUCTION (1000 tons)','RICE YIELD (Kg per ha)',
             'WHEAT AREA (1000 ha)','WHEAT PRODUCTION (1000 tons)','WHEAT YIELD (Kg per ha)',
             'COTTON AREA (1000 ha)','COTTON PRODUCTION (1000 tons)','COTTON YIELD (Kg per ha)']
df2_focus = df2[cols_keep].copy()

before2 = len(df2_focus)
# Cleaning: many "0" entries represent "crop not grown in that district" not a true missing value / data error.
# Treat 0 yield with >0 area as a data inconsistency (should not happen); flag those.
inconsistent_rice = df2_focus[(df2_focus['RICE AREA (1000 ha)'] > 0) & (df2_focus['RICE YIELD (Kg per ha)'] == 0)]
report['ds2_rice_inconsistent_rows'] = int(len(inconsistent_rice))

# Drop exact duplicate district-year rows if any
dup2 = int(df2_focus.duplicated(subset=['Dist Code','Year']).sum())
report['ds2_duplicate_dist_year'] = dup2
df2_focus = df2_focus.drop_duplicates(subset=['Dist Code','Year'])

# Outlier check on yield fields (values of 0 are legitimate "not grown here"; exclude 0s before IQR check)
def iqr_outliers_nonzero(s):
    s2 = s[s > 0]
    q1, q3 = s2.quantile(0.25), s2.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
    return int(((s2 < lo) | (s2 > hi)).sum())

report['ds2_rice_yield_outliers'] = iqr_outliers_nonzero(df2_focus['RICE YIELD (Kg per ha)'])
report['ds2_wheat_yield_outliers'] = iqr_outliers_nonzero(df2_focus['WHEAT YIELD (Kg per ha)'])
report['ds2_rows_after_cleaning'] = len(df2_focus)

# Preliminary analysis: national trend of avg rice & wheat yield per year (only rows where crop is actually grown)
rice_grown = df2_focus[df2_focus['RICE AREA (1000 ha)'] > 0]
wheat_grown = df2_focus[df2_focus['WHEAT AREA (1000 ha)'] > 0]
yearly_rice = rice_grown.groupby('Year')['RICE YIELD (Kg per ha)'].agg(['mean','median','std']).round(1)
yearly_wheat = wheat_grown.groupby('Year')['WHEAT YIELD (Kg per ha)'].agg(['mean','median','std']).round(1)
report['ds2_yearly_rice_yield'] = yearly_rice.to_dict(orient='index')
report['ds2_yearly_wheat_yield'] = yearly_wheat.to_dict(orient='index')

# Top 5 states by average rice yield (2010-2017)
state_rice = rice_grown.groupby('State Name')['RICE YIELD (Kg per ha)'].mean().sort_values(ascending=False).round(1)
report['ds2_top5_states_rice_yield'] = state_rice.head(5).to_dict()
report['ds2_bottom5_states_rice_yield'] = state_rice.tail(5).to_dict()

df2_focus.to_csv("data/crops_state_yield_cleaned.csv", index=False)

with open("analysis_report.json", "w") as f:
    json.dump(report, f, indent=2, default=str)

print("DONE")
print(json.dumps({k: report[k] for k in ['ds1_shape_raw','ds1_duplicates','ds1_impossible_value_rows',
      'ds1_rainfall_outliers_iqr','ds1_rows_after_cleaning','ds2_shape_raw','ds2_states','ds2_years',
      'ds2_rice_inconsistent_rows','ds2_duplicate_dist_year','ds2_rice_yield_outliers','ds2_rows_after_cleaning']}, indent=2))
