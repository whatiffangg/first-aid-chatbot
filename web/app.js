const $=s=>document.querySelector(s);let history=[];let busy=false;
function el(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n}
function tab(name){document.querySelectorAll('.tab').forEach(n=>n.hidden=n.id!==name);document.querySelectorAll('nav button').forEach(n=>n.classList.toggle('active',n.dataset.tab===name))}
document.querySelectorAll('nav button').forEach(n=>n.onclick=()=>tab(n.dataset.tab));
function userMessage(question){$('.welcome')?.remove();const n=el('div','message user');n.append(el('div','role','คุณ'),el('div','answer',question));$('#messages').append(n)}
function renderAnswer(row){const n=el('div','message assistant');n.append(el('div','role',row.model||'ผลการค้นหลักฐาน'));if(row.quality_review){const g=row.quality_review;n.append(el('div',g.safety<=1?'error':'meta',`คะแนน LLM ${g.total}/20 · ความปลอดภัย ${g.safety}/4 · ${g.reason}`))}const displayAnswer=row.answer.replace(/[ \t]*\[S\d+\]/g,'').replace(/[ \t]+$/gm,'').trim();n.append(el('div','answer',displayAnswer));n.append(el('div','meta',`${row.id||''} · ${row.mode} · k=${row.k} · ${row.elapsed_seconds} วินาที${row.finish_reason==='length'?' · คำตอบถึงขีดจำกัด tokens':''}`));
 const sources=el('div','sources');sources.append(el('div','role','หลักฐานที่ค้นพบ'));
 (row.contexts||[]).forEach((c,i)=>{const d=el('div','source');const a=el('a',null,`[S${i+1}] ${c.title_th} — ${c.publisher}`);a.href=c.source_url;a.target='_blank';a.rel='noopener noreferrer';d.append(a,el('span',null,` · ${c.retrieval} · similarity ${c.score.toFixed(3)}`));const detail=el('details');detail.append(el('summary',null,'อ่านข้อความต้นฉบับ'),el('pre',null,c.text));d.append(detail);sources.append(d)});n.append(sources);
 if(row.graph_paths?.length){const d=el('details');d.append(el('summary',null,'เส้นทางค้นข้อมูลใน Knowledge Graph'),el('pre',null,JSON.stringify(row.graph_paths,null,2)));n.append(d)}
 if(row.invalid_citations?.length)n.append(el('div','error','พบรหัสอ้างอิงไม่ถูกต้อง ต้องตรวจคำตอบอีกครั้ง'));
 $('#messages').append(n);return n}
$('#ask').onsubmit=async e=>{
 e.preventDefault();if(busy)return;
 const question=$('#question').value.trim();if(!question)return;
 userMessage(question);$('#question').value='';busy=true;$('#send').disabled=true;$('#send').textContent='กำลังตอบ…';
 const loading=el('div','meta','กำลังค้นข้อมูลและตอบเป็นขั้นตอน… 0 วินาที');$('#messages').append(loading);
 const started=Date.now();const controller=new AbortController();
 const deadline=setTimeout(()=>controller.abort(),100000);
 const timer=setInterval(()=>{const seconds=Math.floor((Date.now()-started)/1000);loading.textContent=`กำลังประมวลผล… ${seconds} วินาที${seconds>=20?' · ครั้งแรกอาจใช้เวลาโหลดโมเดล':''}`},1000);
 try{
  const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({question,mode:$('#mode').value,k:Number($('#k').value),history})});
  const data=await r.json();if(!r.ok)throw Error(data.detail||'ไม่สำเร็จ');
  renderAnswer(data);history.push({role:'user',content:question},{role:'assistant',content:data.answer});history=history.slice(-4)
 }catch(err){$('#messages').append(el('div','error',err.name==='AbortError'?'รอนานเกิน 100 วินาที กรุณาตรวจว่า Ollama เปิดอยู่ และใช้โมเดล firstaid-qwen แล้วลองใหม่':err.message))}
 finally{clearTimeout(deadline);clearInterval(timer);loading.remove();busy=false;$('#send').disabled=false;$('#send').textContent='ส่งคำถาม ↗'}
};
document.querySelectorAll('.examples button').forEach(n=>n.onclick=()=>{$('#question').value=n.textContent;$('#question').focus()});$('#clear').onclick=()=>{history=[];$('#messages').replaceChildren();$('#question').focus()};
function loadRun(r){tab('chat');$('#messages').replaceChildren();history=[];$('#mode').value=r.mode;$('#k').value=String(r.k);userMessage(r.question);renderAnswer(r)}
async function init(){try{const s=await(await fetch('/api/status')).json();$('#index-info').textContent=s.ready?`${s.index.documents} หัวข้อ · ${s.index.chunks} chunks\nQdrant + Knowledge Graph`:'ยังไม่มีฐานข้อมูล';const g=await(await fetch('/api/graph')).json();const labels=Object.fromEntries(g.nodes.map(n=>[n.id,n.label]));g.nodes.forEach(n=>$('#graph-view').append(el('span','graph-card',n.label)));g.edges.forEach(e=>$('#graph-view').append(el('div','edge',`${labels[e.from]} → ${labels[e.to]}`)));const ev=await(await fetch('/api/evaluation')).json();if(ev.status==='not_run')$('#eval-view').textContent=ev.message;else{const t=el('table');const head=el('tr');['ระบบ','กลุ่ม','จำนวนข้อ','คะแนน / 20','Recall หลักฐาน','เวลาตอบเฉลี่ย'].forEach(s=>head.append(el('th',null,s)));t.append(head);(ev.groups||[]).forEach(r=>{const tr=el('tr');[r.mode==='graph'?'Vector + Graph':'Vector',r.group==='direct'?'คำถามตรง':'คำถามเชื่อมโยง',r.n,r.mean_score??'ยังไม่มีคะแนน',r.evidence_recall.toFixed(3),`${r.mean_seconds.toFixed(1)} วินาที`].forEach(v=>tr.append(el('td',null,String(v))));t.append(tr)});$('#eval-view').append(t);(ev.averages||[]).forEach(a=>{if(a.macro_mean_score!=null)$('#eval-view').append(el('p','meta',`ค่าเฉลี่ยสองกลุ่ม ${a.mode==='graph'?'Vector + Graph':'Vector'}: ${a.macro_mean_score.toFixed(2)}/20 (${(a.macro_mean_score/20*100).toFixed(2)}%)`))});$('#eval-view').append(el('p','muted',ev.evaluator?'ผู้ประเมิน: Codex ซึ่งเป็น LLM คนละโมเดลกับ Qwen · ยังไม่ใช่ผลจากมนุษย์หรือการรับรองทางคลินิก':'ยังไม่มีผู้ประเมินคุณภาพคำตอบ'))}
const runs=await(await fetch('/api/runs')).json();runs.forEach(r=>{const b=el('button','run',`${r.id} · ${r.question}`);b.onclick=()=>loadRun(r);$('#run-list').append(b)});
const id=new URLSearchParams(location.search).get('run');if(id){const r=await(await fetch('/api/run/'+encodeURIComponent(id))).json();loadRun(r)}window.appReady=true}catch(e){$('#index-info').textContent=e.message;window.appReady=true}}
init();
