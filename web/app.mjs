import {EXAMPLE, parseTable, analyseTable, toCsv} from './diversity.mjs';
const $ = id => document.getElementById(id);
let last = null;
function setStatus(message, error=false) { $('status').textContent=message; $('status').className=error?'status error':'status'; }
function cell(row, value, header=false) { const el=document.createElement(header?'th':'td');el.textContent=String(value);row.append(el); }
function emptyTable(id) { const table=$(id);table.querySelector('tbody').replaceChildren();if(id==='beta')table.querySelector('thead').replaceChildren(); }
function resetResults() {last=null;emptyTable('alpha');emptyTable('beta');for(const id of ['k-samples','k-features','k-reads']) $(id).textContent='—';$('export-alpha').disabled=true;$('export-beta').disabled=true;}
function fmt(n) {return Number(n).toFixed(4);}
function show(result, table) {
  resetResults(); last=result;
  $('k-samples').textContent=String(table.samples.length);
  $('k-features').textContent=String(table.features.length);
  $('k-reads').textContent=table.samples.reduce((sum,s)=>sum+s.depth,0).toLocaleString();
  const abody=$('alpha').querySelector('tbody');
  for(const a of result.alpha){const tr=document.createElement('tr');for(const x of [a.sample,a.reads,a.observed,fmt(a.shannon),fmt(a.simpson),fmt(a.chao1),fmt(a.evenness)])cell(tr,x);abody.append(tr);}
  const head=document.createElement('tr');cell(head,'Sample',true);for(const name of result.sampleNames)cell(head,name,true);$('beta').querySelector('thead').append(head);
  const bbody=$('beta').querySelector('tbody');result.beta.forEach((dist,i)=>{const tr=document.createElement('tr');cell(tr,result.sampleNames[i],true);for(const v of dist)cell(tr,fmt(v));bbody.append(tr);});
  $('export-alpha').disabled=false;$('export-beta').disabled=false;setStatus(`Calculated ${result.alpha.length} samples using ${table.features.length} features. No data left this browser.`);
}
$('csv-input').addEventListener('input',()=>{resetResults();setStatus('Input changed; select Analyze diversity.');});
$('analyse').addEventListener('click',()=>{try{const t=parseTable($('csv-input').value);show(analyseTable(t),t);}catch(e){resetResults();setStatus(e.message,true);}});
$('example').addEventListener('click',()=>{$('csv-input').value=EXAMPLE;$('csv-file').value='';resetResults();setStatus('Example loaded; select Analyze diversity.');});
$('clear').addEventListener('click',()=>{$('csv-input').value='';$('csv-file').value='';resetResults();setStatus('Input cleared.');});
$('csv-file').addEventListener('change',async e=>{const file=e.target.files?.[0];if(!file)return;resetResults();if(file.size>3_000_000){setStatus('File exceeds 3 MB limit.',true);return;}try{$('csv-input').value=await file.text();setStatus(`Loaded ${file.name}. Select Analyze diversity.`);}catch{setStatus('Unable to read local CSV file.',true);}});
function download(filename,rows){const blob=new Blob([toCsv(rows)],{type:'text/csv;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('export-alpha').addEventListener('click',()=>{if(!last)return;download('microbiome-alpha-diversity.csv',[['sample_id','reads','observed','shannon','simpson_1_minus_d','chao1_bias_corrected','pielou_evenness'],...last.alpha.map(x=>[x.sample,x.reads,x.observed,x.shannon,x.simpson,x.chao1,x.evenness])]);});
$('export-beta').addEventListener('click',()=>{if(!last)return;download('microbiome-bray-curtis.csv',[['sample_id',...last.sampleNames],...last.beta.map((x,i)=>[last.sampleNames[i],...x])]);});
$('csv-input').value=EXAMPLE;
