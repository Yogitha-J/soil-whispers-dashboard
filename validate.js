const fs = require("fs");
const Papa = require("papaparse");
const agg = require("./aggregations.js");

const df1 = Papa.parse(fs.readFileSync("crop_recommendation_cleaned.csv", "utf8"), { header: true, dynamicTyping: true, skipEmptyLines: true }).data;
const df2 = Papa.parse(fs.readFileSync("crops_state_yield_cleaned.csv", "utf8"), { header: true, dynamicTyping: true, skipEmptyLines: true }).data;

console.log("Rows loaded:", df1.length, df2.length);

// --- Check 1: yearly rice/wheat yield trend (expect 2010 ~2046, 2017 ~2473 for rice) ---
const riceTrend = agg.yearlyYieldTrend(df2, "RICE");
const wheatTrend = agg.yearlyYieldTrend(df2, "WHEAT");
console.log("\nRice yearly trend:", riceTrend.map(r => `${r.year}:${r.meanYield.toFixed(1)}`).join("  "));
console.log("Wheat yearly trend:", wheatTrend.map(r => `${r.year}:${r.meanYield.toFixed(1)}`).join("  "));
const riceGrowth = ((riceTrend[riceTrend.length - 1].meanYield / riceTrend[0].meanYield) - 1) * 100;
console.log(`Rice growth 2010->2017: ${riceGrowth.toFixed(1)}% (expected ~20.9%)`);

// --- Check 2: state ranking (expect Tamil Nadu ~3940 top, Maharashtra ~1400 bottom) ---
const stateRank = agg.stateYieldRanking(df2, "RICE");
console.log("\nTop 5 states:", stateRank.slice(0, 5).map(s => `${s.state}:${s.meanYield.toFixed(0)}`).join(", "));
console.log("Bottom 5 states:", stateRank.slice(-5).map(s => `${s.state}:${s.meanYield.toFixed(0)}`).join(", "));

// --- Check 3: rainfall by crop (expect rice ~236mm mean, cotton ~80mm mean) ---
const crops = ["rice", "maize", "cotton", "coffee", "banana", "chickpea"];
const rainfall = agg.rainfallByCrop(df1, crops);
console.log("\nRainfall by crop (mean mm):");
crops.forEach(c => console.log(`  ${c}: ${rainfall[c].mean.toFixed(1)}  (min ${rainfall[c].min.toFixed(0)}, max ${rainfall[c].max.toFixed(0)})`));

// --- Check 4: correlation matrix (expect P-K strong positive ~0.74, others weak) ---
const fields = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"];
const corr = agg.correlationMatrix(df1, fields);
console.log("\nCorrelation matrix:");
console.log("      " + fields.map(f => f.padEnd(6)).join(""));
corr.forEach((row, i) => console.log(fields[i].padEnd(6) + row.map(v => v.toFixed(2).padEnd(6)).join("")));

// --- Check 5: area vs yield scatter sample count ---
const scatter = agg.areaVsYieldScatter(df2, "RICE", 20);
console.log(`\nArea-vs-yield scatter sample points: ${scatter.length}`);
console.log("First 3:", scatter.slice(0, 3));
