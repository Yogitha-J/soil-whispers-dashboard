const fs = require("fs");
const RealPapa = require("papaparse");

// --- Minimal DOM stub ---
const elements = {};
function makeEl(id) {
  if (!elements[id]) {
    elements[id] = {
      value: "", textContent: "", innerHTML: "", style: {}, classList: { add(){}, toggle(){} },
      addEventListener(){}, appendChild(){}, nextElementSibling: { textContent: "" },
      add(opt) { this._options = this._options || []; this._options.push(opt); if (!this.value) this.value = opt.value; },
    };
  }
  return elements[id];
}
global.document = {
  getElementById: (id) => makeEl(id),
  querySelector: (sel) => ({ innerHTML: "" }),
  dispatchEvent: () => {},
};
global.window = { dispatchEvent: () => {} };
global.Event = function(name) { this.name = name; };
global.Option = function(text, value) { return { text, value }; };
global.Papa = RealPapa;
elements['agroCropPrefix'] = { value: 'RICE', textContent: "", innerHTML: "", style: {}, classList: { add(){}, toggle(){} }, addEventListener(){}, nextElementSibling: { textContent: "" } };
global.Plotly = {
  react: (divId, traces, layout, opts) => {
    // Validate the trace/layout shapes are sane (this is what would actually render)
    traces.forEach((t, i) => {
      if (t.x && t.y && t.x.length !== t.y.length && t.type !== 'box') {
        throw new Error(`Trace ${i} in ${divId}: x/y length mismatch (${t.x.length} vs ${t.y.length})`);
      }
      if (t.type === 'heatmap' && (!t.z || !t.z.length)) {
        throw new Error(`Heatmap in ${divId} has empty z`);
      }
    });
    console.log(`  Plotly.react('${divId}') OK - ${traces.length} trace(s), first trace type=${traces[0].type||'scatter'}, points=${(traces[0].x||traces[0].y||[]).length}`);
  },
};

// --- Load and eval the real extracted script ---
const script = fs.readFileSync("_extracted.js", "utf8");
eval(script);

console.log("\n=== Running init() ===");
console.log("init executed without throwing.\n");

console.log("=== Simulating farmer view filter change (state=Punjab, crop=cotton) ===");
document.getElementById('farmerState').value = 'Punjab';
document.getElementById('farmerCrop').value = 'cotton';
renderFarmer();

console.log("\n=== Simulating agronomist view filter change (crop=WHEAT, highlight=coffee) ===");
document.getElementById('agroCropPrefix').value = 'WHEAT';
document.getElementById('agroCropHighlight').value = 'coffee';
renderAgro();

console.log("\nALL CHECKS PASSED");
