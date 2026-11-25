// 读取FreeCAD导出的三角网格和装配步骤；模型、步骤、零件使用同一份数据。
const routeColors={main:'#68418b',emergency:'#a58bb9',return:'#aab4b9'};
const partColors={union:'#454c50',unionClear:'#acc6cd',unionWhite:'#edf0ef',elbow:'#383e43',valve:'#2f353a',check:'#e9eeec',gate:'#242a2f',clear:'#6eabb9',support:'#788b80',handle:'#b42130',bulkhead:'#41484e'};

export function componentColor(o) {
  if(o.kind==='clear')return partColors.clear;
  if(o.kind==='support')return partColors.support;
  if(o.id==='GateHandwheel'||o.id.endsWith('Handle'))return partColors.handle;
  if(o.id==='ReturnCheckBody')return partColors.unionClear;
  if(o.id==='ReturnCheckUnions')return partColors.unionWhite;
  if(o.id==='ReturnCheckFlap')return '#64777c';
  if(o.id.includes('Union'))return o.finish==='white'?partColors.unionWhite:o.finish==='clear'?partColors.unionClear:partColors.union;
  if(o.id.startsWith('Gate'))return partColors.gate;
  if(/ValveBody|IsolationBody/.test(o.id))return partColors.valve;
  if(o.id==='ReturnTee'||o.id.startsWith('ReturnElbow'))return partColors.elbow;
  if(/Bulkhead|Nozzle|Barb|HoseClamp/.test(o.id))return partColors.bulkhead;
  if(o.id==='MainPump'||o.id==='PumpSoftLink')return o.color;
  return routeColors[o.route]||o.color;
}

// The CAD keeps each pipe run intact. Display its curved elbow faces in a
// second material, using the same centerlines and radii as the CAD sweep.
export function fittingMaterialGroups(o,paths) {
  let classify;
  const positions=o.geometry.positions, indices=o.geometry.indices;
  if(/^(ReturnIsolation|ReturnFrontValve|ReturnRearValve)Body$/.test(o.id)) {
    let low=Infinity,high=-Infinity;
    for(let i=2;i<positions.length;i+=3){low=Math.min(low,positions[i]);high=Math.max(high,positions[i]);}
    classify=p=>p[2]<low+12.01||p[2]>high-12.01;
  } else if(o.id.startsWith('Pipe')&&o.kind!=='clear') {
    const key=['ReturnCommon','ReturnFront','ReturnRear','Emergency','Main'].find(k=>o.id.startsWith('Pipe'+k));
    const pts=paths?.[key];
    if(!pts)return null;
    const dot=(a,b)=>a.reduce((sum,x,i)=>sum+x*b[i],0),sub=(a,b)=>a.map((x,i)=>x-b[i]);
    const zones=[];
    for(let i=1;i<pts.length-1;i++) {
      let incoming=sub(pts[i],pts[i-1]),outgoing=sub(pts[i+1],pts[i]);
      const before=Math.hypot(...incoming),after=Math.hypot(...outgoing);
      incoming=incoming.map(x=>x/before);outgoing=outgoing.map(x=>x/after);
      const radius=Math.min(key==='Main'||key==='Emergency'?30:28,before*(i===1?.9:.45),after*(i===pts.length-2?.9:.45));
      const entry=pts[i].map((x,j)=>x-incoming[j]*radius),exit=pts[i].map((x,j)=>x+outgoing[j]*radius);
      const center=entry.map((x,j)=>x+outgoing[j]*radius),limit=radius+(key==='Main'||key==='Emergency'?12.5:10)+.1;
      zones.push({incoming,outgoing,entry,exit,center,limit});
    }
    classify=p=>zones.some(z=>dot(sub(p,z.entry),z.incoming)>=-.01&&dot(sub(p,z.exit),z.outgoing)<=.01&&Math.hypot(...sub(p,z.center))<=z.limit);
  } else return null;
  const plain=[],fittings=[];
  for(let i=0;i<indices.length;i+=3) {
    const point=[0,1,2].map(k=>(positions[indices[i]*3+k]+positions[indices[i+1]*3+k]+positions[indices[i+2]*3+k])/3);
    (classify(point)?fittings:plain).push(indices[i],indices[i+1],indices[i+2]);
  }
  return fittings.length?{plain,fittings,color:o.id.startsWith('Pipe')?partColors.elbow:partColors.union}:null;
}
const $ = id => document.getElementById(id);
const escapeHtml = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function validateScene(data) {
  if (!data || !Array.isArray(data.objects) || !Array.isArray(data.routes) || !data.routes.length) throw new Error('模型数据缺少零件或步骤');
  const ids = new Set();
  for (const o of data.objects) {
    if (!o.id || ids.has(o.id)) throw new Error('零件编号重复或缺失');
    ids.add(o.id);
    if (!o.geometry || !Array.isArray(o.geometry.positions) || o.geometry.positions.length % 3 || !Array.isArray(o.geometry.indices) || o.geometry.indices.length % 3) throw new Error('零件网格格式不完整');
    if (o.geometry.positions.some(n => !Number.isFinite(n)) || o.geometry.indices.some(n => !Number.isInteger(n) || n < 0 || n >= o.geometry.positions.length / 3)) throw new Error('零件网格坐标不完整');
  }
  const steps = new Set();
  for (const route of data.routes) {
    if (!route.id || !Array.isArray(route.steps) || !route.steps.length) throw new Error('管路缺少装配步骤');
    for (const step of route.steps) {
      if (!step.id || steps.has(step.id)) throw new Error('步骤编号重复或缺失');
      steps.add(step.id);
      for (const id of step.objectIds || []) if (!ids.has(id)) throw new Error(`步骤零件不存在：${id}`);
    }
  }
  return data;
}

export function objectVisibility(object, route, stepIndex, mode, allRoutes = false, selectedId = null, solo = false) {
  if (!object.route) return {visible:true, current:false, context:true};
  const asReference = () => ({visible:true, current:false, context:true, reference:true});
  if (solo) return object.id === 'MainPump' && object.id !== selectedId ? asReference() : {visible:object.id === selectedId, current:object.id === selectedId, context:false};
  if (allRoutes) return {visible:true, current:false, context:false};
  if (object.route !== route.id) return object.id === 'MainPump' ? asReference() : {visible:false, current:false, context:false};
  const index = route.steps.findIndex(s => s.id === object.stepId || (s.objectIds || []).includes(object.id));
  const current = index === stepIndex;
  const visible = mode === 'complete' || index < 0 || (mode === 'current' ? current : index <= stepIndex);
  return !visible && object.id === 'MainPump' ? asReference() : {visible, current, context:false};
}

async function startAssembly(){
  const state={routeIndex:0,stepIndex:0,allRoutes:true,selectedId:null,solo:false};
  let data,THREE,scene,camera,renderer,controls,observer,canvas,modelBounds,transition=null,dirty=true,raf,lastView='front';
  const meshes=[],labels=[],viewport=$('assembly-viewport'),reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const statusMessage=(text,retry=false)=>{const node=$('assembly-status');node.hidden=false;node.innerHTML=`<p>${escapeHtml(text)}</p>${retry?'<button type="button" id="assembly-retry">重新加载</button>':''}`;$('assembly-retry')?.addEventListener('click',()=>location.reload())};
  try{
    const response = await fetch(new URL('assembly-scene.json', import.meta.url), {cache:'no-cache'});
    if(!response.ok)throw Error(`模型暂未读取成功（${response.status}）`);
    data = validateScene(await response.json());
  }catch(e){statusMessage(e.message,true);$('assembly-progress-text').textContent='模型数据加载失败';return}
  const objectMap=new Map(data.objects.map(o=>[o.id,o])),route=()=>data.routes[state.routeIndex],step=()=>route().steps[state.stepIndex];
  const total=data.routes.reduce((n,r)=>n+r.steps.length,0);
  $('assembly-total').textContent=`${data.routes.length} 条管路 · ${total} 步`;
  $('assembly-revision').textContent=`${data.revision||'CAD装配模型'} · mm`;
  const noteLabels=['局部检漏','实物配色','接管顺序','胶接与固化','管夹定位','下水与检修','安装与备用','通水验收'];
  $('assembly-notes').innerHTML=(data.notes||[]).map((t,i)=>`<tr><td>${escapeHtml(noteLabels[i]||'安装事项')}</td><td>${escapeHtml(t)}</td></tr>`).join('');
  $('assembly-routes').innerHTML='<button type="button" data-route="all" aria-pressed="true">总装</button>'+data.routes.map((r,i)=>`<button type="button" data-route="${i}" aria-pressed="false">${escapeHtml(r.shortTitle||r.title)}</button>`).join('');
  const swatch=(color,title)=>`<span class="assembly-swatch" style="background:${color}"></span>${escapeHtml(title)}`;
  document.querySelector('.assembly-legend').innerHTML='<table class="prices"><thead><tr><th>类别</th><th>实物配色</th></tr></thead><tbody>'+data.routes.map(r=>`<tr><td>${escapeHtml(r.shortTitle||r.title)}直管</td><td>${swatch(routeColors[r.id],{main:'紫色',emergency:'浅紫色',return:'灰色'}[r.id]||'实物配色')}</td></tr>`).join('')+[['union','灰活接','深灰'],['unionClear','透明活接','透明'],['unionWhite','白活接','白色'],['elbow','弯头／三通','深灰'],['valve','阀体','近黑灰'],['handle','阀柄','红色'],['clear','透明管','透明，显示时加深轮廓']].map(([key,title,text])=>`<tr><td>${escapeHtml(title)}</td><td>${swatch(partColors[key],text)}</td></tr>`).join('')+'</tbody></table>';
  const clearOrder=['ClearMainUpper','PipeMainTail','ClearEmergencyUpper','PipeEmergencyTail','ClearCommon','ClearFront','ClearRear'];
  const clearObjects=data.objects.filter(o=>o.kind==='clear').sort((a,b)=>clearOrder.indexOf(a.id)-clearOrder.indexOf(b.id));
  $('assembly-clear-parts').innerHTML='<table class="prices"><thead><tr><th>位置</th><th>编号</th><th>查看</th></tr></thead><tbody>'+clearObjects.map(o=>`<tr><td>${escapeHtml(o.label)}</td><td><code>${escapeHtml(o.procurementId||o.id)}</code></td><td><button type="button" data-object="${escapeHtml(o.id)}">查看位置 ↑</button></td></tr>`).join('')+'</tbody></table>';
  function stepObjects(s){const ids=new Set([...(s.objectIds||[]),...data.objects.filter(o=>o.stepId===s.id&&o.route===route().id).map(o=>o.id)]);return [...ids].map(id=>objectMap.get(id)).filter(Boolean)}
  function clearSelection(){state.selectedId=null;state.solo=false}
  const behavior=()=>reduced.matches?'instant':'smooth';
  function showStage(){const r=viewport.getBoundingClientRect();if(r.bottom<120||r.top>innerHeight-120)document.querySelector('.assembly-work').scrollIntoView({behavior:behavior(),block:'start'})}
  function showStep(){const t=$('assembly-top'),r=t.getBoundingClientRect(),stage=document.querySelector('.assembly-stage').getBoundingClientRect(),top=matchMedia('(max-width:734px)').matches?stage.bottom:48;if(r.top<top||r.top>innerHeight*.55)t.scrollIntoView({behavior:behavior(),block:'start'})}
  function setRoute(index){state.allRoutes=false;state.routeIndex=index;state.stepIndex=0;clearSelection();renderUi();updateModel();focusStep(true);showStep()}
  function setStep(index){state.allRoutes=false;state.stepIndex=Math.max(0,Math.min(index,route().steps.length-1));clearSelection();renderUi();updateModel();focusStep(true);showStep()}
  function selectObject(id){if(!objectMap.has(id))return;state.selectedId=id;state.solo=false;renderSelection();updateModel();focusStep(true)}
  function renderUi(){
    const r=route(),s=step();document.querySelector('.assembly-guide').dataset.overview=String(state.allRoutes);
    document.querySelectorAll('[data-route]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.route==='all'?state.allRoutes:!state.allRoutes&&Number(b.dataset.route)===state.routeIndex)));
    $('assembly-progress-text').textContent=state.allRoutes?'总装':`${r.shortTitle||r.title} · ${String(state.stepIndex+1).padStart(2,'0')} / ${String(r.steps.length).padStart(2,'0')}`;
    $('assembly-progress-bar').style.width=state.allRoutes?'0':`${100*(state.stepIndex+1)/r.steps.length}%`;
    document.querySelector('.assembly-stepnav').hidden=state.allRoutes;document.querySelector('.assembly-stepdetails').hidden=state.allRoutes;
    $('assembly-prev').disabled=state.allRoutes||state.stepIndex===0;$('assembly-next').disabled=state.allRoutes||state.stepIndex===r.steps.length-1;
    $('assembly-step-count').textContent=`${r.steps.length} 步`;
    if(state.allRoutes){
      $('assembly-instruction').innerHTML='<h2 class="assembly-title">接管顺序</h2><p class="assembly-step-description">先固定管夹，再无胶试拼。位置确认后，分组件胶接。</p><div class="assembly-overview">'+data.routes.map((r,i)=>`<button type="button" data-route-go="${i}"><b>${escapeHtml(r.shortTitle||r.title)}</b><span>${escapeHtml((r.title||'').split('：')[1]||'')}</span><i>${r.steps.length} 步 ›</i></button>`).join('')+'</div>';
    }else{
      const parts=s.parts||[],objects=stepObjects(s);
      $('assembly-instruction').innerHTML=`<h2 class="assembly-title">${escapeHtml(s.title)}</h2><p class="assembly-step-description">${escapeHtml(s.description)}</p>${parts.length?'<h3 class="assembly-sublabel">本步零件</h3><table class="prices assembly-parts-table"><thead><tr><th>零件</th><th>采购编号</th><th>数量</th></tr></thead><tbody>'+parts.map(p=>`<tr><td>${escapeHtml(p.name)}</td><td><code>${escapeHtml(p.id)}</code></td><td>${escapeHtml(p.qty)}${escapeHtml(p.unit)}</td></tr>`).join('')+'</tbody></table>':''}${s.checks?.length?'<h3 class="assembly-sublabel">装好后检查</h3><ul class="assembly-checks">'+s.checks.map(c=>`<li>${escapeHtml(c)}</li>`).join('')+'</ul>':''}${objects.length?'<details class="assembly-objectdetails"><summary>辨认本步零件 · '+objects.length+'</summary><div class="assembly-objectbuttons">'+objects.map((o,i)=>`<button type="button" data-object="${escapeHtml(o.id)}" aria-pressed="false"><b>${i+1}</b>${escapeHtml(o.label)}</button>`).join('')+'</div></details>':''}`;
    }
    $('assembly-steps').innerHTML=r.steps.map((s,i)=>`<li><button type="button" data-step="${i}"${i===state.stepIndex?' aria-current="step"':''}><b>${String(i+1).padStart(2,'0')}</b><span>${escapeHtml(s.title)}</span></button></li>`).join('');renderSelection();
  }
  function renderSelection(){
    const o=objectMap.get(state.selectedId),panel=$('assembly-part');document.querySelectorAll('[data-object]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.object===state.selectedId)));
    if(!o){panel.hidden=true;panel.replaceChildren();return}panel.hidden=false;
    const r=data.routes.find(r=>r.id===o.route),s=r?.steps.find(s=>s.id===o.stepId||s.objectIds?.includes(o.id));
    const meta=[o.procurementId,r?.shortTitle,s?`第${r.steps.indexOf(s)+1}步`:null].filter(Boolean).join(' · ');
    panel.innerHTML=`<button type="button" id="assembly-clear" aria-label="关闭零件说明">×</button><h3>${escapeHtml(o.label)}</h3><p>${escapeHtml(o.description||s?.description||'模型位置参照；安装按实物核对。')}</p><p class="assembly-part-meta">${escapeHtml(meta)}</p>${o.evidence?`<details><summary>尺寸与来源</summary><p>${escapeHtml(o.evidence)}</p></details>`:''}${o.route?`<button type="button" id="assembly-solo">${state.solo?'返回管路视图':'单独查看这个零件'}</button>`:''}${s?'<button type="button" id="assembly-jump" class="assembly-part-jump">回到这一步</button>':''}`;
    $('assembly-clear').addEventListener('click',()=>{clearSelection();renderSelection();updateModel();if(state.allRoutes)setView(lastView,true);else focusStep(true)});
    $('assembly-solo')?.addEventListener('click',()=>{state.solo=!state.solo;renderSelection();updateModel();focusStep(true)});
    $('assembly-jump')?.addEventListener('click',()=>{state.routeIndex=data.routes.indexOf(r);state.stepIndex=r.steps.indexOf(s);state.allRoutes=false;clearSelection();renderUi();updateModel();focusStep(true)});
  }
  $('assembly-routes').addEventListener('click',e=>{const b=e.target.closest('[data-route]');if(!b)return;if(b.dataset.route==='all'){state.allRoutes=true;clearSelection();renderUi();updateModel();setView('front',true);showStep()}else setRoute(Number(b.dataset.route))});
  $('assembly-instruction').addEventListener('click',e=>{const b=e.target.closest('[data-route-go]');if(b)setRoute(Number(b.dataset.routeGo))});
  document.querySelector('.assembly-page').addEventListener('click',e=>{const b=e.target.closest('[data-object]');if(b){selectObject(b.dataset.object);showStage()}});
  $('assembly-steps').addEventListener('click',e=>{const b=e.target.closest('[data-step]');if(b)setStep(Number(b.dataset.step))});
  $('assembly-prev').addEventListener('click',()=>setStep(state.stepIndex-1));$('assembly-next').addEventListener('click',()=>setStep(state.stepIndex+1));
  document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>setView(b.dataset.view,true)));
  renderUi();
  try{
    THREE=await import('./vendor/three/three.module.js');const {OrbitControls}=await import('./vendor/three/OrbitControls.js');
    renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'low-power'});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setClearColor(0xf5f5f7);renderer.outputColorSpace=THREE.SRGBColorSpace;
    canvas=renderer.domElement;canvas.setAttribute('role','img');canvas.setAttribute('aria-label','可旋转缩放、点选零件的管路3D模型');viewport.prepend(canvas);
    canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();statusMessage('3D显示暂时中断，重新加载可恢复模型。',true)});
    scene=new THREE.Scene();camera=new THREE.OrthographicCamera(-600,600,800,-800,1,14000);camera.up.set(0,0,1);
    scene.add(new THREE.AmbientLight(0xffffff,1.5));for(const [x,y,z,intensity] of [[-700,-1100,2200,2.3],[1300,600,1400,1.2]]){const light=new THREE.DirectionalLight(0xffffff,intensity);light.position.set(x,y,z);scene.add(light)}
    const root=new THREE.Group();scene.add(root);
    for(const object of data.objects){
      const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(object.geometry.positions,3));geometry.setIndex(object.geometry.indices);geometry.computeVertexNormals();geometry.computeBoundingSphere();
      const context=!object.route,opacity=context?Math.min(object.opacity??.4,/Glass|Sump/i.test(object.group)?.035:/Equipment/i.test(object.group)?.3:['UpperBoard','UpperMat'].includes(object.id)?.08:.9):(object.kind==='clear'||object.finish==='clear'?.94:1);
      const groups=fittingMaterialGroups(object,data.pipeCenterlinesMM),colors=[componentColor(object)||'#788485'];
      if(groups){geometry.setIndex([...groups.plain,...groups.fittings]);geometry.clearGroups();if(groups.plain.length)geometry.addGroup(0,groups.plain.length,0);geometry.addGroup(groups.plain.length,groups.fittings.length,1);colors.push(groups.color)}
      const materials=colors.map(color=>new THREE.MeshStandardMaterial({color,roughness:.64,metalness:.04,side:THREE.DoubleSide,transparent:opacity<1,opacity,depthWrite:opacity>.8}));
      const mesh=new THREE.Mesh(geometry,materials.length===1?materials[0]:materials);mesh.userData={object,baseStyles:materials.map(material=>({material,color:material.color.clone(),opacity}))};root.add(mesh);meshes.push(mesh);
      if(object.route||/Glass|Sump|Frame/i.test(object.group)){const lineColor=object.route?(object.kind==='clear'?0x82b9c5:0x879399):0x91a1ac;const edge=new THREE.LineSegments(new THREE.EdgesGeometry(geometry,object.route?42:36),new THREE.LineBasicMaterial({color:lineColor,transparent:true,opacity:object.route?.4:.35,depthWrite:false}));edge.userData.baseColor=edge.material.color.clone();edge.userData.baseOpacity=edge.material.opacity;mesh.add(edge)}
    }
    modelBounds=new THREE.Box3().setFromObject(root);controls=new OrbitControls(camera,canvas);controls.enableDamping=true;controls.dampingFactor=.09;controls.screenSpacePanning=true;controls.minZoom=.2;controls.maxZoom=18;
    controls.mouseButtons={LEFT:THREE.MOUSE.ROTATE,MIDDLE:THREE.MOUSE.DOLLY,RIGHT:THREE.MOUSE.PAN};controls.touches={ONE:THREE.TOUCH.ROTATE,TWO:THREE.TOUCH.DOLLY_PAN};
    controls.addEventListener('start',()=>{transition=null;viewport.dataset.transitioning='false';dirty=true});controls.addEventListener('change',()=>dirty=true);
    let down;const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();canvas.addEventListener('pointerdown',e=>down={x:e.clientX,y:e.clientY});canvas.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down.x,e.clientY-down.y)>6)return;const b=canvas.getBoundingClientRect();pointer.set((e.clientX-b.left)/b.width*2-1,-(e.clientY-b.top)/b.height*2+1);raycaster.setFromCamera(pointer,camera);const hits=raycaster.intersectObjects(meshes.filter(m=>m.visible&&m.userData.object.route),false);if(hits.length)selectObject(hits[0].object.userData.object.id)});
    observer=new ResizeObserver(()=>{resize();if(state.allRoutes&&!state.selectedId)setView(lastView,false);else focusStep(false,lastView)});observer.observe(viewport);
    setView('front',false);updateModel();$('assembly-status').hidden=true;
    const draw=time=>{raf=requestAnimationFrame(draw);if(document.hidden)return;let moved=false;if(transition){const t=Math.min(1,(time-transition.start)/transition.duration),ease=t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;camera.position.lerpVectors(transition.position,transition.endPosition,ease);controls.target.lerpVectors(transition.target,transition.endTarget,ease);camera.up.lerpVectors(transition.up,transition.endUp,ease).normalize();camera.userData.baseHeight=THREE.MathUtils.lerp(transition.height,transition.endHeight,ease);camera.zoom=1;camera.lookAt(controls.target);resize();dirty=true;if(t===1){transition=null;viewport.dataset.transitioning='false';controls.update()}}else moved=controls.update();if(dirty||moved){updateLabels();renderer.render(scene,camera);dirty=false}};raf=requestAnimationFrame(draw);
    window.addEventListener('pagehide',()=>{cancelAnimationFrame(raf);observer.disconnect();controls.dispose();renderer.dispose()},{once:true});
  }catch(e){console.warn('CAD viewer unavailable',e);statusMessage('当前浏览器无法显示3D，请换用支持WebGL的浏览器；下方步骤仍可查看。',true);document.querySelectorAll('[data-view]').forEach(b=>b.disabled=true)}
  function resize(){if(!camera||!renderer)return;const b=viewport.getBoundingClientRect(),renderHeight=b.height-54,h=camera.userData.baseHeight||1800,aspect=b.width/renderHeight;camera.left=-h*aspect/2;camera.right=h*aspect/2;camera.top=h/2;camera.bottom=-h/2;camera.updateProjectionMatrix();if(canvas.width!==Math.floor(b.width*renderer.getPixelRatio())||canvas.height!==Math.floor(renderHeight*renderer.getPixelRatio()))renderer.setSize(b.width,renderHeight,false);dirty=true}
  function currentMeshes(){if(state.selectedId)return meshes.filter(m=>m.userData.object.id===state.selectedId);const ids=new Set(stepObjects(step()).map(o=>o.id));return meshes.filter(m=>ids.has(m.userData.object.id))}
  function frame(bounds,view,smooth){
    if(!camera||!controls)return;lastView=view;document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
    const center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3()),rect=viewport.getBoundingClientRect(),aspect=rect.width/(rect.height-54),up=view==='top'?new THREE.Vector3(0,1,0):new THREE.Vector3(0,0,1),direction=view==='top'?new THREE.Vector3(0,0,1):view==='right'?new THREE.Vector3(1,0,0):new THREE.Vector3(0,-1,0);
    const h=Math.max(view==='top'?size.y:size.z,(view==='right'?size.y:size.x)/aspect,state.allRoutes&&!state.selectedId?0:460)*(state.allRoutes&&!state.selectedId?1.06:1.6),endPosition=center.clone().addScaledVector(direction,3800);
    controls.enableDamping=false;controls.update();controls.enableDamping=true;
    if(smooth&&!reduced.matches){transition={start:performance.now(),duration:780,position:camera.position.clone(),target:controls.target.clone(),up:camera.up.clone(),height:camera.userData.baseHeight||h,endPosition,endTarget:center,endUp:up,endHeight:h};viewport.dataset.transitioning='true'}else{transition=null;camera.position.copy(endPosition);controls.target.copy(center);camera.up.copy(up);camera.userData.baseHeight=h;camera.zoom=1;camera.lookAt(center);resize();controls.update();viewport.dataset.transitioning='false'}dirty=true;
  }
  function setView(view,smooth){if(!modelBounds)return;if(state.allRoutes&&!state.selectedId)frame(modelBounds,view,smooth);else focusStep(smooth,view)}
  function focusStep(smooth=true,view){if(!THREE||!modelBounds)return;const targets=currentMeshes();if(!targets.length){frame(modelBounds,view||'front',smooth);return}const bounds=new THREE.Box3();targets.forEach(m=>bounds.expandByObject(m));const size=bounds.getSize(new THREE.Vector3());frame(bounds,view||(size.y>size.x*1.3?'right':'front'),smooth)}
  function updateModel(){
    if(!scene)return;const ids=new Set(state.allRoutes?[]:stepObjects(step()).map(o=>o.id));
    for(const mesh of meshes){const o=mesh.userData.object,selected=o.id===state.selectedId,current=state.selectedId?selected:ids.has(o.id),focus=state.selectedId||!state.allRoutes;mesh.visible=!state.solo||!o.route||selected;
      for(const base of mesh.userData.baseStyles){const material=base.material;material.color.copy(base.color);material.emissive.setHex(0);material.opacity=base.opacity;if(focus){material.opacity=current?1:Math.min(base.opacity,o.route?.3:.16);if(!current&&o.route)material.color.setHex(0xc4c9ce);if(selected){material.color.setHex(0x0066cc)}}material.transparent=material.opacity<1;material.depthWrite=material.opacity>.8;material.needsUpdate=true}
      mesh.children.forEach(edge=>{edge.material.color.copy(edge.userData.baseColor);edge.material.opacity=focus?(current?.9:.18):edge.userData.baseOpacity;if(current)edge.material.color.setHex(0x0066cc)})
    }
    rebuildLabels();dirty=true;
  }
  function rebuildLabels(){
    labels.length=0;$('assembly-labels').replaceChildren();if(state.allRoutes&&!state.selectedId)return;const numbered=state.allRoutes?[objectMap.get(state.selectedId)]:stepObjects(step());
    numbered.filter(Boolean).forEach((o,i)=>{const mesh=meshes.find(m=>m.userData.object.id===o.id);if(!mesh?.visible)return;const el=document.createElement('span');el.className='assembly-marker'+(o.id===state.selectedId?' selected':'');el.textContent=String(i+1);el.addEventListener('pointerdown',e=>{e.stopPropagation();selectObject(o.id)});$('assembly-labels').append(el);const bounds=new THREE.Box3().setFromObject(mesh),position=bounds.getCenter(new THREE.Vector3());if(o.id.startsWith('Pipe')){const vertices=mesh.geometry.getAttribute('position'),p=new THREE.Vector3(),nearest=new THREE.Vector3();let distance=Infinity;for(let j=0;j<vertices.count;j++){p.fromBufferAttribute(vertices,j);const d=p.distanceToSquared(position);if(d<distance){distance=d;nearest.copy(p)}}position.copy(nearest)}labels.push({el,position})});
  }
  function updateLabels(){const b=viewport.getBoundingClientRect(),occupied=[];for(const label of labels){const p=label.position.clone().project(camera);let x=(p.x*.5+.5)*b.width,y=(-p.y*.5+.5)*(b.height-54);const hidden=p.z < -1||p.z>1||x<16||y<16||x>b.width-16||y>b.height-70;label.el.hidden=hidden;if(hidden)continue;const offsets=[[0,0],[30,0],[-30,0],[0,-30],[0,30],[30,-30],[-30,-30],[30,30],[-30,30]];const spot=offsets.map(([dx,dy])=>({x:x+dx,y:y+dy})).find(p=>p.x>16&&p.y>16&&p.x<b.width-16&&p.y<b.height-70&&occupied.every(q=>Math.hypot(p.x-q.x,p.y-q.y)>=28));if(spot){x=spot.x;y=spot.y}occupied.push({x,y});label.el.style.left=`${x}px`;label.el.style.top=`${y}px`}}
}
if(typeof document!=='undefined'&&document.getElementById('assembly-viewport'))startAssembly();
