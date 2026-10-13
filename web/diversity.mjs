/** Count-table parsing and descriptive diversity metrics; no phylogeny or inference. */
export const EXAMPLE = `sample_id,ASV_1,ASV_2,ASV_3,ASV_4,ASV_5
Control_1,40,30,20,10,0
Control_2,45,25,20,10,0
Treatment_1,5,5,20,30,40
Treatment_2,10,0,15,35,40`;
const MAX_SAMPLES = 100;
const MAX_FEATURES = 500;

function readCsv(text) {
  if (typeof text !== 'string' || text.length > 3_000_000) throw new Error('CSV must be text under 3 MB.');
  const rows = [];
  let row = [], cell = '', quoted = false, closed = false;
  text = text.replace(/^\uFEFF/, '');
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (c === '"') { quoted = false; closed = true; }
      else cell += c;
    } else if (c === '"' && cell === '' && !closed) {
      quoted = true;
    } else if (c === ',') {
      row.push(cell); cell = ''; closed = false;
    } else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(cell); if (row.some(v => v.trim() !== '')) rows.push(row);
      row = []; cell = ''; closed = false;
    } else if (closed && c !== ' ' && c !== '\t') {
      throw new Error('Unexpected characters after closing CSV quote.');
    } else if (!closed) {
      if (c === '"') throw new Error('Unescaped quote in CSV value.');
      cell += c;
    }
  }
  if (quoted) throw new Error('Unterminated quoted CSV field.');
  row.push(cell); if (row.some(v => v.trim() !== '')) rows.push(row);
  return rows;
}

export function parseTable(text) {
  const rows = readCsv(text);
  if (rows.length < 2) throw new Error('Provide a header and at least one sample row.');
  const header = rows[0].map(x => x.trim());
  if (header.length < 2 || header[0].toLowerCase() !== 'sample_id') {
    throw new Error('First column must be sample_id, followed by ASV/OTU count columns.');
  }
  if (header.length - 1 > MAX_FEATURES || rows.length - 1 > MAX_SAMPLES) {
    throw new Error(`Maximum ${MAX_SAMPLES} samples and ${MAX_FEATURES} ASVs/OTUs per analysis.`);
  }
  if (header.some(v => !v) || new Set(header).size !== header.length) {
    throw new Error('Column names must be nonempty and unique.');
  }
  const samples = [], seen = new Set();
  for (let i = 1; i < rows.length; i++) {
    const cells = rows[i];
    if (cells.length !== header.length) throw new Error(`Row ${i + 1}: expected ${header.length} columns; found ${cells.length}.`);
    const name = cells[0].trim();
    if (!name || seen.has(name)) throw new Error(`Row ${i + 1}: sample_id must be nonempty and unique.`);
    seen.add(name);
    const counts = cells.slice(1).map((value, j) => {
      const v = value.trim();
      const number = Number(v);
      if (!/^[0-9]+$/.test(v) || !Number.isSafeInteger(number)) {
        throw new Error(`Row ${i + 1}, ${header[j + 1]}: read count must be a nonnegative safe integer.`);
      }
      return number;
    });
    const depth = counts.reduce((a, b) => a + b, 0);
    if (!Number.isSafeInteger(depth) || depth === 0) throw new Error(`Row ${i + 1}: total read count must be positive and within safe integer range.`);
    samples.push({name, counts, depth});
  }
  return {features: header.slice(1), samples};
}

export function analyseTable(table) {
  const {samples, features} = table;
  if (!Array.isArray(samples) || !Array.isArray(features) || !samples.length) throw new Error('Invalid sample table.');
  const alpha = samples.map(s => {
    const present = s.counts.filter(n => n > 0);
    const observed = present.length;
    const singletons = present.filter(n => n === 1).length;
    const doubletons = present.filter(n => n === 2).length;
    const shannon = -present.reduce((sum, n) => { const p = n / s.depth; return sum + p * Math.log(p); }, 0);
    const simpson = 1 - present.reduce((sum, n) => { const p = n / s.depth; return sum + p * p; }, 0);
    const chao1 = observed + singletons * (singletons - 1) / (2 * (doubletons + 1));
    return {sample: s.name, reads: s.depth, observed, shannon, simpson, chao1, evenness: observed > 1 ? shannon / Math.log(observed) : 0};
  });
  const beta = samples.map((a, i) => samples.map((b, j) => {
    if (i === j) return 0;
    // Bray–Curtis applied to relative abundances to mitigate library-depth effects.
    let distance = 0;
    for (let k = 0; k < features.length; k++) distance += Math.abs(a.counts[k] / a.depth - b.counts[k] / b.depth);
    return Math.min(1, Math.max(0, distance / 2));
  }));
  return {alpha, beta, sampleNames: samples.map(s => s.name)};
}

export function toCsv(rows) {
  return rows.map(row => row.map(value => {
    let v = String(value);
    if (/^\s*[=+\-@]/.test(v)) v = "'" + v;
    return /[",\r\n]/.test(v) ? `"${v.replaceAll('"','""')}"` : v;
  }).join(',')).join('\r\n') + '\r\n';
}
