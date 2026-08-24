// aggregations.js
// Pure functions that turn the two cleaned CSVs into the exact aggregates the dashboard needs.
// Written so they can run identically in Node (for validation against the Week 2 pandas output)
// and in the browser (embedded directly in the dashboard HTML).

function mean(arr) { return arr.reduce((a, b) => a + b, 0) / arr.length; }

function quantile(sortedArr, q) {
  const pos = (sortedArr.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  if (sortedArr[base + 1] !== undefined) {
    return sortedArr[base] + rest * (sortedArr[base + 1] - sortedArr[base]);
  }
  return sortedArr[base];
}

function pearson(x, y) {
  const n = x.length;
  const mx = mean(x), my = mean(y);
  let num = 0, dx2 = 0, dy2 = 0;
  for (let i = 0; i < n; i++) {
    const dx = x[i] - mx, dy = y[i] - my;
    num += dx * dy; dx2 += dx * dx; dy2 += dy * dy;
  }
  return num / Math.sqrt(dx2 * dy2);
}

// --- Dataset 1: Crop Recommendation (soil/climate) ---

function rainfallByCrop(rows, crops) {
  // returns {crop: {min, q1, median, q3, max, mean}} for box-plot rendering
  const out = {};
  crops.forEach(crop => {
    const vals = rows.filter(r => r.label === crop).map(r => r.rainfall).sort((a, b) => a - b);
    out[crop] = {
      min: vals[0], max: vals[vals.length - 1],
      q1: quantile(vals, 0.25), median: quantile(vals, 0.5), q3: quantile(vals, 0.75),
      mean: mean(vals),
    };
  });
  return out;
}

function correlationMatrix(rows, fields) {
  const cols = {};
  fields.forEach(f => { cols[f] = rows.map(r => r[f]); });
  const matrix = fields.map(f1 => fields.map(f2 => pearson(cols[f1], cols[f2])));
  return matrix;
}

// --- Dataset 2: District crop yield panel ---

function yearlyYieldTrend(rows, cropPrefix) {
  // cropPrefix e.g. "RICE" -> uses "RICE AREA (1000 ha)" and "RICE YIELD (Kg per ha)"
  const areaKey = `${cropPrefix} AREA (1000 ha)`;
  const yieldKey = `${cropPrefix} YIELD (Kg per ha)`;
  const grown = rows.filter(r => r[areaKey] > 0);
  const byYear = {};
  grown.forEach(r => {
    if (!byYear[r.Year]) byYear[r.Year] = [];
    byYear[r.Year].push(r[yieldKey]);
  });
  const years = Object.keys(byYear).map(Number).sort((a, b) => a - b);
  return years.map(y => ({ year: y, meanYield: mean(byYear[y]) }));
}

function stateYieldRanking(rows, cropPrefix) {
  const areaKey = `${cropPrefix} AREA (1000 ha)`;
  const yieldKey = `${cropPrefix} YIELD (Kg per ha)`;
  const grown = rows.filter(r => r[areaKey] > 0);
  const byState = {};
  grown.forEach(r => {
    const s = r['State Name'];
    if (!byState[s]) byState[s] = [];
    byState[s].push(r[yieldKey]);
  });
  return Object.entries(byState)
    .map(([state, vals]) => ({ state, meanYield: mean(vals) }))
    .sort((a, b) => b.meanYield - a.meanYield);
}

function areaVsYieldScatter(rows, cropPrefix, sampleEvery) {
  const areaKey = `${cropPrefix} AREA (1000 ha)`;
  const yieldKey = `${cropPrefix} YIELD (Kg per ha)`;
  const grown = rows.filter(r => r[areaKey] > 0 && r[yieldKey] > 0);
  return grown
    .filter((_, i) => i % sampleEvery === 0)
    .map(r => ({ area: r[areaKey], yield: r[yieldKey], state: r['State Name'] }));
}

if (typeof module !== "undefined") {
  module.exports = { mean, quantile, pearson, rainfallByCrop, correlationMatrix, yearlyYieldTrend, stateYieldRanking, areaVsYieldScatter };
}
