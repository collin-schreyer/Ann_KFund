'use strict';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const escapeHTML=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// Render the Markdown used by the local guidance as text-first HTML. Raw HTML is
// always escaped; only this small, explicit set of tags is ever generated.
function inlineMarkdown(value){
  return escapeHTML(value)
    .replace(/`([^`\n]+)`/g,'<code>$1</code>')
    .replace(/\*\*([^*\n]+)\*\*/g,'<strong>$1</strong>')
    .replace(/__([^_\n]+)__/g,'<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g,'$1<em>$2</em>');
}
function renderMarkdown(value){
  const lines=String(value??'').replace(/\r\n?/g,'\n').split('\n');
  let html='',paragraph=[],lists=[];
  const flushParagraph=()=>{if(paragraph.length){html+='<p>'+paragraph.map(inlineMarkdown).join('<br>')+'</p>';paragraph=[]}};
  const closeList=()=>{while(lists.length){html+='</li></'+lists.pop().type+'>'}};
  const tableCells=line=>line.trim().replace(/^\|/,'').replace(/\|$/,'').split('|').map(s=>s.trim());
  const isTableRule=line=>{const cells=tableCells(line);return cells.length>1&&cells.every(s=>/^:?-{3,}:?$/.test(s))};
  for(let i=0;i<lines.length;i++){
    const line=lines[i];
    if(!line.trim()){flushParagraph();closeList();continue}
    if(/^\s*```/.test(line)){
      flushParagraph();closeList();const code=[];i++;
      while(i<lines.length&&!/^\s*```/.test(lines[i]))code.push(lines[i++]);
      html+='<pre><code>'+escapeHTML(code.join('\n'))+'</code></pre>';continue;
    }
    if(line.includes('|')&&i+1<lines.length&&isTableRule(lines[i+1])){
      flushParagraph();closeList();const headers=tableCells(line);i++;
      html+='<div class="markdown-table-wrap"><table><thead><tr>'+headers.map(c=>'<th scope="col">'+inlineMarkdown(c)+'</th>').join('')+'</tr></thead><tbody>';
      while(i+1<lines.length&&lines[i+1].includes('|')&&lines[i+1].trim()){
        const cells=tableCells(lines[++i]);html+='<tr>'+headers.map((_,n)=>'<td>'+inlineMarkdown(cells[n]??'')+'</td>').join('')+'</tr>';
      }
      html+='</tbody></table></div>';continue;
    }
    const heading=line.match(/^\s{0,3}(#{1,6})\s+(.*)$/);
    if(heading){flushParagraph();closeList();const n=Math.min(6,heading[1].length+2);html+='<h'+n+'>'+inlineMarkdown(heading[2].replace(/\s+#+\s*$/,''))+'</h'+n+'>';continue}
    if(/^\s{0,3}(?:-{3,}|\*{3,}|_{3,})\s*$/.test(line)){flushParagraph();closeList();html+='<hr>';continue}
    const item=line.match(/^(\s*)([-+*]|\d+\.)\s+(.*)$/);
    if(item){
      flushParagraph();const indent=item[1].replace(/\t/g,'    ').length,type=/\d/.test(item[2][0])?'ol':'ul';
      while(lists.length&&indent<lists[lists.length-1].indent)html+='</li></'+lists.pop().type+'>';
      if(lists.length&&indent===lists[lists.length-1].indent&&type!==lists[lists.length-1].type)html+='</li></'+lists.pop().type+'>';
      const number=type==='ol'?parseInt(item[2],10):null;
      if(!lists.length||indent>lists[lists.length-1].indent){html+='<'+type+(type==='ol'?' start="'+number+'"':'')+'>';lists.push({indent,type})}else html+='</li>';
      html+='<li'+(type==='ol'?' value="'+number+'"':'')+'>'+inlineMarkdown(item[3]);continue;
    }
    closeList();paragraph.push(line.trim());
  }
  flushParagraph();closeList();return html;
}
// Older saved citations may have been cut at a fixed character boundary, even
// inside a bold marker or a word. Omit an incomplete trailing bold fragment
// from the display and flag truncation; never modify the saved evidence.
function renderEvidenceMarkdown(value){
  const excerpt=String(value??'');
  const markers=excerpt.match(/\*\*/g)||[];
  const tail=excerpt.match(/\*\*([^*\n]*)$/);
  const dangling=markers.length%2===1&&tail;
  const display=dangling?excerpt.slice(0,tail.index):excerpt;
  const truncated=excerpt.length===1400||!!dangling;
  return renderMarkdown(display)+(truncated?'<p class="excerpt-note">This excerpt may be truncated. Consult the full source for context.</p>':'');
}
const money=x=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(Number(x)||0);
let currentReview=null,sourceCache=[],reviewStep=1,reviewSnapshot=null,analysisPending=false,receiptPending=false,reviewGeneration=0,deploymentMode='unknown';
const titles={overview:'Overview',review:'Event review',search:'Guidance search',sources:'Source library'};
function go(page){$$('.page').forEach(el=>el.classList.toggle('active',el.id===`page-${page}`));$$('.nav').forEach(el=>{const selected=el.dataset.page===page;el.classList.toggle('active',selected);if(selected)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current')});$('#breadcrumb').textContent=titles[page];window.scrollTo({top:0,behavior:'smooth'});if(page==='sources')loadSources();if(page==='overview')loadCases()}
$$('[data-page]').forEach(el=>el.addEventListener('click',()=>go(el.dataset.page))); $$('[data-go]').forEach(el=>el.addEventListener('click',()=>go(el.dataset.go)));
async function api(url,options={}){const r=await fetch(url,{headers:{'Content-Type':'application/json'},...options});let data;try{data=await r.json()}catch{throw new Error('The local service returned an unexpected response.')}if(!r.ok)throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||'Request failed'));return data}
async function status(){try{const d=await api('/api/status');deploymentMode=d.deployment_mode==='cloud'?'cloud':'local';const cloud=deploymentMode==='cloud';$('#workspace-label').textContent=cloud?'Shared demo workspace':'Local workspace';$('#workspace-location').textContent=cloud?'Hosted on Render':'Running on this computer';$('#prototype-label').textContent=cloud?'CLOUD DEMO':'LOCAL PROTOTYPE';$('#footer-environment').textContent=(cloud?'Shared cloud demo':'Local prototype')+' · Sample sources · Human review required';$('#search-privacy').textContent='Your question, recent conversation, and relevant source excerpts are sent to OpenAI. '+(cloud?'Saved reviews are shared with demo users and may disappear after a restart.':'Saved reviews remain on this computer.');$('#cloud-notice').hidden=!cloud;$('#sign-out').hidden=!cloud;$('#service-status').textContent=d.configured?(cloud?'Cloud demo ready':'Local service ready'):'OpenAI key needed';$('.status-dot').style.background=d.configured?'#78cda7':'#dfa54f'}catch{$('#service-status').textContent='Service unavailable';$('.status-dot').style.background='#d47b6e'}}
$('#sign-out').addEventListener('click',async()=>{try{await api('/api/auth/logout',{method:'POST',body:'{}'});window.location.href='/login'}catch(e){$('#service-status').textContent='Sign out failed. Please try again.'}});
function cloudMode(){return deploymentMode==='cloud'}
function row(desc='',amount='',source={}){const el=document.createElement('div');el.className='line-entry';el.dataset.sourceFilename=source.source_filename||'';el.dataset.sourcePage=source.source_page||'';el.innerHTML=`<div class="line-row"><input aria-label="Expense description" class="item-description" placeholder="e.g. Reception catering" required maxlength="300" value="${escapeHTML(desc)}"><input aria-label="Expense amount in dollars" class="item-amount" type="number" min="0" step="0.01" placeholder="0.00" required value="${escapeHTML(amount??'')}"><button type="button" aria-label="Remove line item" title="Remove line item">×</button></div>${source.source_filename?`<p class="line-source">From ${escapeHTML(source.source_filename)}${source.source_page?' · page '+escapeHTML(source.source_page):''}${source.needs_review?' · needs review':''}</p>`:''}`;el.querySelector('button').addEventListener('click',()=>{if($$('.line-entry').length===1){el.querySelectorAll('input').forEach(i=>i.value='');el.dataset.sourceFilename='';el.dataset.sourcePage='';el.querySelector('.line-source')?.remove()}else el.remove();updateTotal()});el.addEventListener('input',updateTotal);$('#line-items').appendChild(el);updateTotal()}
function updateTotal(){let lines=$$('.line-row');$('#line-count').textContent=`${lines.length} ${lines.length===1?'item':'items'}`;$('#entered-total').textContent=money(lines.reduce((n,l)=>n+(Number(l.querySelector('.item-amount').value)||0),0));refreshReturnControl()}
$('#add-item').addEventListener('click',()=>row());row();
// Validate only visible steps: native whole-form validation cannot focus hidden controls.
const reviewForm=$('#review-form');reviewForm.noValidate=true;
function snapshotReviewInputs(){return JSON.stringify({event_name:$('#event-name').value,requester:$('#requester').value,event_date:$('#event-date').value,purpose:$('#event-purpose').value,foreign_guests:$('#foreign-guests').value,total_guests:$('#total-guests').value,per_person_limit:$('#per-person-limit').value,items:$$('.line-entry').map(el=>({description:el.querySelector('.item-description').value,amount:el.querySelector('.item-amount').value,source_filename:el.dataset.sourceFilename||'',source_page:el.dataset.sourcePage||''}))})}
function refreshReturnControl(){
  const button=$('#return-review'),status=$('#workflow-status');if(!button||!status)return;
  const hasResult=!!currentReview&&!!reviewSnapshot,unchanged=hasResult&&snapshotReviewInputs()===reviewSnapshot;
  button.hidden=reviewStep!==2||!unchanged;status.hidden=reviewStep!==2||!hasResult;
  status.textContent=!hasResult?'':unchanged?'Your previous results and reviewer decisions are available.':'The inputs have changed. Reanalysis replaces the previous draft and reviewer decisions. Restore the previous inputs to view or save those decisions first.';
}
function setReviewStep(step,{scroll=true}={}){
  reviewStep=step;
  $$('.workflow-step').forEach(el=>el.hidden=Number(el.dataset.step)!==step);
  $$('[data-progress-step]').forEach(el=>{const n=Number(el.dataset.progressStep);el.classList.toggle('is-current',n===step);el.classList.toggle('is-complete',n<step);if(n===step)el.setAttribute('aria-current','step');else el.removeAttribute('aria-current')});
  $('#step-next').hidden=step!==1;
  $('#step-back').hidden=step===1;
  $('#analyze').hidden=step!==2;
  $('#analysis-note').hidden=step!==2;
  $('#review-result').hidden=step!==3 || !currentReview;
  refreshReturnControl();
  if(scroll){if(step===3)$('#review-result').scrollIntoView({behavior:'smooth',block:'start'});else $('#review-form').scrollIntoView({behavior:'smooth',block:'start'})}
}
function validateStep(step){
  const fields=$$(`.workflow-step[data-step="${step}"] input, .workflow-step[data-step="${step}"] select, .workflow-step[data-step="${step}"] textarea`);
  for(const field of fields){
    if(!field.disabled && !field.checkValidity()){field.reportValidity();return false}
  }
  if(step===1){const foreign=Number($('#foreign-guests').value),total=$('#total-guests');if(foreign>Number(total.value)){total.setCustomValidity('Total guests must be at least the number of foreign guests.');total.reportValidity();return false}total.setCustomValidity('')}
  return true;
}
$('#total-guests').addEventListener('input',()=>$('#total-guests').setCustomValidity(''));
$('#foreign-guests').addEventListener('input',()=>$('#total-guests').setCustomValidity(''));
$('#step-next').addEventListener('click',()=>{if(validateStep(1)){ $('#review-error').hidden=true;setReviewStep(2)}});
$('#step-back').addEventListener('click',()=>{if(reviewStep>1){$('#review-error').hidden=true;setReviewStep(reviewStep-1)}});
$('#return-review').addEventListener('click',()=>{if(currentReview&&reviewSnapshot===snapshotReviewInputs())setReviewStep(3)});
reviewForm.addEventListener('input',refreshReturnControl);reviewForm.addEventListener('change',refreshReturnControl);
setReviewStep(1,{scroll:false});
// A complete, fictional scenario that can be explored without entering real event data.
function loadExample(){
  reviewGeneration++;
  $('#event-name').value='Sample: Reception for visiting delegates';
  $('#requester').value='Sample: EDCS';
  $('#event-date').value='2026-04-15';
  $('#event-purpose').value='Fictional reception for visiting delegates.';
  $('#per-person-limit').value=100;
  $('#foreign-guests').value=4;
  $('#total-guests').value=10;
  $('#line-items').innerHTML='';
  row('Reception catering for all 10 guests',1000);
  row('Interpretation for visiting delegates',400);
  row('Decorative balloons',100);
  $('#receipt-status').textContent='Fictional event loaded. The sample receipt contains the same expenses; if you extract it, remove the duplicate rows before analysis.';
  $('#review-result').hidden=true;
  $('#review-error').hidden=true;
  currentReview=null;reviewSnapshot=null;
  setReviewStep(1,{scroll:false});
  go('review');
}
$('#load-demo').addEventListener('click',loadExample);
document.addEventListener('click',e=>{if(e.target.closest('#start-example'))loadExample()});
function fileAsBase64(file){return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result).split(',')[1]);reader.onerror=()=>reject(new Error('Could not read '+file.name));reader.readAsDataURL(file)})}
function updateAsyncControls(){const busy=analysisPending||receiptPending;$('#extract-receipts').disabled=busy;$('#sample-receipt').disabled=busy;$$('[data-sample-path]').forEach(b=>b.disabled=busy);['#analyze','#step-back','#step-next','#return-review','#load-demo','#start-example'].forEach(id=>$(id).disabled=busy)}
async function extractFiles(files){
  const status=$('#receipt-status'), error=$('#receipt-error');
  error.hidden=true;
  if(analysisPending||receiptPending){showError('#receipt-error','Wait for the current task to finish.');return}
  if(!files.length){showError('#receipt-error','Select one or more documents first.');return}
  if(files.length>5||files.some(f=>f.size>8*1024*1024)){showError('#receipt-error','Select up to five files, no larger than 8 MB each.');return}
  if(files.some(f=>!['application/pdf','image/png','image/jpeg','image/webp'].includes(f.type))){showError('#receipt-error','Use PDF, PNG, JPEG, or WEBP files.');return}
  const extractionGeneration=reviewGeneration;receiptPending=true;updateAsyncControls();status.textContent='Extracting draft line items. This may take a moment…';
  try{const payload=await Promise.all(files.map(async file=>({filename:file.name,mime_type:file.type,data_base64:await fileAsBase64(file)})));
    const result=await api('/api/receipts/extract',{method:'POST',body:JSON.stringify({files:payload})});
    if(reviewGeneration!==extractionGeneration)return
    const items=result.items||[];
    if(items.length){const first=$('.line-entry');if($$('.line-entry').length===1&&!first.querySelector('.item-description').value&&!first.querySelector('.item-amount').value)first.remove();items.forEach(it=>row(it.description,it.amount,it))}
    const warnings=(result.documents||[]).flatMap(d=>(d.warnings||[]).map(w=>`${d.filename}: ${w}`));
    status.textContent=(items.length?`${items.length} draft line item${items.length===1?'':'s'} added. Review each amount against the document.`:'No line items were extracted. Enter them manually or try a clearer document.')+(warnings.length?' '+warnings.join(' '):'')+(result.note?' '+result.note:'');
  }catch(e){if(reviewGeneration===extractionGeneration){status.textContent='';showError('#receipt-error',e.message)}}finally{receiptPending=false;updateAsyncControls()}
}
async function fetchSample(path){
  const res=await fetch(path);
  // Sample assets are never HTML. A redirected login page means the cloud
  // session expired; keep the current form intact so the user can choose when to reload.
  if(res.status===401 || (res.redirected && new URL(res.url,window.location.href).pathname==='/login') || (res.headers.get('content-type')||'').toLowerCase().includes('text/html')) throw new Error('Your session expired. Reload and sign in again.');
  if(!res.ok)throw new Error('Sample document is unavailable.');
  return res;
}
$('#extract-receipts').addEventListener('click',()=>extractFiles([...$('#receipt-files').files]));
document.addEventListener('click',async e=>{
  const button=e.target.closest('[data-sample-path]');if(!button)return;
  try{const path=button.dataset.samplePath;const res=await fetchSample(path);const blob=await res.blob();const mime=blob.type.split(';')[0].toLowerCase();if(!['application/pdf','image/png','image/jpeg','image/webp'].includes(mime))throw new Error('Sample document has an unsupported file type.');await extractFiles([new File([blob],path.split('/').pop(),{type:mime})])}catch(err){showError('#receipt-error',err.message)}
});
$('#sample-receipt').addEventListener('click',async()=>{
  try{const res=await fetchSample('/sample-receipt.svg');const svg=await res.blob(),url=URL.createObjectURL(svg),img=new Image();
    try{await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=()=>reject(new Error('Could not load sample receipt.'));img.src=url});const canvas=document.createElement('canvas');canvas.width=img.naturalWidth;canvas.height=img.naturalHeight;canvas.getContext('2d').drawImage(img,0,0);const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));if(!blob)throw new Error('Could not prepare sample receipt.');await extractFiles([new File([blob],'fictional-sample-receipt.png',{type:'image/png'})])}finally{URL.revokeObjectURL(url)}
  }catch(e){showError('#receipt-error',e.message)}
});
function citations(items){if(!items?.length)return '<p class="results-note">No supporting passages were returned. Verify the source before relying on this assessment.</p>';return `<div class="citations"><div class="eyebrow">SOURCE PASSAGES</div>${items.map(c=>`<details><summary>${escapeHTML(c.title||c.source_id||'Source')}</summary><div class="markdown-content">${renderEvidenceMarkdown(c.excerpt||'')}</div></details>`).join('')}</div>`}
function classificationLabel(v){return ({K_FUND_ALLOWABLE:'Suggested K Fund',NOT_ALLOWABLE:'Not suggested for K Fund',LEGAL_REVIEW:'Needs review'})[v]||v}
function renderReview(data,decisions=[]){currentReview=data;let box=$('#review-result');box.hidden=false;box.className='results';box.innerHTML=`<div class="result-header"><div><div class="eyebrow">DRAFT ASSESSMENT</div><h2>Review the results</h2></div><span class="badge review">Human review required</span></div><p class="results-note">${escapeHTML(data.note||'AI-generated suggestions require review against approved guidance.')} ${cloudMode()?'Saved reviews are shared with demo users and may disappear after a restart.':'The review decisions and notes below are saved locally when you choose Save review.'}</p>${data.per_person?.per_person_cost!=null?`<div class="comparison"><strong>Event cost per guest: ${money(data.per_person.per_person_cost)}</strong>${data.per_person.limit!=null?` · Reviewer comparison: ${money(data.per_person.limit)} per person · ${data.per_person.exceeds_limit?'Above':'At or below'} comparison amount`:''}<p>Simple event total divided by total guests. Comparisons use the unrounded value. The comparison amount is user-entered and is not an approved policy limit.</p></div>`:''}<div class="summary-grid"><div class="metric"><span>Event total</span><strong>${money(data.totals.total)}</strong></div><div class="metric"><span>Suggested K Fund</span><strong>${money(data.totals.k_fund)}</strong></div><div class="metric"><span>Other / remainder</span><strong>${money(data.totals.other)}</strong></div><div class="metric"><span>Pending review</span><strong>${money(data.totals.pending)}</strong></div></div>${data.items.map((it,i)=>`<article class="result-item"><div class="result-item-head"><div><div class="eyebrow">LINE ITEM ${String(i+1).padStart(2,'0')}</div><h3>${escapeHTML(it.description)}</h3></div><span class="badge ${it.classification==='LEGAL_REVIEW'?'review':it.classification==='NOT_ALLOWABLE'?'no':''}">${escapeHTML(classificationLabel(it.classification))}</span></div>${data.intake?.sources?.[i]?.filename?`<p class="line-source">Receipt: ${escapeHTML(data.intake.sources[i].filename)}${data.intake.sources[i].page?' · page '+escapeHTML(data.intake.sources[i].page):''}</p>`:''}<p>${escapeHTML(it.rationale)}</p><div class="amounts"><span>EXPENSE<b>${money(it.amount)}</b></span><span>SUGGESTED K FUND<b>${money(it.k_fund_amount)}</b></span><span>OTHER / REMAINDER<b>${money(it.other_amount)}</b></span><span>PENDING<b>${money(it.pending_amount)}</b></span></div>${it.prorated?'<p class="results-note">A guest-count ratio was used for this suggested amount.</p>':''}${it.questions?.length?`<p><strong>Questions for review:</strong> ${it.questions.map(escapeHTML).join(' · ')}</p>`:''}${citations(it.citations)}<div class="review-controls"><select class="decision" aria-label="Reviewer decision for ${escapeHTML(it.description)}"><option value="Pending">Pending review</option><option value="Accepted">Accept suggestion</option><option value="Needs follow-up">Needs follow-up</option><option value="Not accepted">Do not accept</option></select><input class="decision-note" aria-label="Reviewer note for ${escapeHTML(it.description)}" placeholder="Reviewer note (optional)" value="${escapeHTML(decisions[i]?.note||'')}"></div></article>`).join('')}<div class="record-controls"><button id="save-review" class="usa-button secondary">${cloudMode()?'Save shared demo review':'Save review locally'}</button><button id="export-review" class="usa-button secondary">Download report</button><span id="save-message" class="save-message" role="status"></span></div><p class="results-note">The report is a self-contained HTML file; open it and use your browser’s Print command to save a PDF. It reflects the last analysis and current reviewer decisions.</p>`;box.querySelectorAll('.decision').forEach((el,i)=>el.value=decisions[i]?.decision||'Pending');$('#save-review').onclick=saveReview;$('#export-review').onclick=exportReview;box.scrollIntoView({behavior:'smooth',block:'start'})}
$('#review-form').addEventListener('submit',async e=>{e.preventDefault();if(reviewStep===1){if(validateStep(1))setReviewStep(2);return}if(reviewStep!==2||analysisPending||receiptPending||!validateStep(2))return;let f=Number($('#foreign-guests').value),t=Number($('#total-guests').value);if(f>t){showError('#review-error','Foreign guests cannot exceed total guests.');return}let items=$$('.line-entry').map(x=>({description:x.querySelector('.item-description').value.trim(),amount:Number(x.querySelector('.item-amount').value),source_filename:x.dataset.sourceFilename||null,source_page:x.dataset.sourcePage?Number(x.dataset.sourcePage):null}));let limit=$('#per-person-limit').value;let payload={event_name:$('#event-name').value.trim(),foreign_guests:f,total_guests:t,items,per_person_limit:limit?Number(limit):null,requester:$('#requester').value.trim(),event_date:$('#event-date').value,purpose:$('#event-purpose').value.trim()};const intake={requester:$('#requester').value.trim(),event_date:$('#event-date').value,purpose:$('#event-purpose').value.trim(),sources:$$('.line-entry').map(el=>({filename:el.dataset.sourceFilename||'',page:el.dataset.sourcePage||''}))};$('#review-error').hidden=true;const submissionSnapshot=snapshotReviewInputs(),submissionGeneration=reviewGeneration;const b=$('#analyze');analysisPending=true;updateAsyncControls();b.innerHTML='Analyzing event… <span>◌</span>';try{const result=await api('/api/analyze',{method:'POST',body:JSON.stringify(payload)});if(reviewGeneration!==submissionGeneration)return;if(snapshotReviewInputs()!==submissionSnapshot){showError('#review-error','Event details or expenses changed during analysis. Analyze again to review the current inputs.');return}result.intake=intake;reviewSnapshot=submissionSnapshot;renderReview(result);setReviewStep(3)}catch(err){if(reviewGeneration===submissionGeneration)showError('#review-error',err.message)}finally{analysisPending=false;updateAsyncControls();b.innerHTML='Analyze event <span>→</span>'}});
function showError(sel,message){const n=$(sel);n.textContent=message;n.hidden=false;n.scrollIntoView({behavior:'smooth',block:'center'})}
async function saveReview(){if(!currentReview)return;let decisions=$$('.decision').map((el,i)=>({decision:el.value,note:$$('.decision-note')[i].value}));let msg=$('#save-message');try{await api('/api/cases',{method:'POST',body:JSON.stringify({title:currentReview.event_name,data:{result:currentReview,decisions}})});msg.textContent=cloudMode()?'Saved to the shared demo temporarily. Reviews may disappear after a restart.':'Saved to this computer.'}catch(e){msg.textContent='Could not save: '+e.message}}
function exportReview(){
  if(!currentReview)return;const d=currentReview, intake=d.intake||{}, decisions=$$('.decision').map((el,i)=>({decision:el.value,note:$$('.decision-note')[i].value}));
  const esc=escapeHTML,per=d.per_person;
  const rows=(d.items||[]).map((it,i)=>`<section><h2>${i+1}. ${esc(it.description)} — ${money(it.amount)}</h2><p><strong>Draft suggestion:</strong> ${esc(classificationLabel(it.classification))}</p><p>${esc(it.rationale)}</p><p>Suggested K Fund: ${money(it.k_fund_amount)} · Other / remainder: ${money(it.other_amount)} · Pending: ${money(it.pending_amount)}</p>${intake.sources?.[i]?.filename?`<p><strong>Receipt source:</strong> ${esc(intake.sources[i].filename)}${intake.sources[i].page?' · page '+esc(intake.sources[i].page):''}</p>`:''}<p><strong>Reviewer decision:</strong> ${esc(decisions[i]?.decision||'Pending')}<br><strong>Reviewer note:</strong> ${esc(decisions[i]?.note||'None')}</p><h3>Supporting passages</h3>${it.citations?.length?it.citations.map(c=>`<div class="markdown-content"><strong>${esc(c.title||c.source_id||'Source')}</strong>${renderEvidenceMarkdown(c.excerpt||'')}</div>`).join(''):'<p>No supporting passage returned. Verify before relying on this assessment.</p>'}</section>`).join('');
  const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><title>K Fund review — ${esc(d.event_name)}</title><style>body{font:16px/1.55 Arial,sans-serif;color:#1b1b1b;max-width:850px;margin:3rem auto;padding:0 1.5rem}h1,h2{color:#162e51}h2{font-size:20px}section{border-top:1px solid #a9aeb1;margin-top:1.5rem;padding-top:1rem;break-inside:avoid}.markdown-content table{border-collapse:collapse;width:100%}.markdown-content th,.markdown-content td{border:1px solid #a9aeb1;padding:.35rem;text-align:left}.markdown-content pre{white-space:pre-wrap}.notice{border-left:6px solid #ffb81c;background:#faf3d1;padding:1rem}.summary{background:#f0f0f0;padding:1rem}@media print{body{margin:0;padding:0}.notice,.summary{print-color-adjust:exact}}</style></head><body><p>EDCS · K FUND WORKSPACE</p><h1>Event review report</h1><p class="notice"><strong>Prototype and human review required.</strong> Included guidance is illustrative and not approved policy. Verify all expense details and source documents.</p><h2>${esc(d.event_name)}</h2><p><strong>Requester:</strong> ${esc(intake.requester||'Not provided')}<br><strong>Event date:</strong> ${esc(intake.event_date||'Not provided')}<br><strong>Purpose:</strong> ${esc(intake.purpose||'Not provided')}<br><strong>Foreign guests / total guests:</strong> ${esc(d.foreign_guests)} / ${esc(d.total_guests)}</p><div class="summary"><strong>Event total:</strong> ${money(d.totals.total)} · <strong>Suggested K Fund:</strong> ${money(d.totals.k_fund)} · <strong>Other:</strong> ${money(d.totals.other)} · <strong>Pending:</strong> ${money(d.totals.pending)}${per?.per_person_cost!=null?`<p><strong>Event cost per guest:</strong> ${money(per.per_person_cost)}${per.limit!=null?` · <strong>Reviewer comparison:</strong> ${money(per.limit)} (${per.exceeds_limit?'above':'at or below'})`:''}. Event total divided by all guests; comparison uses the unrounded value. The comparison amount is user-entered and is not an approved policy limit.</p>`:''}</div>${rows}<p>Generated ${esc(new Date().toLocaleString())}. Decisions and notes reflect this export.</p></body></html>`;
  const url=URL.createObjectURL(new Blob([html],{type:'text/html;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='kfund-review-report.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function loadReview(result,decisions){
  reviewGeneration++;
  $('#event-name').value=result.event_name||'';
  $('#requester').value=result.intake?.requester||'';
  $('#event-date').value=result.intake?.event_date||'';
  $('#event-purpose').value=result.intake?.purpose||'';
  $('#per-person-limit').value=result.per_person?.limit??'';
  $('#foreign-guests').value=result.foreign_guests??0;
  $('#total-guests').value=result.total_guests??0;
  $('#line-items').innerHTML='';
  (result.items||[]).forEach((item,i)=>row(item.description,item.amount,{source_filename:result.intake?.sources?.[i]?.filename,source_page:result.intake?.sources?.[i]?.page}));
  if(!result.items?.length)row();
  $('#review-error').hidden=true;
  go('review');
  reviewSnapshot=snapshotReviewInputs();
  renderReview(result,decisions);
  setReviewStep(3);
}
async function loadCases(){if(deploymentMode==='unknown')return;let container=$('#saved-cases');if(!container){container=document.createElement('div');container.id='saved-cases';$('.overview-footer').before(container)}try{const d=await api('/api/cases');if(!d.cases?.length){container.innerHTML='';return}container.innerHTML=`<div class="section-heading" style="margin-top:45px"><div><div class="eyebrow">${cloudMode()?'SHARED DEMO RECORDS':'LOCAL RECORDS'}</div><h2>Saved reviews</h2></div></div>${d.cases.map(c=>`<div class="source-item"><div class="source-icon">▤</div><div><h3>${escapeHTML(c.title)}</h3><p>${cloudMode()?'Shared demo record · May disappear after a restart':'Saved on this computer'}</p></div><button class="text-button open-case" data-id="${escapeHTML(c.id)}">Open review →</button></div>`).join('')}`;container.querySelectorAll('.open-case').forEach(el=>el.onclick=async()=>{try{let c=await api('/api/cases/'+encodeURIComponent(el.dataset.id));loadReview(c.data.result,c.data.decisions)}catch(e){alert(e.message)}})}catch{container.innerHTML=''}}
$$('.suggest').forEach(b=>b.addEventListener('click',()=>{$('#question').value=b.textContent;$('#question').focus()}));
let searchHistory=[];
$('#clear-conversation').addEventListener('click',()=>{searchHistory=[];$('#search-result').innerHTML='';$('#search-result').hidden=true;$('#clear-conversation').hidden=true;$('#question').value='';$('#search-error').hidden=true;$('#question').focus()});
$('#search-form').addEventListener('submit',async e=>{e.preventDefault();let b=$('#search-button');$('#search-error').hidden=true;b.disabled=true;b.innerHTML='Searching… <span>◌</span>';let question=$('#question').value.trim();try{const d=await api('/api/search',{method:'POST',body:JSON.stringify({question,history:searchHistory.slice(-12)})});searchHistory.push({role:'user',content:question},{role:'assistant',content:d.answer});searchHistory=searchHistory.slice(-12);let box=$('#search-result');box.hidden=false;let entry=document.createElement('div');entry.className='conversation-turn';entry.innerHTML=`<div class="result-item question-item"><div class="eyebrow">YOUR QUESTION</div><p>${escapeHTML(question).replace(/\n/g,'<br>')}</p></div><div class="result-item"><div class="eyebrow">DRAFT ANSWER</div><div class="answer markdown-content">${renderMarkdown(d.answer)}</div><p class="results-note">${escapeHTML(d.note||'Review all cited material and verify guidance before use.')} Previous conversation is context, not evidence.</p>${citations(d.citations)}</div>`;box.appendChild(entry);$('#clear-conversation').hidden=false;$('#question').value='';entry.scrollIntoView({behavior:'smooth',block:'start'})}catch(err){showError('#search-error',err.message)}finally{b.disabled=false;b.innerHTML='Search guidance <span>↗</span>'}});
async function loadSources(){try{let d=await api('/api/sources');sourceCache=d.sources||[];$('#sources-list').innerHTML=sourceCache.length?sourceCache.map(s=>`<div class="source-item"><div class="source-icon">▥</div><div><h3>${escapeHTML(s.title)}</h3><p>Sample guidance · Workspace file</p></div><button class="text-button open-source" data-id="${escapeHTML(s.id)}">Read source →</button></div>`).join(''):'<p>No sources found.</p>';$$('.open-source').forEach(b=>b.onclick=()=>{let source=sourceCache.find(s=>s.id===b.dataset.id);let d=$('#source-detail');d.hidden=false;d.innerHTML=`<div class="panel"><button class="text-button close-source">Close ×</button><div class="eyebrow">SAMPLE SOURCE</div><h2 style="margin:10px 0">${escapeHTML(source.title)}</h2><div class="source-content markdown-content">${renderMarkdown(source.content)}</div></div>`;d.querySelector('.close-source').onclick=()=>d.hidden=true;d.scrollIntoView({behavior:'smooth'})})}catch(e){$('#sources-list').innerHTML=`<div class="error">${escapeHTML(e.message)}</div>`}}
status().then(loadCases);
