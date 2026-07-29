/* Dropdown do menu PROJETOS — mostra todos os projetos e as edições ao passar o cursor.
   Auto-contido: injeta o próprio CSS e lê /projetos.json. Funciona em PT e EN. */
(function(){
  var EN = location.pathname.indexOf('/en/') === 0;
  var proj = EN ? '/en/project.html?id=' : '/projeto.html?id=';

  // CSS
  var css = document.createElement('style');
  css.textContent =
   '.projdd{position:relative;display:inline-block}'+
   '.projdd .pp{position:absolute;top:100%;left:50%;transform:translateX(-50%) translateY(8px);'+
     'background:#fff;border:1px solid var(--line,#d6e0e4);border-radius:14px;box-shadow:0 18px 44px rgba(10,37,64,.18);'+
     'padding:.6rem;min-width:290px;opacity:0;visibility:hidden;transition:opacity .18s,transform .18s;z-index:60}'+
   '.projdd:hover .pp{opacity:1;visibility:visible;transform:translateX(-50%) translateY(2px)}'+
   '.projdd .pp::before{content:"";position:absolute;top:-14px;left:0;right:0;height:14px}'+
   '.projdd .pp a{display:block;padding:.5rem .7rem;border-radius:9px;text-decoration:none;color:var(--navy,#0a2540);'+
     "font-family:'Barlow Condensed',sans-serif;font-weight:600;text-transform:uppercase;letter-spacing:.03em;font-size:.95rem;white-space:nowrap;transition:background .15s}"+
   '.projdd .pp a:hover{background:var(--sand,#e9eff1);color:var(--teal-d,#00727e)}'+
   '.projdd .pp .sub{padding-left:.9rem;border-left:2px solid var(--teal,#00a3b4);margin:.15rem 0 .3rem .8rem}'+
   '.projdd .pp .sub a{font-size:.86rem;color:var(--muted,#5b6f7a)}'+
   '.projdd .pp .sub a::before{content:"› ";color:var(--teal,#00a3b4)}'+
   '.projdd .pp .todos{border-top:1px solid var(--line,#d6e0e4);margin-top:.3rem;padding-top:.4rem;color:var(--teal-d,#00727e)}'+
   '@media(max-width:820px){.projdd .pp{display:none !important}}';
  document.head.appendChild(css);

  // acha o link "Projetos" no menu do topo (não no rodapé)
  var nav = document.querySelector('.nav') || document;
  var link = null;
  nav.querySelectorAll('a').forEach(function(a){
    var h=(a.getAttribute('href')||'');
    if(!link && /(projetos|projects)\.html$/.test(h)) link=a;
  });
  if(!link) return;

  fetch('/projetos.json').then(function(r){return r.json();}).then(function(d){
    var todos=d.projetos||[];
    var pais=todos.filter(function(p){return !p.parent;});
    var wrap=document.createElement('span'); wrap.className='projdd';
    link.parentNode.insertBefore(wrap,link); wrap.appendChild(link);
    var pp=document.createElement('div'); pp.className='pp';
    pais.forEach(function(p){
      var nome = (EN && p.nome_en) ? p.nome_en : p.nome;
      var a=document.createElement('a'); a.href=proj+p.id; a.textContent=nome; pp.appendChild(a);
      var filhos=todos.filter(function(x){return x.parent===p.id;}).sort(function(x,y){return (x.ordem||0)-(y.ordem||0);});
      if(filhos.length){
        var sub=document.createElement('div'); sub.className='sub';
        filhos.forEach(function(f){
          var fn=(EN && f.nome_en)?f.nome_en:f.nome;
          var fa=document.createElement('a'); fa.href=proj+f.id; fa.textContent=fn; sub.appendChild(fa);
        });
        pp.appendChild(sub);
      }
    });
    var todosLink=document.createElement('a'); todosLink.className='todos';
    todosLink.href=EN?'/en/projects.html':'/projetos.html';
    todosLink.textContent=EN?'See all projects →':'Ver todos os projetos →';
    pp.appendChild(todosLink);
    wrap.appendChild(pp);
  }).catch(function(){});
})();
