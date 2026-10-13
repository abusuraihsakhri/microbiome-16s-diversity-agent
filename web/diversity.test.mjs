import test from 'node:test';
import assert from 'node:assert/strict';
import {EXAMPLE, parseTable, analyseTable, toCsv} from './diversity.mjs';

test('descriptive diversity is mathematically correct for equal taxa', () => {
  const r = analyseTable(parseTable('sample_id,A,B\na,5,5\nb,10,0'));
  assert.ok(Math.abs(r.alpha[0].shannon - Math.log(2)) < 1e-12);
  assert.equal(r.alpha[0].simpson, 0.5);
  assert.equal(r.alpha[0].observed, 2);
  assert.equal(r.alpha[0].evenness, 1);
  assert.equal(r.beta[0][1], 0.5);
  assert.deepEqual(r.beta[0], [0, 0.5]);
});
test('library depth normalization and singleton Chao1 correction', () => {
  const r = analyseTable(parseTable('sample_id,A,B,C\na,1,1,2\nb,10,10,20'));
  assert.equal(r.alpha[0].chao1, 3 + 2 * 1 / (2 * 2));
  assert.equal(r.beta[0][1], 0);
});
test('example runs and contains four samples', () => {
  const result = analyseTable(parseTable(EXAMPLE));
  assert.equal(result.alpha.length, 4);
  assert.equal(result.beta.length, 4);
});
test('CSV escaped identifiers', () => {
  const r = parseTable('sample_id,"ASV,1",ASV2\n"sample ""one""",3,2');
  assert.equal(r.samples[0].name, 'sample "one"');
  assert.equal(r.features[0], 'ASV,1');
  assert.equal(toCsv([['x,y','"z"']]), '"x,y","""z"""\r\n');
});
test('invalid counts and malformed layouts fail closed', () => {
  for (const csv of ['sample_id,A\na,-1','sample_id,A\na,1.5', 'sample_id,A\na,1e2', 'sample_id,A\na,0x10','sample_id,A\na,NaN', 'sample_id,A\na,','sample_id,A\na,0', 'sample_id,A\na,1\na,2', 'x,A\na,1', 'sample_id,A\na,1,2', 'sample_id,A\na,"1']) {
    assert.throws(() => parseTable(csv), csv);
  }
});

test('spreadsheet formula payloads are escaped on export', () => {
  assert.equal(toCsv([['=2+2','@SUM(1)']]), "'=2+2,'@SUM(1)\r\n");
});
