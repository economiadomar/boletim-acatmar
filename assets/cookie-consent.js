/* ACATMAR — Aviso de cookies / LGPD (leve, sem serviço externo) */
(function(){
  var KEY='acatmar_cookie_consent';
  try{ if(localStorage.getItem(KEY)) return; }catch(e){ return; }

  var EN = false;
  try{ EN = (localStorage.getItem('acatmar_lang')==='en'); }catch(e){}

  var T = EN ? {
    text:'We use only essential storage to keep your language preference and make the site work. We do not use tracking or advertising cookies.',
    more:'Cookie Policy', accept:'Got it', reject:'Essentials only'
  } : {
    text:'Usamos apenas armazenamento essencial para lembrar seu idioma e fazer o site funcionar. Não usamos cookies de rastreamento ou publicidade.',
    more:'Política de Cookies', accept:'Entendi', reject:'Somente essenciais'
  };

  var css = ''
   + '.acmk{position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#0a2540;color:#e6eef4;'
   + 'border-top:2px solid #00a3b4;box-shadow:0 -8px 30px rgba(0,0,0,.35);'
   + "font-family:'Barlow Condensed',system-ui,Arial,sans-serif;font-size:1rem;line-height:1.45;"
   + 'transform:translateY(110%);transition:transform .4s ease}'
   + '.acmk.in{transform:translateY(0)}'
   + '.acmk .wr{max-width:1160px;margin:0 auto;padding:1rem 1.3rem;display:flex;gap:1rem 1.4rem;align-items:center;flex-wrap:wrap;justify-content:space-between}'
   + '.acmk p{margin:0;max-width:760px;color:#cfe0ea}'
   + '.acmk a.more{color:#35c9da;text-decoration:underline;white-space:nowrap}'
   + '.acmk .btns{display:flex;gap:.6rem;flex-wrap:wrap}'
   + '.acmk button{font-family:inherit;font-weight:700;text-transform:uppercase;letter-spacing:.05em;font-size:.9rem;'
   + 'padding:.6rem 1.2rem;border-radius:999px;cursor:pointer;border:1.5px solid transparent}'
   + '.acmk .ok{background:#00a3b4;color:#fff}.acmk .ok:hover{background:#35c9da;color:#06263c}'
   + '.acmk .no{background:transparent;color:#cfe0ea;border-color:rgba(255,255,255,.35)}.acmk .no:hover{background:rgba(255,255,255,.1);color:#fff}';

  var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);

  var bar=document.createElement('div'); bar.className='acmk'; bar.setAttribute('role','dialog'); bar.setAttribute('aria-label','Aviso de cookies');
  bar.innerHTML='<div class="wr">'
    + '<p>'+T.text+' <a class="more" href="cookies.html">'+T.more+'</a></p>'
    + '<div class="btns">'
    + '<button type="button" class="no">'+T.reject+'</button>'
    + '<button type="button" class="ok">'+T.accept+'</button>'
    + '</div></div>';
  document.body.appendChild(bar);
  requestAnimationFrame(function(){ setTimeout(function(){ bar.classList.add('in'); },120); });

  function close(v){ try{ localStorage.setItem(KEY,v); }catch(e){} bar.classList.remove('in'); setTimeout(function(){ bar.remove(); },400); }
  bar.querySelector('.ok').addEventListener('click',function(){ close('accepted'); });
  bar.querySelector('.no').addEventListener('click',function(){ close('essential'); });
})();
