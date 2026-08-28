import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams.update({"font.size": 11, "axes.titleweight": "bold"})
GREEN = "#2E7D32"

df1 = pd.read_csv("data/crop_recommendation.csv")
df2 = pd.read_csv("data/crops_state_yield.csv")

rice_grown = df2[df2['RICE AREA (1000 ha)'] > 0]
wheat_grown = df2[df2['WHEAT AREA (1000 ha)'] > 0]
yearly_rice = rice_grown.groupby('Year')['RICE YIELD (Kg per ha)'].mean()
yearly_wheat = wheat_grown.groupby('Year')['WHEAT YIELD (Kg per ha)'].mean()

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(yearly_rice.index, yearly_rice.values, marker='o', color=GREEN, label='Rice')
ax.plot(yearly_wheat.index, yearly_wheat.values, marker='s', color="#F9A825", label='Wheat')
ax.set_title("Average Yield Trend, 2010\u20132017 (India, district-level data)")
ax.set_xlabel("Year"); ax.set_ylabel("Yield (Kg per hectare)")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("chart1_yield_trend.png", dpi=150); plt.close()

state_rice = rice_grown.groupby('State Name')['RICE YIELD (Kg per ha)'].mean().sort_values(ascending=False)
top5 = state_rice.head(5); bottom5 = state_rice.tail(5)
combo = pd.concat([top5, bottom5])
colors = [GREEN]*5 + ["#C62828"]*5
fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.barh(combo.index[::-1], combo.values[::-1], color=colors[::-1])
ax.set_title("Highest vs Lowest Average Rice Yield by State (2010\u20132017)")
ax.set_xlabel("Average Yield (Kg per hectare)")
plt.tight_layout(); plt.savefig("chart2_state_comparison.png", dpi=150); plt.close()

key_crops = ['rice', 'maize', 'cotton', 'coffee', 'banana', 'chickpea']
sub = df1[df1['label'].isin(key_crops)]
order = sub.groupby('label')['rainfall'].mean().sort_values(ascending=False).index
fig, ax = plt.subplots(figsize=(7, 4))
sns.boxplot(data=sub, x='label', y='rainfall', order=order, color=GREEN, ax=ax)
ax.set_title("Typical Rainfall Range by Crop")
ax.set_xlabel(""); ax.set_ylabel("Rainfall (mm)")
plt.tight_layout(); plt.savefig("chart3_rainfall_by_crop.png", dpi=150); plt.close()

corr = df1[['N','P','K','temperature','humidity','ph','rainfall']].corr()
fig, ax = plt.subplots(figsize=(5.5, 4.5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="Greens", ax=ax, cbar_kws={"shrink": .8})
ax.set_title("Correlation Between Soil & Climate Variables")
plt.tight_layout(); plt.savefig("chart4_correlation_heatmap.png", dpi=150); plt.close()

# NEW for Week 4 / revised Week 2: an explicit outlier visualization
fig, ax = plt.subplots(figsize=(7, 4.2))
vals = df1['rainfall']
q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
iqr = q3 - q1
lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
sns.boxplot(x=vals, color=GREEN, ax=ax, fliersize=4, flierprops={"markerfacecolor":"#C62828","markeredgecolor":"#C62828"})
ax.axvline(lo, color="#F9A825", linestyle="--", linewidth=1.2, label=f"Lower fence ({lo:.1f} mm)")
ax.axvline(hi, color="#F9A825", linestyle="--", linewidth=1.2, label=f"Upper fence ({hi:.1f} mm)")
ax.set_title("Rainfall Outlier Fences (1.5\u00d7IQR Rule), All Crops Combined")
ax.set_xlabel("Rainfall (mm)")
ax.legend(loc="upper right", fontsize=9)
plt.tight_layout(); plt.savefig("chart5_outlier_fences.png", dpi=150); plt.close()

print("done")
print(f"Rainfall IQR fences: lo={lo:.2f}, hi={hi:.2f}, Q1={q1:.2f}, Q3={q3:.2f}")
