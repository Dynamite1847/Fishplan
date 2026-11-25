/* Shared navigation, dialogs and reading navigation. */
(()=>{
 let previousFocus=null;
 function openDialog(id){const d=document.getElementById(id);if(!d||d.open)return;previousFocus=document.activeElement;d.showModal();}
 function closeDialog(d){if(!d)return;d.close();if(previousFocus?.isConnected)previousFocus.focus();}
 window.SiteUI={openDialog,closeDialog,toast(message){let el=document.getElementById('site-toast');if(!el){el=document.createElement('div');el.id='site-toast';el.className='toast';el.setAttribute('role','status');document.body.append(el)}el.textContent=message;clearTimeout(window.siteToastTimer);window.siteToastTimer=setTimeout(()=>el.remove(),3200)}};
 document.addEventListener('click',e=>{const open=e.target.closest('[data-dialog-open]');if(open)openDialog(open.dataset.dialogOpen);const close=e.target.closest('[data-dialog-close]');if(close)closeDialog(close.closest('dialog'));});
 document.querySelectorAll('dialog').forEach(d=>{d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeDialog(d)}});d.addEventListener('cancel',()=>{if(previousFocus?.isConnected)previousFocus.focus()})});
 const article=document.querySelector('.doc-layout .prose');const side=document.querySelector('.doc-layout .side');
 if(article){
  const headings=[...article.querySelectorAll('h2,h3')];
  headings.forEach((h,i)=>{if(!h.id)h.id='section-'+(i+1)});
  if(side&&headings.length){const nav=document.createElement('div');nav.className='article-toc';nav.innerHTML='<p class="lab" style="margin-top:26px">本页目录</p>';headings.forEach(h=>{const a=document.createElement('a');a.href='#'+h.id;a.textContent=h.textContent;nav.append(a)});side.append(nav)}
  if(side){const mobile=document.createElement('details');mobile.className='toc-mobile';const summary=document.createElement('summary');summary.textContent='栏目与本页目录';mobile.append(summary);const nav=document.createElement('nav');nav.setAttribute('aria-label','手机阅读目录');side.querySelectorAll('a').forEach(a=>nav.append(a.cloneNode(true)));mobile.append(nav);article.before(mobile);mobile.addEventListener('click',e=>{if(e.target.closest('a'))mobile.open=false})}
 }
 document.querySelectorAll('.prose table').forEach(t=>{if(!t.parentElement.classList.contains('tw')){const w=document.createElement('div');w.className='tw';t.before(w);w.append(t)}if(t.querySelector('tr')?.children.length>2){t.classList.add('wide-table');t.parentElement.classList.add('scroll-table')}});
})();
