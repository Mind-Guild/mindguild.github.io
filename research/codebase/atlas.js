/* A source-linked, offline-capable atlas. No credentials or API calls. */
(() => {
  'use strict';
  const data = window.MIND_GUILD_MAP;
  if (!data) return;
  const $ = id => document.getElementById(id);
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const groups = new Map(data.groups.map(g => [g.id, g]));
  const files = new Map(data.files.map(f => [f.path, f]));
  const base = `https://github.com/${data.repository}/blob/${data.revision}/`;
  const sourceURL = (path, line) => base + path.split('/').map(encodeURIComponent).join('/') + (line ? `#L${line}` : '');
  const colors = {benchmark:'#edb76a',layer1:'#8acbb9',support:'#b9b2ea',archive:'#9ca6b0'};
  const positions = {entry:[30,74],agents:[405,74],envs:[780,74],ops:[30,239],benchmarks:[405,239],contracts:[780,239],l1experiments:[30,464],l1runtime:[405,464],l1model:[780,464],verification:[30,629],successor:[405,629],l1contracts:[780,629]};
  const state = {view:'architecture',module:'l1runtime',stage:'slots',file:'src/mind_guild/layer1/runtime/engine.py',group:'all',query:'',trace:-1};
  const pipeline = [
    {id:'sensors',xy:[30,74],title:'Sensor adapters',sub:'World · demand · clocked',group:'l1runtime',description:'Physical sources retain their identity and origination time. Clock translation maps native ticks into common time; interrogated replies retain the consumer demand timestamp.',paths:['src/mind_guild/layer1/runtime/adapters.py','src/mind_guild/layer1/runtime/clocks.py'],note:'Asynchronous arrival; independent source sequences.'},
    {id:'mailbox',xy:[405,74],title:'Timestamp mailboxes',sub:'Bounded interval reads',group:'l1runtime',description:'Fixed-capacity modality mailboxes sort by timestamp and deterministic ties. Each scheduled read consumes the current Layer 1 interval, retains future samples, and accounts for late and overflow drops.',paths:['src/mind_guild/layer1/runtime/mailbox.py','src/mind_guild/layer1/runtime/engine.py'],note:'Read interval: ((k−1)T, kT].'},
    {id:'encoding',xy:[780,74],title:'Encode and project',sub:'Private widths → shared tokens',group:'l1model',description:'Modality encoders produce native-width representations. ProvenanceProjection maps them into the shared token width; concatenation preserves physical-source and modality provenance.',paths:['src/mind_guild/layer1/models/perception.py','src/mind_guild/layer1/interfaces/tensors.py'],note:'Differentiable inside the model backend.'},
    {id:'slots',xy:[780,269],title:'Predict and refine slots',sub:'Prior state + competitive attention',group:'l1model',description:'SlotPredictor initializes from the preceding slot state. Competitive attention and recurrent refinement bind the new tokens into slots using a fixed iteration count; final-iterate attention supplies liveness evidence.',paths:['src/mind_guild/layer1/models/perception.py','src/mind_guild/layer1/runtime/engine.py'],note:'Reference policy: six refinement iterations.'},
    {id:'state',xy:[405,269],title:'Publish slots and liveness',sub:'S / f double buffer',group:'l1runtime',description:'The runtime combines the refined slots with persistent liveness, then publishes a complete S/f pair. Exactly two publication backing pairs are used. Reader leases prevent reuse while a pair is still in use.',paths:['src/mind_guild/layer1/runtime/state.py','src/mind_guild/layer1/runtime/engine.py'],note:'The previous S/f state feeds the next prediction.'},
    {id:'history',xy:[30,269],title:'Aligned trajectory history',sub:'Slots · live mask · actions',group:'l1runtime',description:'A bounded trajectory buffer stores published slots, liveness and aligned actions. Independent SFA and InfoNCE snapshots read this history at their own scheduled periods.',paths:['src/mind_guild/layer1/runtime/state.py','src/mind_guild/layer1/interfaces/payloads.py'],note:'Bounded history with checkpointable state.'},
    {id:'sfa',xy:[30,494],title:'Incremental SFA',sub:'Slow features → Y',group:'l1runtime',description:'Incremental slow-feature analysis updates from the trajectory history and publishes features for live rows. Y remains bitwise held between its scheduled publications.',paths:['src/mind_guild/layer1/runtime/statistics.py','src/mind_guild/layer1/runtime/ports.py'],note:'Reference SFA period: 40 ms.'},
    {id:'mi',xy:[405,494],title:'InfoNCE estimator',sub:'Per-slot information → ρ',group:'l1runtime',description:'The InfoNCE critic consumes aligned history and valid actions to estimate per-slot information. Its reused workspaces reduce temporaries, while whole-runtime allocation-free acceptance remains open.',paths:['src/mind_guild/layer1/runtime/statistics.py','src/mind_guild/layer1/runtime/ports.py'],note:'Reference MI period: 60 ms.'},
    {id:'ports',xy:[780,494],title:'Leased output ports',sub:'S · f · Y · ρ',group:'l1runtime',description:'read_outputs() leases a consistent read-only bundle of the latest S/f pair and the held Y/rho outputs. Slow outputs can retain stale values for vacant rows, so consumers must use the liveness mask.',paths:['src/mind_guild/layer1/runtime/ports.py','src/mind_guild/layer1/runtime/engine.py'],note:'Hold semantics differ from a new publication every tick.'},
    {id:'consumers',xy:[780,679],title:'Live-row consumers',sub:'Read the active representation',group:'l1runtime',description:'read_live() filters the output bundle by f and returns only live rows. This is the default reference consumer boundary. Runtime state, holds, statistics and pending ingress can be checkpointed for continuation.',paths:['src/mind_guild/layer1/runtime/engine.py','src/mind_guild/layer1/checkpoint.py'],note:'Consumer boundary; no downstream policy integration implied.'}
  ];
  const stages = new Map(pipeline.map(p => [p.id,p]));
  const groupEdges = new Map();
  data.edges.forEach(e => {
    const from = files.get(e.from).group, to = files.get(e.to).group;
    if (from === to || !positions[from] || !positions[to]) return;
    const key = `${from}:${to}`;
    if (!groupEdges.has(key)) groupEdges.set(key,{from,to,count:0,loader:false});
    const edge = groupEdges.get(key); edge.count++; edge.loader ||= e.kind === 'loader';
  });
  function defs(prefix) {
    return `<defs><marker id="${prefix}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#7893a5"/></marker><marker id="${prefix}-active" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#f3c17a"/></marker></defs>`;
  }
  function node(id,xy,title,subtitle,track,count,index,selected) {
    const [x,y] = xy, col = colors[track] || colors.layer1;
    return `<g class="node${selected?' selected':''}" role="button" tabindex="0" aria-pressed="${!!selected}" aria-label="${esc(title)}: ${esc(subtitle)}" data-node="${esc(id)}" transform="translate(${x},${y})"><title>${esc(title)}. ${esc(subtitle)}. Select for details.</title><rect width="270" height="103" rx="4"/><circle cx="20" cy="21" r="3" fill="${col}"/><text class="node-index" x="31" y="25" fill="${col}">${String(index+1).padStart(2,'0')}</text><text class="node-title" x="18" y="52">${esc(title)}</text><text class="node-subtitle" x="18" y="72">${esc(subtitle)}</text><text class="node-count" x="18" y="91">${esc(count)}</text></g>`;
  }
  function route(from,to,reverse=false) {
    const [x,y] = from,[tx,ty] = to, w=270,h=103;
    if (y === ty) {
      if (Math.abs(tx-x) > 400) return `M${x+w/2},${y} V${y-22} H${tx+w/2} V${ty-3}`;
      const left = tx < x, sy=y+h/2+(reverse?10:-6);
      return `M${left?x:x+w},${sy} H${left?tx+w+3:tx-3}`;
    }
    const down=ty>y, startY=down?y+h:y,endY=down?ty-3:ty+h+3;
    const sx=x+w/2,ex=tx+w/2,mid=(startY+endY)/2;
    return `M${sx},${startY} C${sx},${mid} ${ex},${mid} ${ex},${endY}`;
  }
  function edgePath(d,prefix,active=false,extra='') {
    return `<path class="diagram-edge ${extra} ${active?'active':''}" d="${d}" marker-end="url(#${prefix}-${active?'active':'arrow'})"/>`;
  }
  function renderArchitecture() {
    let svg=defs('arch')+'<rect class="lane-bg" x="13" y="48" width="1054" height="334" rx="6"/><rect class="lane-bg" x="13" y="438" width="1054" height="328" rx="6"/><text class="lane-title" x="30" y="29">BENCHMARKS + MEETING OPERATIONS</text><text class="lane-title" x="30" y="420">S3Q LAYER 1 + SHARED VERIFICATION</text>';
    for (const e of groupEdges.values()) {
      if (e.from === 'verification' && state.module !== 'verification') continue;
      const active=e.from===state.module||e.to===state.module;
      svg += edgePath(route(positions[e.from],positions[e.to],e.from==='l1model'), 'arch', active, e.loader?'loader':'');
    }
    Object.entries(positions).forEach(([id,xy],i) => {
      const g=groups.get(id); svg += node(id,xy,g.label,g.subtitle,g.track,`${g.count} tracked ${g.count===1?'file':'files'}`,i,id===state.module);
    });
    $('architecture-graph').innerHTML=svg;
    const g=groups.get(state.module);
    const outbound=[...groupEdges.values()].filter(e=>e.from===g.id).reduce((sum,e)=>sum+e.count,0);
    $('module-detail').innerHTML=`<div class="eyebrow">${esc(g.track==='layer1'?'S3Q reference implementation':g.track==='benchmark'?'Agent benchmark track':'Supporting tools')}</div><h3>${esc(g.label)}</h3><p>${esc(g.description)}</p><div class="detail-meta">${g.count} tracked files<br>${outbound} cross-module import pairs</div><div class="sources"><div class="small-heading">Start with these files</div>${sourceItems(g.featured)}</div><button class="button" data-open-group="${g.id}">Explore this module <span aria-hidden="true">→</span></button>`;
  }
  function sourceItems(paths) {
    return paths.map(p=>`<a class="source-item" href="${sourceURL(p)}" target="_blank" rel="noopener"><code>${esc(p)} ↗</code><small>${files.get(p)?.lines?`${files.get(p).lines.toLocaleString()} lines · `:''}Pinned source</small></a>`).join('');
  }
  function renderPipeline() {
    let svg=defs('flow')+'<text class="lane-title" x="30" y="29">PERCEPTION AND TEMPORAL STATE</text><text class="lane-title" x="30" y="458">SLOW READERS AND HELD OUTPUTS</text>';
    const edges=[['sensors','mailbox'],['mailbox','encoding'],['encoding','slots'],['slots','state'],['state','history'],['history','sfa'],['history','mi'],['mi','ports'],['ports','consumers']];
    edges.forEach(([from,to])=>svg+=edgePath(route(stages.get(from).xy,stages.get(to).xy),'flow',from===state.stage||to===state.stage));
    const active=(a,b)=>state.stage===a||state.stage===b;
    svg+=edgePath('M540,269 C540,216 915,216 915,266','flow',active('state','slots'),'loader');
    svg+='<text class="edge-label" x="645" y="224">previous S / f → prediction</text>';
    svg+=edgePath('M300,549 C485,612 650,612 780,570','flow',active('sfa','ports'));
    svg+='<text class="edge-label" x="525" y="612">held Y</text>';
    svg+=edgePath('M675,320 C745,320 1055,355 1055,468 V545 H1053','flow',active('state','ports'));
    svg+='<text class="edge-label" x="942" y="403">current S / f</text>';
    pipeline.forEach((p,i)=>svg+=node(p.id,p.xy,p.title,p.sub,'layer1',p.note.length>42?'Reference runtime':p.note,i,state.stage===p.id));
    svg+='<text class="edge-label" x="30" y="722">S = slots · f = live mask</text><text class="edge-label" x="30" y="744">Y = slow features · ρ = information estimate</text>';
    $('pipeline-graph').innerHTML=svg;
    const p=stages.get(state.stage);
    $('pipeline-detail').innerHTML=`<div class="eyebrow">Layer 1 / stage ${String(pipeline.indexOf(p)+1).padStart(2,'0')}</div><h3>${esc(p.title)}</h3><p>${esc(p.description)}</p><div class="detail-meta">${esc(p.note)}</div><div class="sources"><div class="small-heading">Source implementation</div>${sourceItems(p.paths)}</div><button class="button" data-open-file="${p.paths[0]}">Inspect files &amp; imports <span aria-hidden="true">→</span></button>`;
    $('trace-step').innerHTML=`${state.trace<0?'Follow the flow':state.trace===pipeline.length-1?'Restart the flow':`Next: ${esc(pipeline[state.trace+1].title)}`} <span aria-hidden="true">→</span>`;
  }
  function renderFiles() {
    const q=state.query.toLowerCase().trim();
    const matching=data.files.filter(f=>(state.group==='all'||f.group===state.group)&&(!q||`${f.path} ${f.symbols.map(s=>s.name).join(' ')}`.toLowerCase().includes(q)));
    if (matching.length && !matching.some(f=>f.path===state.file)) state.file=matching[0].path;
    $('file-count').textContent=`${matching.length} of ${data.files.length} files`;
    $('file-list').innerHTML=matching.length?matching.map(f=>`<button class="file-row${f.path===state.file?' selected':''}" data-file="${esc(f.path)}" aria-pressed="${f.path===state.file}"><code>${esc(f.path)}</code><small>${esc(groups.get(f.group).label)}${f.lines?` · ${f.lines.toLocaleString()} lines`:''}</small></button>`).join(''):'<p class="empty">No matching files. Try another path or symbol, or reset the filters.</p>';
    $('group-filter').value=state.group;
    renderFileDetail();
  }
  function renderFileDetail() {
    const f=files.get(state.file);
    const outgoing=data.edges.filter(e=>e.from===f.path),incoming=data.edges.filter(e=>e.to===f.path);
    const links=(edges,inbound)=>edges.length?edges.map(e=>{
      const path=inbound?e.from:e.to;
      return `<button class="dependency-link" data-file="${esc(path)}">${esc(path)}<small>${e.kind==='loader'?'Explicit file loader':'Static import'} · ${inbound?'importer':'this file'} line ${e.line}</small></button>`;
    }).join(''):'<p class="empty">No internal Python imports recorded.</p>';
    $('file-detail').innerHTML=`<div class="eyebrow">${esc(groups.get(f.group).label)} / ${f.python?'Python source':'Repository material'}</div><h3>${esc(f.path.split('/').pop())}</h3><code class="file-path">${esc(f.path)}</code><div class="file-meta">${f.lines?`${f.lines.toLocaleString()} lines · `:''}${incoming.length} importers · ${outgoing.length} internal dependencies</div><a class="button" href="${sourceURL(f.path)}" target="_blank" rel="noopener">Open pinned source <span aria-hidden="true">↗</span></a>${f.python?`<div class="dependency-graph">${miniGraph(f,incoming,outgoing)}</div><p class="mini-note">Importer → dependency. Up to four neighbors per side are drawn; complete lists appear below.</p><div class="dependency-columns"><section><h4>Imported by (${incoming.length})</h4>${links(incoming,true)}</section><section><h4>Imports (${outgoing.length})</h4>${links(outgoing,false)}</section></div><div class="symbols"><h4>Top-level symbols (${f.symbols.length})</h4><div class="symbol-list">${f.symbols.length?f.symbols.map(s=>`<a href="${sourceURL(f.path,s.line)}" target="_blank" rel="noopener" title="${esc(s.kind)} · line ${s.line}">${esc(s.name)} <span aria-hidden="true">↗</span></a>`).join(''):'<p class="empty">No top-level classes or functions.</p>'}</div></div>`:'<p class="empty" style="margin-top:28px">This file provides documentation, configuration, evidence or supporting material. Static Python dependencies are available for Python source files.</p>'}`;
  }
  function miniGraph(f,incoming,outgoing) {
    const inNodes=incoming.slice(0,4),outNodes=outgoing.slice(0,4),height=Math.max(210,Math.max(inNodes.length,outNodes.length)*50+62),cy=height/2;
    const item=(path,x,y,selected=false)=>{
      const short=path.split('/').pop(),label=short.length>24?short.slice(0,21)+'…':short;
      return `<g class="dependency-node${selected?' selected':''}" role="button" tabindex="0" data-file="${esc(path)}" aria-label="Inspect ${esc(path)}"><title>${esc(path)}</title><rect x="${x}" y="${y}" width="210" height="34" rx="3"/><text x="${x+10}" y="${y+21}">${esc(label)}</text></g>`;
    };
    let s=`<svg viewBox="0 0 760 ${height}" role="group" aria-label="Static dependencies for ${esc(f.path)}">${defs('mini')}<text class="dependency-label" x="15" y="22">IMPORTED BY</text><text class="dependency-label" x="275" y="22">SELECTED FILE</text><text class="dependency-label" x="535" y="22">IMPORTS</text>`;
    inNodes.forEach((e,i)=>{const y=42+i*50;s+=edgePath(`M225,${y+17} C250,${y+17} 250,${cy} 272,${cy}`,'mini');s+=item(e.from,15,y);});
    outNodes.forEach((e,i)=>{const y=42+i*50;s+=edgePath(`M485,${cy} C510,${cy} 510,${y+17} 532,${y+17}`,'mini',false,e.kind==='loader'?'loader':'');s+=item(e.to,535,y);});
    return s+item(f.path,275,cy-17,true)+'</svg>';
  }
  function syncHash() {
    const params=new URLSearchParams({view:state.view});
    if(state.view==='architecture') params.set('module',state.module);
    if(state.view==='pipeline') params.set('stage',state.stage);
    if(state.view==='files') {params.set('file',state.file);if(state.group!=='all')params.set('group',state.group);if(state.query)params.set('q',state.query);}
    history.replaceState(null,'','#'+params.toString());
  }
  function showView(view,update=true) {
    if(!['architecture','pipeline','files'].includes(view))view='architecture';
    state.view=view;
    document.querySelectorAll('[data-tab]').forEach(b=>{const selected=b.dataset.tab===view;b.setAttribute('aria-selected',String(selected));b.tabIndex=selected?0:-1;});
    ['architecture','pipeline','files'].forEach(v=>{$('panel-'+v).hidden=v!==view;});
    if(view==='architecture')renderArchitecture();else if(view==='pipeline')renderPipeline();else renderFiles();
    if(update)syncHash();
  }
  function openFile(path) {
    if(!files.has(path))return;
    state.file=path;state.group='all';state.query='';$('file-search').value='';showView('files');
  }
  function activate(event) {
    const target=event.target.closest('[data-node],[data-open-group],[data-open-file],[data-file],[data-tab]');
    if(!target)return;
    if(target.dataset.tab){showView(target.dataset.tab);return;}
    if(target.dataset.node){if(state.view==='architecture'){state.module=target.dataset.node;renderArchitecture();}else{state.stage=target.dataset.node;state.trace=pipeline.findIndex(p=>p.id===state.stage);renderPipeline();}syncHash();return;}
    if(target.dataset.openGroup){state.group=target.dataset.openGroup;state.query='';$('file-search').value='';state.file=groups.get(state.group).featured[0];showView('files');return;}
    if(target.dataset.openFile){openFile(target.dataset.openFile);return;}
    if(target.dataset.file){if(target.closest('#file-detail')){openFile(target.dataset.file);return;}state.file=target.dataset.file;renderFiles();syncHash();}
  }
  document.addEventListener('click',activate);
  document.addEventListener('keydown',event=>{
    if(event.target.matches('svg [role=button]')&&(event.key==='Enter'||event.key===' ')){event.preventDefault();const key=event.target.dataset.node?'data-node':'data-file',id=event.target.getAttribute(key);activate(event);const svg=state.view==='files'?$('file-detail'):$(state.view==='architecture'?'architecture-graph':'pipeline-graph');svg.querySelector(`[${key}="${CSS.escape(id)}"]`)?.focus();}
    if(event.target.matches('[data-tab]')&&['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();const tabs=[...document.querySelectorAll('[data-tab]')],index=tabs.indexOf(event.target),next=event.key==='Home'?0:event.key==='End'?2:(index+(event.key==='ArrowRight'?1:2))%3;showView(tabs[next].dataset.tab);tabs[next].focus();}
  });
  $('trace-step').addEventListener('click',()=>{state.trace=(state.trace+1)%pipeline.length;state.stage=pipeline[state.trace].id;renderPipeline();syncHash();});
  $('file-search').addEventListener('input',event=>{state.query=event.target.value;renderFiles();syncHash();});
  $('group-filter').addEventListener('change',event=>{state.group=event.target.value;renderFiles();syncHash();});
  $('clear-filters').addEventListener('click',()=>{state.query='';state.group='all';$('file-search').value='';renderFiles();syncHash();});
  $('stats').innerHTML=[['files','Files mapped'],['python','Python files'],['imports','Internal import pairs'],['testFiles','Test files']].map(([key,label])=>`<div class="stat"><b>${data.stats[key].toLocaleString()}</b><span>${label}</span></div>`).join('');
  $('snapshot').href=`https://github.com/${data.repository}/tree/${data.revision}`;
  $('snapshot').title=`Source commit ${data.revision} · ${data.committed}`;
  $('snapshot-date').textContent=new Intl.DateTimeFormat('en-GB',{day:'2-digit',month:'short',year:'numeric',timeZone:'America/New_York'}).format(new Date(data.committed));
  document.querySelector('.snapshot-label').innerHTML='<i></i> Source snapshot · ET';
  $('revision').textContent=data.revision.slice(0,10);
  $('verification-link').href=sourceURL('docs/layer1/VERIFICATION.md');
  $('method-text').textContent=data.method;
  $('group-filter').innerHTML='<option value="all">All modules</option>'+data.groups.map(g=>`<option value="${g.id}">${esc(g.label)} (${g.count})</option>`).join('');
  function loadHash() {
    const p=new URLSearchParams(location.hash.slice(1));
    if(groups.has(p.get('module'))&&positions[p.get('module')])state.module=p.get('module');
    if(stages.has(p.get('stage')))state.stage=p.get('stage');
    if(files.has(p.get('file')))state.file=p.get('file');
    state.group=groups.has(p.get('group'))?p.get('group'):'all';state.query=p.get('q')||'';$('file-search').value=state.query;
    showView(p.get('view')||'architecture',false);
  }
  window.addEventListener('hashchange',loadHash);loadHash();
})();
