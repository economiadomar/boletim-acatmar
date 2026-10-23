/* App do VI Fórum ACATMAR — PWA sem framework. Conteúdo vem de data/forum.json */
(function(){
'use strict';
var APP_V=85;
var D=null, view=document.getElementById('view');
var LS={get:function(k,d){try{var v=localStorage.getItem('forum_'+k);return v==null?d:JSON.parse(v);}catch(e){return d;}},set:function(k,v){try{localStorage.setItem('forum_'+k,JSON.stringify(v));}catch(e){}}};
var API='https://acatmar-app.programamundomar.workers.dev';
function plataforma(){var u=navigator.userAgent;if(/iPad/.test(u))return 'iPad';if(/iPhone/.test(u))return 'iPhone';if(/Android/.test(u))return 'Android';if(/Macintosh/.test(u))return 'Mac';if(/Windows/.test(u))return 'Windows';return 'Outro';}
function devId(){var id=LS.get('dev_id',null);if(!id){id='d'+Date.now().toString(36)+Math.random().toString(36).slice(2,8);LS.set('dev_id',id);}return id;}
function pingUso(forcar,extra){try{var agora=Date.now();if(!forcar&&agora-(LS.get('reg_t',0)||0)<43200000)return;var me=LS.get('me',null)||{};var b={id:devId(),plataforma:plataforma(),instalado:isStandalone()||LS.get('instalado',false),nome:me.nome||'',empresa:me.empresa||'',cargo:me.cargo||'',email:me.email||'',fone:me.fone||'',tipo:me.tipo||''};if(extra)for(var k in extra)b[k]=extra[k];LS.set('reg_t',agora);fetch(API+'/registro',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b),keepalive:true}).catch(function(){});}catch(e){}}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function h(html){if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();view.innerHTML=html;view.scrollTop=0;window.scrollTo(0,0);}
function toast(m){var t=document.getElementById('toast');t.textContent=m;t.hidden=false;clearTimeout(toast._t);toast._t=setTimeout(function(){t.hidden=true;},2600);}
function fmtData(iso){var p=iso.split('-');var m=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];return p[2]+' '+m[+p[1]-1]+' '+p[0];}
function eventDate(){var e=D.evento;return {start:new Date(e.data_iso+'T'+e.inicio+':00-03:00'),end:new Date(e.data_iso+'T'+e.fim+':00-03:00')};}
function status(){var n=new Date(),d=eventDate();if(n<d.start)return 'antes';if(n>d.end)return 'depois';return 'agora';}
function nowHM(){var n=new Date();return n.getHours()*60+n.getMinutes();}
function hm(s){var p=s.split(':');return +p[0]*60+(+p[1]);}

/* ---------- carregamento ---------- */
function load(){
  var cached=LS.get('data',null);
  if(cached){D=cached;boot();}
  fetch('data/forum.json?t='+Date.now(),{cache:'no-store'}).then(function(r){return r.json();}).then(function(j){
    var changed=!D||D.versao!==j.versao;D=j;LS.set('data',j);
    if(!cached)boot();else if(changed){checkUpdate();render();toast('Conteúdo atualizado');}
    updateBadge();
  }).catch(function(){ if(!D){h('<div class="card"><h3>Sem conexão</h3><p>Abra o app com internet uma vez para baixar o conteúdo do Fórum.</p></div>');} });
}
var booted=false;
function forcarAtualizacao(){
  var p=('serviceWorker' in navigator)
    ? navigator.serviceWorker.getRegistrations().then(function(rs){
        return Promise.all(rs.map(function(r){return r.unregister().catch(function(){});}));
      })
    : Promise.resolve();
  return p.then(function(){
    return (window.caches&&caches.keys)
      ? caches.keys().then(function(ks){return Promise.all(ks.map(function(x){return caches.delete(x);}));})
      : null;
  }).catch(function(){}).then(function(){
    location.replace(location.pathname+'?v='+Date.now()+location.hash);
  });
}
function checkUpdate(){
  if(!(D&&D.app_min&&D.app_min>APP_V))return;
  var k='forum_reload_'+D.app_min;
  try{ if(sessionStorage.getItem(k))return; sessionStorage.setItem(k,'1'); }catch(e){}
  forcarAtualizacao();
}
/* o app instalado no iPhone volta suspenso, sem reiniciar: checa de novo ao voltar pra tela */
var ultimaChecagem=Date.now();
document.addEventListener('visibilitychange',function(){
  if(document.visibilityState!=='visible')return;
  if(Date.now()-ultimaChecagem<30000)return;
  ultimaChecagem=Date.now();
  fetch('data/forum.json?t='+Date.now(),{cache:'no-store'}).then(function(r){return r.json();}).then(function(j){
    if(j&&j.app_min&&j.app_min>APP_V){forcarAtualizacao();return;}
    if(j&&D&&j.versao!==D.versao){D=j;render();updateBadge();}
  }).catch(function(){});
});
function boot(){if(booted)return;booted=true;checkUpdate();render();updateBadge();setTimeout(installGate,150);setTimeout(function(){var s=document.getElementById('splash');s.classList.add('off');setTimeout(function(){s.remove();},400);},350);}

/* ---------- roteamento ---------- */
var routes={'/':home,'/programacao':programacao,'/palestrantes':palestrantes,'/avisos':avisos,'/aviso':aviso,'/credencial':credencial,'/patrocinadores':patrocinadores,'/local':local,'/interagir':interagir,'/certificado':certificado,'/instalar':instalar,'/sobre':sobre,'/mais':mais,'/anterior':anterior,'/faq':faq,'/credenciamento':credenciamento,'/edicoes':edicoes,'/inscricao':inscricao,'/controle':controle,'/diario':diario,'/posevento':posEvento,'/avaliacao':avaliacao,'/resultados':resultados};
var titles={'/programacao':'Programação','/palestrantes':'Palestrantes','/avisos':'Avisos','/aviso':'Aviso','/credencial':'Minha credencial','/patrocinadores':'Patrocinadores','/local':'Local e como chegar','/interagir':'Interagir','/certificado':'Certificado','/instalar':'Instalar o app','/sobre':'Sobre o Fórum','/mais':'Mais','/anterior':'V Fórum (2025)','/faq':'Perguntas frequentes','/credenciamento':'Credenciamento','/edicoes':'Edições anteriores','/inscricao':'Inscrição','/controle':'Controle do app','/diario':'Fórum todo dia','/posevento':'VI Fórum: como foi','/avaliacao':'Avaliação do Fórum','/resultados':'Resultados da avaliação'};
var tabsMain=['/','/programacao','/credencial','/avisos','/mais'];
function route(){var hsh=location.hash.replace(/^#/,'')||'/';var parts=hsh.split('/');var path='/'+(parts[1]||'');var arg=parts[2]||'';return {path:path,arg:arg};}
function render(){
  if(!D)return;var r=route();var fn=routes[r.path]||home;try{renderInner(r,fn);}catch(err){h('<div class="card"><h3>Ops</h3><p>Algo deu errado ao abrir esta tela. <a href="#/">Voltar ao início</a></p></div>');}
}
function renderInner(r,fn){
  document.getElementById('topbar-brand').hidden=r.path!=='/';
  var tt=document.getElementById('topbar-title');tt.hidden=r.path==='/';tt.textContent=titles[r.path]||'';
  document.getElementById('btn-back').hidden=tabsMain.indexOf(r.path)>=0;
  document.querySelectorAll('.tab').forEach(function(t){t.classList.toggle('on',t.getAttribute('data-tab')===r.path||(r.path==='/aviso'&&t.getAttribute('data-tab')==='/avisos'));});
  fn(r.arg);
}
window.addEventListener('hashchange',render);
document.getElementById('btn-back').addEventListener('click',function(){if(history.length>1)history.back();else location.hash='#/';});

/* ---------- Início ---------- */
var NUMED=['zero','Uma','Duas','Três','Quatro','Cinco','Seis','Sete','Oito','Nove','Dez','Onze','Doze'];
function numEdicoes(){var n=(D.edicoes||[]).length;return (NUMED[n]||n)+' ediç'+(n===1?'ão':'ões');}
function anosEdicoes(){var e=D.edicoes||[];return e.length?e[0].ano+' a '+e[e.length-1].ano:'';}
function home(){
  var e=D.evento,st=status();var d=eventDate();
  var cd='';
  if(st==='antes'){var diff=d.start-new Date();var dd=Math.floor(diff/864e5),hh=Math.floor(diff%864e5/36e5),mm=Math.floor(diff%36e5/6e4);
    cd='<div class="countdown"><div class="cd"><b>'+dd+'</b><span>dias</span></div><div class="cd"><b>'+hh+'</b><span>horas</span></div><div class="cd"><b>'+mm+'</b><span>min</span></div></div>';}
  else if(st==='agora')cd='<div class="live-pill"><i></i> Acontecendo agora</div>';
  else cd='<div class="tag" style="background:var(--teal);color:#fff;margin-top:12px">Edição realizada. Obrigado por participar!</div>';
  var unread=unreadAvisos();
  var av=D.avisos.slice(0,2).map(avisoCard).join('');
  var spons=D.patrocinadores.map(function(c,i){var modo={'Patrocínio':'inst','Realização':'real'}[c.cota]||'apoio';return '<div class="strip-cota strip-'+modo+'"><span>'+esc(c.cota)+'</span><div>'+c.empresas.map(function(p){var hb=({'Patrocínio':100,'Realização':56}[c.cota]||50);return '<a href="#/patrocinadores">'+(p.logo?'<img src="'+p.logo+'" alt="'+esc(p.nome)+'" style="height:'+Math.round(hb*(p.escala||1))+'px">':'<span class="logo-txt logo-txt-sm">'+esc(p.nome)+'</span>')+'</a>';}).join('')+'</div></div>';}).join('');
  var regBtn=st==='antes'?'<a class="btn btn-teal btn-block" href="#/inscricao">'+(LS.get('inscrito',null)?'✅ Inscrito · ver programação':'Inscrição gratuita')+'</a>':'';
  h('<section class="hero"><div class="hero-top"><img src="media/emblema-v2.jpg" alt="VI Fórum ACATMAR"><div><p class="kicker">'+esc(e.edicao)+' · '+esc(e.mote)+'</p><h1>'+esc(e.nome)+'</h1></div></div><div class="hero-in"><p>'+esc(e.data_texto)+' · '+esc(e.horario_texto)+'</p>'+cd+'</div></section>'
   +(st==='depois'?'<div class="quick"><a href="#/certificado"><i>📜</i>Certificado</a><a href="#/avaliacao"><i>⭐</i>Avaliar</a><a href="#/posevento"><i>📸</i>Como foi</a><a href="#/edicoes"><i>📷</i>Edições</a></div>':'<div class="quick"><a href="#/programacao"><i>🗓️</i>Programação</a><a href="#/local"><i>📍</i>Local</a><a href="#/credencial"><i>🎫</i>Credencial</a><a href="#/interagir"><i>💬</i>Interagir</a></div>')
   +(st==='depois'?retroHomeCard():diarioHomeCard(st,d))
   +(st==='depois'?'':'<section class="section"><div class="card"><div class="info"><div class="info-row"><div class="ic">📅</div><div><b>Quando</b><span>'+esc(e.data_texto)+'<br>'+esc(e.horario_texto)+'</span></div></div><div class="info-row"><div class="ic">📍</div><div><b>Onde</b><span>'+esc(e.local.nome)+(e.local.sala?' · '+esc(e.local.sala):'')+'<br><small class="muted">'+esc(e.local.endereco)+'</small></span></div></div><div class="info-row"><div class="ic">🅿️</div><div><b>Estacionamento</b><span>Próprio e gratuito no câmpus</span></div></div><div class="info-row"><div class="ic">🎟️</div><div><b>Participação</b><span>Gratuita, vagas limitadas'+(e.certificado?' · com certificado':'')+'</span></div></div></div>'+(regBtn?'<div class="btn-row">'+regBtn+'</div>':'')+'</div></section>')
   +'<section class="section"><div class="section-h"><h2>Avisos'+(unread?' <span class="tag red">'+unread+' novo'+(unread>1?'s':'')+'</span>':'')+'</h2><a href="#/avisos">Ver todos</a></div>'+av+'</section>'
   +'<section class="section"><div class="section-h"><h2>Sobre o Fórum</h2><a href="#/sobre">Mais</a></div><div class="card"><p>'+esc(D.sobre.resumo)+'</p><p class="small muted">'+esc(D.sobre.para_quem)+'</p></div></section>'
   +'<section class="section"><div class="section-h"><h2>'+numEdicoes()+' de história</h2><a href="#/edicoes">Ver fotos</a></div><div class="gal gal-ed">'+(D.edicoes||[]).map(function(e){return '<a href="#/edicoes"><img src="'+e.capa+'" alt="" loading="lazy"><span>'+e.ed+' Fórum · '+e.ano+'</span></a>';}).join('')+'</div></section>'
   +'<section class="section"><div class="section-h"><h2>Quem faz acontecer</h2><a href="#/patrocinadores">Ver</a></div><a href="#/patrocinadores"><img src="media/quem-faz-acontecer.jpg" alt="Quem faz o VI Fórum acontecer: patrocinadores e apoiadores" style="width:100%;border-radius:12px;display:block"></a></section>'
   +(st==='depois'?'':'<section class="section"><div class="card" style="background:var(--navy);color:#fff;border:0"><p class="kicker" style="color:var(--teal-b)">Dica</p><h3 style="color:#fff">Instale o app na tela inicial</h3><p class="small" style="opacity:.85">Assim ele abre em um toque, mostra sua credencial rápido no credenciamento e funciona mesmo sem sinal.</p><div class="btn-row"><a class="btn btn-light btn-sm" href="#/instalar">Como instalar</a></div></div></section>'));
  if(st==='antes'){clearInterval(home._t);home._t=setInterval(function(){if(route().path==='/')home();else clearInterval(home._t);},60000);}
}

/* ---------- Programação ---------- */
var periodoSel=LS.get('periodo','Manhã');var periodoManual=false;
function programacao(){
  var favs=LS.get('favs',[]);var st=status();var n=nowHM();
  var per=[];D.programacao.forEach(function(s){if(per.indexOf(s.periodo)<0)per.push(s.periodo);});
  if(per.indexOf(periodoSel)<0)periodoSel=per[0];
  if(st==='agora'&&!periodoManual){var cur=null;D.programacao.forEach(function(s){if(hm(s.hora)<=n)cur=s;});if(cur)periodoSel=cur.periodo;}
  var list=D.programacao.filter(function(s){return s.periodo===periodoSel;});
  var nowId=null;if(st==='agora'){for(var i=0;i<D.programacao.length;i++){var a=D.programacao[i],b=D.programacao[i+1];if(hm(a.hora)<=n&&(!b||hm(b.hora)>n))nowId=a.id;}}
  var byId={};(D.palestrantes||[]).forEach(function(p){byId[p.id]=p;});
  var items=list.map(function(s){var f=favs.indexOf(s.id)>=0;var cls='card sess '+(s.tipo||'')+(s.id===nowId?' now':'');var sp=s.palestrante?byId[s.palestrante]:null;
    var quem=sp&&sp.foto?'<a class="quem quem-foto" href="#/palestrantes"><img src="'+sp.foto+'" alt=""><span>'+esc(s.quem||sp.nome)+'</span></a>':'<div class="quem">'+esc(s.quem||'')+'</div>';
    return '<div class="'+cls+'"><div class="sess-h">'+esc(s.hora.replace(':','h'))+'</div><div class="sess-b"><h3>'+esc(s.titulo)+'</h3>'+quem+(s.desc?'<div class="desc">'+esc(s.desc)+'</div>':'')+(s.id===nowId?'<span class="tag red">Agora</span>':'')+(s.tipo==='bloco'||s.tipo==='palestra'?'<div class="btn-row"><a class="btn btn-outline btn-sm" href="#/interagir/'+encodeURIComponent(s.id)+'">Enviar pergunta</a></div>':'')+'</div>'+(s.tipo!=='pausa'?'<div class="sess-a"><button class="fav'+(f?' on':'')+'" data-fav="'+esc(s.id)+'" aria-label="Favoritar">★</button></div>':'')+'</div>';}).join('');
  var naGrade={};D.programacao.forEach(function(x){if(x.palestrante)naGrade[x.palestrante]=1;});
  var conf=(D.palestrantes||[]).filter(function(p){return p.tema&&!naGrade[p.id];});
  h((D.programacao_status==='preliminar'?'<div class="notice">⚠️ '+esc(D.programacao_aviso)+'</div>':'')
   +(conf.length&&D.programacao_status==='preliminar'?'<div class="section-h"><h2>Palestras confirmadas</h2><a href="#/palestrantes">Palestrantes</a></div>'+conf.map(function(p){return '<a class="card spk" href="#/palestrantes" style="text-decoration:none;color:inherit"><div class="av">'+(p.foto?'<img src="'+p.foto+'" alt="">':esc(p.nome[0]))+'</div><div><b>'+esc(p.tema)+'</b><span>'+esc(p.nome)+(p.empresa?' · '+esc(p.empresa):'')+' · '+esc(p.hora||'horário a confirmar')+'</span></div></a>';}).join('')+'<div class="section-h" style="margin-top:16px"><h2>Estrutura do dia</h2></div>':'')
   +'<div class="periodo">'+per.map(function(p){return '<button data-per="'+esc(p)+'" class="'+(p===periodoSel?'on':'')+'">'+esc(p)+'</button>';}).join('')+'</div>'
   +items
   +'<div class="btn-row"><button class="btn btn-navy btn-sm" id="btn-ics">Adicionar à minha agenda</button>'+(favs.length?'<span class="small muted" style="align-self:center">★ '+favs.length+' favorito'+(favs.length>1?'s':'')+'</span>':'')+'</div>'
   +'<section class="section" style="margin-top:22px"><div class="section-h"><h2>'+esc(D.edicao_anterior.titulo)+'</h2><a href="#/anterior">Ver</a></div><div class="card"><p class="small">'+esc(D.edicao_anterior.resumo)+'</p></div></section>');
  view.querySelectorAll('[data-per]').forEach(function(b){b.onclick=function(){periodoSel=b.getAttribute('data-per');periodoManual=true;LS.set('periodo',periodoSel);programacao();};});
  view.querySelectorAll('[data-fav]').forEach(function(b){b.onclick=function(){var id=b.getAttribute('data-fav');var fv=LS.get('favs',[]);var i=fv.indexOf(id);if(i>=0)fv.splice(i,1);else fv.push(id);LS.set('favs',fv);b.classList.toggle('on',i<0);toast(i<0?'Adicionado aos favoritos':'Removido dos favoritos');};});
  document.getElementById('btn-ics').onclick=downloadICS;
}
function downloadICS(){
  var e=D.evento;var ds=e.data_iso.replace(/-/g,'');var s=ds+'T'+e.inicio.replace(':','')+'00',f=ds+'T'+e.fim.replace(':','')+'00';
  var ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ACATMAR//Forum//PT','BEGIN:VEVENT','UID:vi-forum-2026@acatmar.org','DTSTAMP:'+s,'DTSTART;TZID=America/Sao_Paulo:'+s,'DTEND;TZID=America/Sao_Paulo:'+f,'SUMMARY:'+e.nome,'LOCATION:'+e.local.nome+' - '+e.local.endereco,'DESCRIPTION:'+D.sobre.resumo+' App: '+e.app_url,'URL:'+e.app_url,'END:VEVENT','END:VCALENDAR'].join('\r\n');
  var blob=new Blob([ics],{type:'text/calendar'});var u=URL.createObjectURL(blob);var a=document.createElement('a');a.href=u;a.download='vi-forum-acatmar.ics';document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(u);},2000);
}

/* ---------- Palestrantes ---------- */
function palestrantes(){
  var ps=D.palestrantes||[];
  var body=ps.length?'<p class="small muted" style="margin:0 0 12px">Palestrantes confirmados até agora. Novos nomes entram aqui e nos Avisos.</p>'+ps.map(function(p){return '<div class="card spk-card"><div class="spk"><div class="av av-lg">'+(p.foto?'<img src="'+p.foto+'" alt="">':esc((p.nome||'?').split(' ').map(function(w){return w[0];}).slice(0,2).join('')))+'</div><div><b>'+esc(p.nome)+'</b><span>'+esc([p.cargo,p.empresa].filter(Boolean).join(' · '))+'</span></div></div>'+(p.tema?'<div class="spk-tema"><p class="kicker">Palestra</p><h3>'+esc(p.tema)+'</h3>'+(p.hora?'<p class="small muted">'+esc(p.hora)+'</p>':'<p class="small muted">Horário a confirmar</p>')+'</div>':'')+(p.bio?'<p class="small">'+esc(p.bio)+'</p>':'')+'<div class="btn-row"><a class="btn btn-outline btn-sm" href="#/interagir">Enviar pergunta</a>'+(p.instagram?'<a class="btn btn-navy btn-sm" href="'+p.instagram+'" target="_blank" rel="noopener">Instagram</a>':'')+(p.redes||[]).map(function(r){return '<a class="btn btn-outline btn-sm" href="'+r.url+'" target="_blank" rel="noopener">'+esc(r.label)+'</a>';}).join('')+'</div></div>';}).join('')
   :'<div class="card"><h3>Em breve</h3><p>Os palestrantes do VI Fórum serão anunciados aqui no app, em primeira mão para os inscritos. Você receberá um aviso.</p></div>';
  var prev=D.edicao_anterior.programacao.map(function(s){return '<div class="card"><h3 style="text-transform:none;letter-spacing:0;font-family:var(--f-body);font-size:.95rem">'+esc(s.titulo)+'</h3><p class="small muted">'+esc(s.quem)+'</p></div>';}).join('');
  h(body+'<section class="section" style="margin-top:22px"><div class="section-h"><h2>Quem já passou pelo Fórum</h2><a href="#/anterior">V Fórum</a></div>'+prev+'</section>');
}

/* ---------- Avisos ---------- */
function unreadAvisos(){var seen=LS.get('seen',[]);return D.avisos.filter(function(a){return seen.indexOf(a.id)<0;}).length;}
function updateBadge(){if(!D)return;var n=unreadAvisos();var b=document.getElementById('badge-avisos');b.hidden=!n;b.textContent=n;if(navigator.setAppBadge){if(n)navigator.setAppBadge(n);else if(navigator.clearAppBadge)navigator.clearAppBadge();}}
function avisoCard(a){var seen=LS.get('seen',[]);var un=seen.indexOf(a.id)<0;return '<a class="card aviso'+(un?' unread':'')+(a.destaque?' destaque':'')+'" href="#/aviso/'+esc(a.id)+'"><div class="aviso-dot"></div><div style="flex:1;min-width:0"><div class="aviso-date">'+fmtData(a.data)+'</div><h3>'+esc(a.titulo)+'</h3><p>'+esc(a.texto.length>140?a.texto.slice(0,140)+'…':a.texto)+'</p></div>'+(a.imagem?'<img class="aviso-thumb" src="'+a.imagem+'" alt="">':'')+'</a>';}
function avisos(){h('<p class="small muted" style="margin:0 0 12px">As novidades do Fórum chegam aqui antes do e-mail. Toque para ler.</p>'+D.avisos.map(avisoCard).join('')+'<div class="card" style="margin-top:14px"><p class="small muted">Quer receber também por WhatsApp e e-mail? <a href="#/inscricao">Faça sua inscrição</a>.</p></div>');}
function aviso(id){var a=null;D.avisos.forEach(function(x){if(x.id===id)a=x;});if(!a){location.hash='#/avisos';return;}
  var seen=LS.get('seen',[]);if(seen.indexOf(id)<0){seen.push(id);LS.set('seen',seen);updateBadge();}
  var retrato=a.imagem&&/palestrantes\//.test(a.imagem);var interno=a.link&&a.link.charAt(0)==='#';
  h('<div class="card'+(a.destaque?' destaque':'')+'">'+(a.imagem&&retrato?'<img src="'+a.imagem+'" alt="" class="aviso-retrato">':'')+'<div class="aviso-date">'+fmtData(a.data)+'</div><h3 style="margin:6px 0 10px;font-size:1.2rem">'+esc(a.titulo)+'</h3>'+a.texto.split('\n').map(function(p){return '<p>'+esc(p)+'</p>';}).join('')+(a.imagem&&!retrato?'<img src="'+a.imagem+'" alt="" style="border-radius:12px;margin-top:10px">':'')+(a.link?'<div class="btn-row"><a class="btn btn-teal" href="'+a.link+'"'+(interno?'':' target="_blank" rel="noopener"')+'>'+esc(a.link_label||'Abrir')+'</a></div>':'')+'</div><div class="btn-row"><button class="btn btn-outline btn-sm" id="share-aviso">Compartilhar aviso</button></div>');
  document.getElementById('share-aviso').onclick=function(){share(a.titulo,a.texto+'\n\n'+D.evento.app_url+'#/aviso/'+a.id);};
}

/* ---------- Credencial / QR ---------- */
function credencial(){
  var me=LS.get('me',null);var e=D.evento;
  if(!me||credencial._editing){
    var m=me||{};var tipos=['Participante','Palestrante','Patrocinador','Imprensa','Estudante','Organização'];
    var storageOk=(function(){try{localStorage.setItem('forum_t','1');localStorage.removeItem('forum_t');return true;}catch(x){return false;}})();
    var aviso=!storageOk?'<div class="notice">⚠️ Este navegador está bloqueando o salvamento (modo privado ou restrição). A credencial não vai ficar guardada. Abra o app pelo ícone instalado ou pelo Safari normal.</div>':(!me&&!isStandalone()?'<div class="notice">💡 Já criou sua credencial antes? Ela fica salva no lugar onde foi criada. Se você a fez no Safari e agora está no app instalado (ou abriu pelo WhatsApp), precisa criar uma vez aqui também. Leva 30 segundos.</div>':'');
    h(aviso+'<div class="card"><p class="kicker">Sua credencial</p><h3>'+(me?'Editar credencial':'Crie seu QR Code')+'</h3><p class="small muted">Preencha uma vez. Seu QR Code fica salvo neste aparelho e serve para o credenciamento e para trocar contato com outros participantes: quem escanear com a câmera do celular salva você direto na agenda. Nome, empresa e contato também ficam com a organização do Fórum, para controle de uso do app.</p><form id="f-me"><div class="field"><label>Nome completo</label><input name="nome" required autocomplete="name" value="'+esc(m.nome||'')+'"></div><div class="field"><label>Empresa ou instituição</label><input name="empresa" autocomplete="organization" value="'+esc(m.empresa||'')+'"></div><div class="field"><label>Cargo ou função</label><input name="cargo" autocomplete="organization-title" value="'+esc(m.cargo||'')+'"></div><div class="field"><label>E-mail</label><input name="email" type="email" autocomplete="email" value="'+esc(m.email||'')+'"></div><div class="field"><label>WhatsApp</label><input name="fone" type="tel" autocomplete="tel" placeholder="(48) 9 9999-9999" value="'+esc(m.fone||'')+'"></div><div class="field"><label>Perfil</label><select name="tipo">'+tipos.map(function(t){return '<option'+(m.tipo===t?' selected':'')+'>'+t+'</option>';}).join('')+'</select></div><button class="btn btn-teal btn-block" type="submit">'+(me?'Salvar':'Gerar minha credencial')+'</button>'+(me?'<div class="btn-row"><button type="button" class="btn btn-outline btn-sm btn-block" id="me-cancel">Cancelar</button></div>':'')+'</form></div>');
    document.getElementById('f-me').onsubmit=function(ev){ev.preventDefault();var fd=new FormData(ev.target);var o={};fd.forEach(function(v,k){o[k]=String(v).trim();});LS.set('me',o);pingUso(true);credencial._editing=false;if(!LS.get('me',null)){toast('Não foi possível salvar neste navegador.');}credencial();toast(me?'Credencial atualizada':'Credencial criada');};
    var mc=document.getElementById('me-cancel');if(mc)mc.onclick=function(){credencial._editing=false;credencial();};
    return;
  }
  var A=function(t){return String(t||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^\x20-\x7e]/g,'');};
  var vcard='BEGIN:VCARD\nVERSION:3.0\nN:'+A(me.nome)+'\nFN:'+A(me.nome)+(me.empresa?'\nORG:'+A(me.empresa):'')+(me.cargo?'\nTITLE:'+A(me.cargo):'')+(me.fone?'\nTEL;TYPE=CELL:'+me.fone.replace(/[^\d+]/g,''):'')+(me.email?'\nEMAIL:'+A(me.email):'')+'\nNOTE:VI Forum ACATMAR 2026 TIPO='+A(me.tipo||'Participante')+'\nEND:VCARD';
  h('<div class="badge-card"><div class="badge-top"><img src="../media/logos/acatmar-branca.png" alt="ACATMAR"><span>'+esc(e.nome)+'</span></div><div class="badge-name">'+esc(me.nome)+'</div><div class="badge-sub">'+esc([me.cargo,me.empresa].filter(Boolean).join(' · '))+'</div><span class="badge-tipo">'+esc(me.tipo||'Participante')+'</span><div class="badge-qr" id="qr"></div><div class="badge-foot"><span>'+esc(e.data_texto)+'</span><span>'+esc(e.local.bairro)+' · Fpolis</span></div></div>'
   +'<p class="small muted" style="text-align:center;margin:12px 0">Mostre este QR Code no credenciamento. Para networking, peça para escanearem com a câmera: seu contato é salvo na hora.</p>'
   +'<div class="btn-row"><button class="btn btn-outline btn-sm" id="me-edit">Editar dados</button><button class="btn btn-navy btn-sm" id="me-share">Compartilhar contato</button></div>');
  try{new QRCode(document.getElementById('qr'),{text:vcard,width:190,height:190,correctLevel:QRCode.CorrectLevel.L,colorDark:'#0a2540'});}catch(err){try{document.getElementById('qr').innerHTML='';new QRCode(document.getElementById('qr'),{text:'BEGIN:VCARD\nVERSION:3.0\nFN:'+A(me.nome)+'\nEND:VCARD',width:190,height:190,correctLevel:QRCode.CorrectLevel.L,colorDark:'#0a2540'});}catch(e2){document.getElementById('qr').innerHTML='<p class="small" style="color:#0a2540;margin:0">Não foi possível gerar o QR. Edite os dados e tente de novo.</p>';}}
  document.getElementById('me-edit').onclick=function(){credencial._editing=true;credencial();};
  document.getElementById('me-share').onclick=function(){share(me.nome+' · '+e.curto,[me.nome,me.cargo,me.empresa,me.email,me.fone].filter(Boolean).join('\n'));};
}

/* ---------- Patrocinadores ---------- */
function patrocinadores(){
  var c=D.patrocinio_cta;
  var html='<img src="media/quem-faz-acontecer.jpg" alt="Quem faz o VI Fórum acontecer: patrocinadores e apoiadores" style="width:100%;border-radius:14px;display:block;margin:0 0 16px">';
  html+='<p class="small muted" style="margin:0 0 10px">Conheça um pouco de cada um:</p>';
  D.patrocinadores.forEach(function(cota){
    var comTexto=cota.empresas.filter(function(p){return (p.texto||'').trim();});
    if(!comTexto.length)return;
    html+='<div class="section-h" style="margin-top:6px"><h2>'+esc(cota.cota)+'</h2></div>';
    comTexto.forEach(function(p){
      var links=(p.site?'<a class="btn btn-outline btn-sm" href="'+p.site+'" target="_blank" rel="noopener">Site</a>':'')+(p.instagram?'<a class="btn btn-navy btn-sm" href="'+p.instagram+'" target="_blank" rel="noopener">Instagram</a>':'');
      html+='<div class="card"><h3 style="text-transform:none;letter-spacing:0;font-family:var(--f-body);font-size:1.02rem">'+esc(p.nome)+'</h3><p class="small">'+esc(p.texto||'')+'</p>'+(p.materia?'<div class="materia"><p class="kicker">Novidade · '+fmtData(p.materia.data)+'</p><b>'+esc(p.materia.titulo)+'</b><p class="small">'+esc(p.materia.resumo)+'</p><a class="btn btn-teal btn-sm" href="'+p.materia.link+'" target="_blank" rel="noopener">Ler a matéria</a></div>':'')+(links?'<div class="btn-row">'+links+'</div>':'')+'</div>';
    });
  });
  html+='<div class="card" style="background:var(--navy);color:#fff;border:0;margin-top:14px"><p class="kicker" style="color:var(--teal-b)">Patrocínio e apoio</p><h3 style="color:#fff">'+esc(c.titulo)+'</h3><p class="small" style="opacity:.9">'+esc(c.texto)+'</p><div class="btn-row"><a class="btn btn-teal btn-sm" href="mailto:'+c.email+'?subject='+encodeURIComponent('Patrocínio '+D.evento.curto)+'">Falar com a ACATMAR</a></div></div>';
  h(html);
}

/* ---------- Local ---------- */
function local(){
  var l=D.evento.local;
  h((l.foto?'<img src="'+l.foto+'" alt="'+esc(l.nome)+'" style="border-radius:16px;margin:0 0 4px;box-shadow:0 6px 20px rgba(6,23,38,.2)">'+(l.foto_legenda?'<p class="small muted" style="margin:6px 4px 14px">'+esc(l.foto_legenda)+'</p>':''):'')
   +'<div class="card"><p class="kicker">Local do evento</p><h3>'+esc(l.nome)+'</h3>'+(l.sala?'<p><b>'+esc(l.sala)+'</b></p>':'')+'<p>'+esc(l.endereco)+'</p><div class="btn-row"><a class="btn btn-teal btn-sm" href="'+l.maps+'" target="_blank" rel="noopener">Google Maps</a><a class="btn btn-navy btn-sm" href="'+l.waze+'" target="_blank" rel="noopener">Waze</a><a class="btn btn-outline btn-sm" href="'+l.apple+'" target="_blank" rel="noopener">Apple Maps</a></div></div>'
   +'<div class="card"><h3>Como chegar e dicas</h3>'+l.dicas.map(function(d){return '<p class="small">• '+esc(d)+'</p>';}).join('')+'</div>'
   +'<div class="card"><h3>Horário</h3><p>'+esc(D.evento.data_texto)+'<br>'+esc(D.evento.horario_texto)+'. Credenciamento a partir das 7h30.</p></div>');
}

/* ---------- Interagir ---------- */
function interagir(sessId){
  var e=D.evento;var sess=null;D.programacao.forEach(function(s){if(s.id===sessId)sess=s;});var me=LS.get('me',{})||{};
  var opts='<option value="">Geral / não sei</option>'+D.programacao.filter(function(s){return s.tipo!=='pausa'&&s.tipo!=='org';}).map(function(s){return '<option'+(sess&&sess.id===s.id?' selected':'')+'>'+esc(s.hora.replace(':','h')+' · '+s.titulo)+'</option>';}).join('');
  var wa=e.whatsapp_comunidade?'<a href="'+e.whatsapp_comunidade+'" target="_blank" rel="noopener"><i>💬</i>Grupo do Fórum no WhatsApp</a>':'';
  h('<div class="menu">'+wa+'<a href="'+e.instagram+'" target="_blank" rel="noopener"><i>📸</i>@acatmarassociacao no Instagram</a><a href="#" id="share-app"><i>📲</i>Convidar alguém para o app</a><a href="https://wa.me/'+e.whatsapp_acatmar+'?text='+encodeURIComponent('Olá! Estou no app do '+e.curto+'.')+'" target="_blank" rel="noopener"><i>📱</i>WhatsApp da ACATMAR</a><a href="mailto:'+e.email+'"><i>✉️</i>E-mail da organização</a></div>'
   +'<div class="card" id="c-perg"><p class="kicker">Pergunte ao palestrante</p><h3>Envie sua pergunta</h3><p class="small muted">A pergunta vai pelo WhatsApp direto para a equipe da ACATMAR ('+esc(e.whatsapp_acatmar_texto||'')+'), que a leva ao palestrante durante o Fórum.</p><form id="f-perg"><div class="field"><label>Palestra</label><select name="palestra">'+opts+'</select></div><div class="field"><label>Sua pergunta</label><textarea name="pergunta" required maxlength="600"></textarea></div><div class="field"><label>Seu nome</label><input name="nome" value="'+esc(me.nome||'')+'" required></div><button class="btn btn-teal btn-block" type="submit">Enviar pelo WhatsApp</button></form></div>'
   +'<div class="card" id="c-aval"><p class="kicker">Sua opinião</p><h3>Avalie o Fórum</h3><form id="f-aval"><input type="hidden" name="_subject" value="[App VI Fórum] Avaliação"><input type="text" name="_honey" style="display:none"><div class="field"><label>Nota geral</label><select name="nota"><option>5 · Excelente</option><option>4 · Muito bom</option><option>3 · Bom</option><option>2 · Regular</option><option>1 · Ruim</option></select></div><div class="field"><label>O que mais gostou e o que podemos melhorar?</label><textarea name="comentario" required maxlength="800"></textarea></div><div class="field"><label>Seu nome</label><input name="nome" value="'+esc(me.nome||'')+'"></div><button class="btn btn-navy btn-block" type="submit">Enviar avaliação</button></form></div>');
  document.getElementById('share-app').onclick=function(ev){ev.preventDefault();shareApp();};
  document.getElementById('f-perg').onsubmit=function(ev){ev.preventDefault();var f=ev.target;var msg='*Pergunta ao palestrante · '+e.curto+'*\n'+'Palestra: '+(f.palestra.value||'Geral')+'\n'+'Pergunta: '+f.pergunta.value.trim()+'\n'+'De: '+f.nome.value.trim();window.open('https://wa.me/'+e.whatsapp_acatmar+'?text='+encodeURIComponent(msg),'_blank');};
  ['f-aval'].forEach(function(id){var f=document.getElementById(id);f.onsubmit=function(ev){ev.preventDefault();var btn=f.querySelector('button');btn.disabled=true;btn.textContent='Enviando…';var fd=new FormData(f);fd.append('origem','App VI Fórum ACATMAR');
    fetch(e.formsubmit,{method:'POST',headers:{'Accept':'application/json'},body:fd}).then(function(r){if(!r.ok)throw 0;f.parentNode.innerHTML='<div class="ok-box">⚓ Recebido! Obrigado pela participação.</div>';}).catch(function(){btn.disabled=false;btn.textContent='Tentar de novo';toast('Não foi possível enviar agora. Verifique a conexão.');});};});
}

/* ---------- Certificado ---------- */
function normNome(v){
  var s=String(v||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
  return s.replace(/\(.*?\)/g,'').replace(/[^a-z ]/g,' ').replace(/\s+/g,' ').trim();
}
function sha12(txt){
  if(!(window.crypto&&crypto.subtle))return Promise.resolve(null);
  return crypto.subtle.digest('SHA-256',new TextEncoder().encode('acatmar6:'+txt)).then(function(b){
    return Array.prototype.map.call(new Uint8Array(b),function(x){return ('0'+x.toString(16)).slice(-2);}).join('').slice(0,12);
  });
}
function esteve(nome){
  var lista=(D.certificado&&D.certificado.presenca)||[];
  var k=normNome(nome); if(!k)return Promise.resolve(false);
  var ps=k.split(' '), tent=[k, ps[0]];
  if(ps.length>1){
    tent.push(ps[0]+' '+ps[ps.length-1]);
    tent.push(ps[0]+' '+ps[1]);
    tent.push(ps.slice(0,3).join(' '));
    for(var j=1;j<ps.length;j++) tent.push(ps[0]+' '+ps[j]);
    if(ps.length>=3) tent.push(ps[0]+' '+ps[1]+' '+ps[ps.length-1]);
  }
  tent=tent.filter(function(x,i,a2){return x&&a2.indexOf(x)===i;});
  return Promise.all(tent.map(sha12)).then(function(h){
    if(h[0]===null)return true;
    for(var i=0;i<h.length;i++){ if(h[i]&&lista.indexOf(h[i])>=0) return true; }
    return false;
  });
}
function certificado(){
  var c=D.certificado,me=LS.get('me',{})||{};
  if(!c.liberado){h('<div class="card"><p class="kicker">Certificado de conclusão</p><h3>'+esc(c.titulo||'Disponível após o evento')+'</h3><p>'+esc(c.texto)+'</p><p class="small muted">Carga horária: '+esc(c.carga_horaria)+'.</p></div>');return;}
  var A=D.avaliacao||{};
  var pede = A.ativa && !LS.get('avaliou',false) && !LS.get('pulou_aval',false);
  if(pede){
    h('<section class="section"><div class="card" style="background:var(--navy,#0a2540);color:#fff;border:0">'
     +'<p class="kicker" style="color:var(--teal-b,#35c9da)">Antes de baixar</p>'
     +'<h3 style="color:#fff">Podemos contar com você?</h3>'
     +'<p class="small" style="opacity:.9">Sua avaliação do VI Fórum leva uns 3 minutos e é com ela que a gente monta o VII. '
     +'Sua opinião sobre o evento vale muito para a gente.</p>'
     +'<div class="btn-row"><a class="btn btn-teal btn-block btn-xl" href="#/avaliacao">Responder agora · 3 minutos</a></div>'
     +'<p style="text-align:center;margin-top:10px"><a href="#" id="pular-aval" class="small" style="color:#9fc7d8">Prefiro baixar o certificado agora</a></p>'
     +'</div></section>');
    document.getElementById('pular-aval').onclick=function(ev){ev.preventDefault();LS.set('pulou_aval',true);certificado();};
    return;
  }
  h('<div class="card"><p class="kicker">Certificado de conclusão</p><h3>'+esc(c.titulo||'Emita seu certificado')+'</h3><p class="small">'+esc(c.texto)+'</p>'
   +'<form id="f-cert"><div class="field"><label>Nome completo *</label><input name="nome" required autocomplete="name" value="'+esc(me.nome||'')+'"></div>'
   +'<div class="field"><label>CPF *</label><input name="cpf" id="c-cpf" inputmode="numeric" placeholder="000.000.000-00" required></div>'
   +'<div class="field"><label>Empresa <span class="small muted">(se você representa uma)</span></label><input name="empresa" autocomplete="organization" value="'+esc(me.empresa||'')+'"></div>'
   +'<div class="field"><label>CNPJ da empresa <span class="small muted">(se tiver)</span></label><input name="cnpj" id="c-cnpj" inputmode="numeric" placeholder="00.000.000/0000-00"></div>'
   +'<button class="btn btn-teal btn-block" type="submit">Gerar meu certificado</button></form>'
   +'<div class="notice" style="margin-top:12px;background:#f3f7fb;border-color:#cfdae8"><p class="small" style="margin:0">'
   +'<b>Por que pedimos esses dados.</b> O nome vai impresso no certificado, e o CPF serve para registrar '
   +'a emissão e permitir que a ACATMAR confirme o documento se alguém pedir comprovação. '
   +'Guardamos só isso, não repassamos a terceiros e você pode pedir a exclusão quando quiser pelo e-mail '
   +'<a href="mailto:acatmarpresidencia@gmail.com">acatmarpresidencia@gmail.com</a>. '
   +'Detalhes na <a href="https://www.acatmar.org/privacidade.html" target="_blank" rel="noopener">Política de Privacidade</a>.</p></div>'
   +'<div id="cert-msg"></div>'
   +'<p class="small muted" style="margin-top:12px">Carga horária: '+esc(c.carga_horaria)+'. O arquivo é gerado no seu aparelho, em PDF.</p></div>');
  var xc=document.getElementById('c-cpf'), xn=document.getElementById('c-cnpj');
  if(xc)xc.oninput=function(){xc.value=mascaraCPF(xc.value);};
  if(xn)xn.oninput=function(){xn.value=mascaraCNPJ(xn.value);};
  document.getElementById('f-cert').onsubmit=function(ev){
    ev.preventDefault();
    var fd=new FormData(ev.target);
    var nome=String(fd.get('nome')).replace(/\s+/g,' ').trim();
    var cpf=String(fd.get('cpf')||'').trim();
    var empresa=String(fd.get('empresa')||'').trim();
    var cnpj=String(fd.get('cnpj')||'').trim();
    var m=document.getElementById('cert-msg');
    function ec(t,el){m.innerHTML='<div class="notice">'+t+'</div>';if(el){el.focus();el.scrollIntoView({block:'center',behavior:'smooth'});}}
    if(nome.split(' ').length<2) return ec('Digite o nome completo, com sobrenome.');
    if(!validaCPF(cpf)) return ec('Confira o CPF: parece que falta um número ou algum dígito está errado.',xc);
    if(cnpj && !validaCNPJ(cnpj)) return ec('Confira o CNPJ. Se a empresa não tiver, deixe em branco.',xn);
    m.innerHTML='<p class="small muted">Conferindo a lista de presença…</p>';
    esteve(nome).then(function(ok){
      if(!ok){
        var wa=soDigitos(D.evento.whatsapp_acatmar||D.evento.whatsapp||'');
        var txt=encodeURIComponent('Oi! Sou '+nome+' e participei do VI Fórum, mas o app não encontrou meu nome na lista para emitir o certificado.');
        m.innerHTML='<div class="notice" style="border-color:#f2b54a;background:#fff3d6">'
          +'<p class="small" style="margin:0 0 8px"><b>Não achamos esse nome na lista de presença.</b> '
          +'Tente escrever como está na sua inscrição, ou só o primeiro nome e o sobrenome.</p>'
          +'<p class="small" style="margin:0 0 10px">Se você esteve no Fórum, foi engano nosso e a gente libera na hora.</p>'
          +(wa?'<a class="btn btn-navy btn-block btn-sm" target="_blank" rel="noopener" href="https://wa.me/'+esc(wa)+'?text='+txt+'">Falar com a ACATMAR no WhatsApp</a>':'')
          +'</div>';
        return;
      }
      m.innerHTML='<p class="small muted">Gerando o PDF…</p>';
      try{ LS.set('me',Object.assign(LS.get('me',{})||{},{nome:nome,empresa:empresa})); }catch(e2){}
      fetch(API+'/certificado',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({id:devId(),nome:nome,cpf:cpf,empresa:empresa,cnpj:cnpj})}).catch(function(){});
      var s=document.createElement('script');s.src='lib/jspdf.umd.min.js';
      s.onload=function(){gerarPDF(nome,m);};
      s.onerror=function(){m.innerHTML='<div class="notice">Não foi possível carregar o gerador. Verifique a conexão e tente de novo.</div>';};
      document.body.appendChild(s);
    });
  };
}
function gerarPDF(nome,m){
  var c=D.certificado;
  var img=new Image();img.crossOrigin='anonymous';
  img.onload=function(){
    try{
      var cv=document.createElement('canvas');cv.width=img.naturalWidth;cv.height=img.naturalHeight;
      cv.getContext('2d').drawImage(img,0,0);
      var dados=cv.toDataURL('image/jpeg',0.9);
      var doc=new window.jspdf.jsPDF({orientation:'landscape',unit:'mm',format:'a4',compress:true});
      doc.addImage(dados,'JPEG',0,0,297,210);
      doc.setTextColor(15,47,87);doc.setFont('times','bold');
      var t=26;doc.setFontSize(t);
      while(doc.getTextWidth(nome)>215&&t>13){t-=1;doc.setFontSize(t);}
      doc.text(nome,148.5,108,{align:'center'});
      var arq='certificado-vi-forum-'+normNome(nome).replace(/ /g,'-')+'.pdf';
      doc.save(arq);
      if(m)m.innerHTML='<div class="ok-box">✅ Certificado gerado. Procure o arquivo <b>'+esc(arq)+'</b> nos seus downloads.</div>';
      toast('Certificado gerado');
    }catch(e){ if(m)m.innerHTML='<div class="notice">Não foi possível gerar aqui. Tente pelo navegador, em acatmar.org/app.</div>'; }
  };
  img.onerror=function(){ if(m)m.innerHTML='<div class="notice">Não foi possível carregar a arte do certificado. Verifique a conexão.</div>'; };
  img.src=(c.fundo||'media/certificado-fundo.jpg')+'?v='+encodeURIComponent(D.versao);
}

/* ---------- Instalar ---------- */
var deferredPrompt=null;
window.addEventListener('beforeinstallprompt',function(ev){ev.preventDefault();deferredPrompt=ev;maybeBanner();});
function isStandalone(){return window.matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;}
function isIOS(){return /iphone|ipad|ipod/i.test(navigator.userAgent)&&!window.MSStream;}
function inAppBrowser(){var ua=navigator.userAgent||'';return /WhatsApp|Instagram|FBAN|FBAV|FB_IAB|Line\/|LinkedInApp|Twitter|TikTok|Telegram/i.test(ua)||(isIOS()&&!/Safari\//.test(ua)&&!isStandalone())||(isIOS()&&/CriOS|FxiOS|EdgiOS/.test(ua)&&false);}
function inAppWarn(){if(isStandalone()||!inAppBrowser())return;if(document.getElementById('inapp-ov'))return;
  var ios=isIOS();var ov=document.createElement('div');ov.id='inapp-ov';ov.className='inapp-ov';
  ov.innerHTML='<div class="inapp-card"><img src="icons/icon-192.png" alt=""><h3>Abra no '+(ios?'Safari':'Chrome')+' para instalar</h3><p>Você está no navegador interno do '+(/WhatsApp/i.test(navigator.userAgent)?'WhatsApp':/Instagram/i.test(navigator.userAgent)?'Instagram':'aplicativo')+'. Aqui dá para ver o app, mas não dá para instalar na tela inicial.</p>'
   +(ios?'<ol><li>Toque no botão <b>⋯</b> ou no ícone da bússola <b>⌘</b> no canto da tela</li><li>Escolha <b>"Abrir no Safari"</b></li><li>No Safari, toque em <b>Compartilhar</b> e em <b>"Adicionar à Tela de Início"</b></li></ol>':'<ol><li>Toque no menu <b>⋮</b> no canto superior</li><li>Escolha <b>"Abrir no Chrome"</b> (ou "Abrir no navegador")</li><li>No Chrome, toque em <b>Instalar</b></li></ol>')
   +'<div class="btn-row">'+(ios?'<a class="btn btn-teal" href="x-safari-https://www.acatmar.org/app/">Abrir no Safari</a>':'<a class="btn btn-teal" href="intent://www.acatmar.org/app/#Intent;scheme=https;package=com.android.chrome;S.browser_fallback_url=https%3A%2F%2Fwww.acatmar.org%2Fapp%2F;end">Abrir no Chrome</a>')+'<button class="btn btn-outline" id="inapp-copy">Copiar o link</button><button class="btn btn-light" id="inapp-close">Continuar aqui mesmo</button></div><p class="small" style="opacity:.75;margin:10px 0 0">Se preferir, cole <b>acatmar.org/app</b> direto na barra do '+(ios?'Safari':'Chrome')+'.</p></div>';
  document.body.appendChild(ov);
  document.getElementById('inapp-close').onclick=function(){ov.remove();};
  document.getElementById('inapp-copy').onclick=function(){var u='https://www.acatmar.org/app/';(navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject()).then(function(){toast('Link copiado. Cole no '+(ios?'Safari':'Chrome')+'.');},function(){prompt('Copie o link:',u);});};
}
function iosCoach(){if(!isIOS()||isStandalone()||inAppBrowser())return;if(document.getElementById('ios-coach'))return;try{if(sessionStorage.getItem('forum_coach_off'))return;}catch(e){}
  var c=document.createElement('div');c.id='ios-coach';c.className='ios-coach';
  c.innerHTML='<button class="ib-close" id="coach-close" aria-label="Fechar">×</button><div class="coach-t">Instale em 2 toques</div><div class="coach-steps"><div><b>1</b> Toque no botão <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg> <b>Compartilhar</b> aqui embaixo</div><div><b>2</b> Escolha <b>"Adicionar à Tela de Início"</b> e confirme</div></div><div class="coach-arrow">▼</div>';
  document.body.appendChild(c);document.getElementById('coach-close').onclick=function(){c.remove();try{sessionStorage.setItem('forum_coach_off','1');}catch(e){}};
  var ib=document.getElementById('install-banner');if(ib)ib.hidden=true;}
function androidOpenChrome(){if(isIOS()||isStandalone()||deferredPrompt)return;if(!/Android/i.test(navigator.userAgent))return;if(document.getElementById('inapp-ov'))return;
  var b=document.getElementById('install-banner');b.hidden=false;b.querySelector('.ib-text').innerHTML='<b>Instale o app do Fórum</b><span>Toque para abrir no Chrome e instalar em um toque.</span>';
  var btn=document.getElementById('ib-install');btn.textContent='Abrir no Chrome';btn.onclick=function(){location.href='intent://www.acatmar.org/app/#Intent;scheme=https;package=com.android.chrome;S.browser_fallback_url=https%3A%2F%2Fwww.acatmar.org%2Fapp%2F;end';};
  document.getElementById('ib-close').onclick=function(){b.hidden=true;};}
var CHROME_INTENT='intent://www.acatmar.org/app/#Intent;scheme=https;package=com.android.chrome;S.browser_fallback_url=https%3A%2F%2Fwww.acatmar.org%2Fapp%2F;end';
function installGate(){if(isStandalone())return;try{if(sessionStorage.getItem('forum_gate_off'))return;}catch(e){}
  var old=document.getElementById('gate');if(old)old.remove();var ov=document.getElementById('inapp-ov');if(ov)ov.remove();var co=document.getElementById('ios-coach');if(co)co.remove();var ib=document.getElementById('install-banner');if(ib)ib.hidden=true;
  var ios=isIOS(),inapp=inAppBrowser(),and=/Android/i.test(navigator.userAgent);
  var I_SHARE='<svg viewBox="0 0 24 24" fill="none" stroke="#0a84ff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/><polyline points="15.5 6.5 12 3 8.5 6.5"/><line x1="12" y1="3" x2="12" y2="15"/></svg>';
  var I_PLUS='<svg viewBox="0 0 24 24" fill="none" stroke="#111" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="3.5" width="17" height="17" rx="4"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>';
  var I_COMPASS='<svg viewBox="0 0 24 24" fill="none" stroke="#0a84ff" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><polygon points="15.5 8.5 13.5 13.5 8.5 15.5 10.5 10.5" fill="#0a84ff" stroke="none"/></svg>';
  var body='',arrow=false,title='Instale o app';
  if(ios&&inapp){title='Abra no Safari';body='<a class="btn btn-teal btn-block btn-xl" href="x-safari-https://www.acatmar.org/app/">Abrir no Safari</a><div class="gate-ou">ou toque neste botão do WhatsApp</div><div class="gate-pic">'+I_COMPASS+'</div>';}
  else if(ios){title='Instale o app';body='<div class="gate-big"><div class="gate-num">1</div><div class="gate-where">Na barra do Safari, onde está escrito <b>acatmar.org</b>, toque no botão:</div><div class="gate-pic" id="gate-fake">'+I_SHARE+'</div><div class="gate-txt"><small>Ele fica ao lado do endereço, em cima ou embaixo da tela</small></div></div><div class="gate-big"><div class="gate-num">2</div><div class="gate-where">Na lista que abrir, toque em <b>Ver Mais</b> e arraste para baixo até achar:</div><div class="gate-row">'+I_PLUS+'<span>Adicionar à Tela de Início</span></div><div class="gate-txt"><small>Toque nela e depois em <b>Adicionar</b>, no canto de cima</small></div></div>';}
  else if(and&&/SamsungBrowser/i.test(navigator.userAgent)){title='Instale pelo Chrome';body='<a class="btn btn-teal btn-block btn-xl" href="'+CHROME_INTENT+'">Abrir no Chrome e instalar</a><p class="small" style="opacity:.85;margin:12px 0 0">No navegador da Samsung a instalação costuma falhar. Pelo Chrome funciona em um toque.</p>';}
  else if(and&&deferredPrompt){body='<button class="btn btn-teal btn-block btn-xl" id="gate-inst">Instalar</button><p class="small" style="opacity:.75;margin:12px 0 0">Se aparecer "não foi possível instalar", abra <b>acatmar.org/app</b> no Chrome e tente de novo.</p>';}
  else if(and){body='<a class="btn btn-teal btn-block btn-xl" href="'+CHROME_INTENT+'">Instalar</a>';}
  else {body='<p>Abra <b>acatmar.org/app</b> no celular para instalar.</p>';}
  var g=document.createElement('div');g.id='gate';g.className='gate'+(arrow?' gate-arrow':'');
  g.innerHTML='<div class="gate-in"><img src="icons/icon-192.png" alt=""><h2>'+title+'</h2>'+body+'<button class="gate-skip" id="gate-skip">Agora não</button></div>'+(arrow?'<div class="gate-down">▼</div>':'');
  document.body.appendChild(g);
  document.getElementById('gate-skip').onclick=function(){g.remove();try{sessionStorage.setItem('forum_gate_off','1');}catch(e){}};
  var gi=document.getElementById('gate-inst');if(gi)gi.onclick=function(){deferredPrompt.prompt();deferredPrompt.userChoice.then(function(){g.remove();});};
  var gf=document.getElementById('gate-fake');if(gf)gf.onclick=function(){var m=document.getElementById('gate-msg');if(!m){m=document.createElement('div');m.id='gate-msg';m.className='gate-msg';gf.parentNode.insertBefore(m,gf.nextSibling);}m.textContent='Este é só o desenho. O botão de verdade fica na barra do Safari, ao lado de acatmar.org.';if(navigator.vibrate)navigator.vibrate(60);};
}
window.addEventListener('beforeinstallprompt',function(){if(document.getElementById('gate'))installGate();});
function maybeBanner(){if(isStandalone())return;installGate();return;if(isIOS()){iosCoach();return;}if(LS.get('banner_off',false))return;var b=document.getElementById('install-banner');b.hidden=false;
  document.getElementById('ib-install').onclick=function(){if(deferredPrompt){deferredPrompt.prompt();deferredPrompt.userChoice.then(function(){b.hidden=true;deferredPrompt=null;});}else{location.hash='#/instalar';b.hidden=true;}};
  document.getElementById('ib-close').onclick=function(){b.hidden=true;LS.set('banner_off',true);};}
function instalar(){
  var video='<div class="card" style="text-align:center"><p class="kicker">Veja como fazer</p><h3 style="margin-bottom:10px">Instalar no iPhone em 20 segundos</h3><video src="media/como-instalar-iphone.mp4" poster="media/como-instalar-iphone-capa.jpg" controls playsinline preload="none" style="width:100%;max-width:300px;border-radius:14px;display:block;margin:0 auto"></video><p class="small muted" style="margin:10px 0 0">Toque no play. O vídeo mostra o caminho: botão Compartilhar do Safari, <b>Ver Mais</b>, e <b>Adicionar à Tela de Início</b>.</p></div>';
  var ios='<div class="steps"><div><span>Abra este endereço no <b>Safari</b> (no iPhone, só o Safari instala apps da web): <b>acatmar.org/app</b></span></div><div><span>Toque no botão <b>Compartilhar do Safari</b>: o quadrado com a seta para cima, na <b>barra de baixo</b> do navegador. Atenção: não é o botão dentro do app, é o do Safari.</span></div><div><span>Role e toque em <b>"Adicionar à Tela de Início"</b>.</span></div><div><span>Confirme em <b>Adicionar</b>. O ícone do Fórum aparece na sua tela inicial.</span></div></div>';
  var and='<div class="steps"><div><span>Abra <b>acatmar.org/app</b> no <b>Chrome</b>.</span></div><div><span>Toque em <b>Instalar</b> no aviso que aparece, ou no menu ⋮ escolha <b>"Instalar app"</b> / <b>"Adicionar à tela inicial"</b>.</span></div><div><span>Confirme. O app do Fórum aparece junto dos seus outros apps.</span></div><div><span><b>Deu "não foi possível instalar o aplicativo web"?</b> Isso acontece no navegador da Samsung. Abra <b>acatmar.org/app</b> no <b>Chrome</b> e instale por lá.</span></div></div>';
  h((isStandalone()?'<div class="ok-box" style="margin-bottom:14px">✅ O app já está instalado neste aparelho.</div>':'')
   +(deferredPrompt?'<div class="card" style="text-align:center"><h3>Instalar agora</h3><p class="small muted">Seu celular permite instalar em um toque.</p><button class="btn btn-teal btn-block" id="btn-inst">Instalar o app</button></div>':'')
   +(inAppBrowser()&&!isStandalone()?'<div class="notice">⚠️ Você está no navegador interno de um aplicativo (WhatsApp, Instagram…). Ele não instala apps. <b>Abra no '+(isIOS()?'Safari':'Chrome')+'</b> pelo menu do canto da tela, ou copie o link: <button class="btn btn-navy btn-sm" id="copy-link2" style="margin-top:8px">Copiar acatmar.org/app</button></div>':'')
   +video
   +'<div class="card"><p class="kicker">iPhone e iPad</p><h3>Safari</h3>'+ios+'</div>'
   +'<div class="card"><h3>Não achou "Adicionar à Tela de Início"?</h3><p class="small">• <b>Confira se é o Safari de verdade.</b> Link aberto pelo WhatsApp ou Instagram abre um navegador interno, sem essa opção. Copie <b>acatmar.org/app</b>, abra o Safari pelo ícone dele e cole na barra.</p><p class="small">• <b>Role a lista até o fim.</b> No menu Compartilhar, os apps ficam em cima e as ações embaixo. "Adicionar à Tela de Início" fica quase no final.</p><p class="small">• <b>Se sumiu, reative.</b> No fim do menu Compartilhar toque em "Editar Ações…" e ative "Adicionar à Tela de Início" no "+" verde.</p><p class="small">• Se o aparelho tiver restrição de perfil (comum em celular institucional), use o app direto pelo Safari. Funciona igual, só não fica o ícone.</p></div><div class="card"><p class="kicker">Android</p><h3>Chrome</h3>'+and+'</div>'
   +'<div class="card"><h3>Por que instalar?</h3><p class="small">• Abre em um toque, como um app da loja.<br>• Sua credencial com QR Code aparece na hora no credenciamento.<br>• Programação, local e avisos ficam disponíveis mesmo sem sinal.<br>• Sem cadastro, sem senha, sem ocupar espaço.</p><div class="btn-row"><button class="btn btn-outline btn-sm" id="share-app2">Enviar o link para alguém</button></div></div>');
  var bi=document.getElementById('btn-inst');if(bi)bi.onclick=function(){deferredPrompt.prompt();};
  var cl=document.getElementById('copy-link2');if(cl)cl.onclick=function(){var u='https://www.acatmar.org/app/';(navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject()).then(function(){toast('Link copiado');},function(){prompt('Copie o link:',u);});};
  document.getElementById('share-app2').onclick=shareApp;
}

/* ---------- Sobre / Mais / Anterior / FAQ ---------- */
function sobre(){var s=D.sobre;h('<div class="card"><p class="kicker">'+esc(D.evento.edicao)+'</p><h3>'+esc(D.evento.nome)+'</h3><p>'+esc(s.resumo)+'</p><p>'+esc(s.para_quem)+'</p></div><div class="card"><h3>Por que participar</h3>'+s.motivos.map(function(m){return '<p class="small">✔ '+esc(m)+'</p>';}).join('')+'</div><section class="section"><div class="section-h"><h2>Edições anteriores</h2><a href="#/edicoes">Fotos e histórico</a></div><div class="hist">'+s.historia.map(function(x){return '<a href="#/edicoes" style="text-decoration:none;color:inherit"><b>'+x.ed+'</b><span>'+esc(x.tema)+'<small>'+x.ano+' · '+esc(x.onde)+'</small></span></a>';}).join('')+'</div></section><div class="btn-row"><a class="btn btn-outline btn-sm" href="'+D.evento.site_url+'" target="_blank" rel="noopener">Ver no site da ACATMAR</a></div>');}
function anterior(){var a=D.edicao_anterior;h('<div class="card"><p>'+esc(a.resumo)+'</p></div><div class="gal">'+a.fotos.map(function(f){return '<img src="'+f+'" alt="" loading="lazy">';}).join('')+'</div><section class="section" style="margin-top:16px"><div class="section-h"><h2>Programação de 2025</h2></div>'+a.programacao.map(function(s){return '<div class="card sess"><div class="sess-h" style="flex-basis:60px;font-size:.85rem">'+esc(s.periodo)+'</div><div class="sess-b"><h3>'+esc(s.titulo)+'</h3><div class="quem">'+esc(s.quem)+'</div></div></div>';}).join('')+'</section><div class="btn-row"><a class="btn btn-outline btn-sm" href="'+a.link+'" target="_blank" rel="noopener">Matéria completa no site</a></div>');}
function retroHomeCard(){var e=D.pos_evento;if(!e)return '';
  var f=e.destaque?{src:e.destaque}:(e.fotos&&(e.fotos[1]||e.fotos[0]));
  var nums=(e.numeros||[]).map(function(x){return '<div class="cd"><b>'+esc(x.n)+'</b><span>'+esc(x.t)+'</span></div>';}).join('');
  return '<section class="section"><a class="card" href="#/posevento" style="display:block;padding:0;overflow:hidden;text-decoration:none;color:inherit">'
   +(f?'<img src="'+f.src+'" alt="" style="width:100%;display:block">':'')
   +'<div style="padding:14px 16px 16px"><p class="kicker">20 de outubro de 2026 · IFSC Continente</p>'
   +'<h3 style="margin:2px 0 6px">'+esc(e.titulo)+'</h3><p class="small">'+esc(e.chamada)+'</p>'
   +(nums?'<div class="countdown" style="margin-top:12px">'+nums+'</div>':'')
   +'<div class="btn-row"><span class="btn btn-teal btn-sm">Ver fotos e o resumo</span></div></div></a></section>';}
function posEvento(){var e=D.pos_evento;if(!e){h('<div class="card"><p class="small">Em breve.</p></div>');return;}
  h('<div class="card"><p class="kicker">20 de outubro de 2026 · IFSC Continente</p><h3>'+esc(e.titulo)+'</h3><p>'+esc(e.chamada)+'</p></div>'
   +'<div class="gal">'+e.fotos.map(function(f){return '<figure style="flex:0 0 78%;scroll-snap-align:start;margin:0"><img src="'+f.src+'" alt="'+esc(f.legenda||'')+'" loading="lazy" style="flex:none;width:100%"><figcaption class="small muted" style="margin-top:6px">'+esc(f.legenda||'')+'</figcaption></figure>';}).join('')+'</div>'
   +'<p class="small muted" style="margin:6px 2px 16px">Arraste para o lado para ver as '+e.fotos.length+' fotos.</p>'
   +e.blocos.map(function(b){return '<section class="section"><div class="section-h"><h2>'+esc(b.h)+'</h2></div><div class="card">'+b.p.map(function(x){return '<p>'+esc(x)+'</p>';}).join('')+'</div></section>';}).join('')
   +'<div class="btn-row"><a class="btn btn-outline btn-sm" href="#/certificado">Meu certificado</a><a class="btn btn-outline btn-sm" href="https://www.acatmar.org/" target="_blank" rel="noopener">Site da ACATMAR</a></div>');}
function avaliacao(){
  var A=D.avaliacao;
  if(!A||!A.ativa){h('<div class="card"><p class="small">A avaliação ainda não está aberta.</p></div>');return;}
  if(LS.get('avaliou',false)){
    h('<div class="card"><p class="kicker">Avaliação do VI Fórum</p><h3>Obrigado!</h3>'
     +'<p>Sua avaliação já foi registrada. Ela vai direto para quem monta o próximo Fórum.</p>'
     +((D.certificado&&D.certificado.liberado)?'<div class="btn-row"><a class="btn btn-teal btn-block btn-xl" href="#/certificado">Baixar meu certificado</a></div>':'')
     +'<div class="btn-row"><a class="btn btn-outline btn-sm" href="#/posevento">Ver como foi</a>'
     +'<button class="btn btn-light btn-sm" id="av-de-novo">Responder de novo</button></div></div>');
    document.getElementById('av-de-novo').onclick=function(){LS.set('avaliou',false);avaliacao();};
    return;
  }
  var rot=A.rotulos||['1','2','3','4','5'];
  function nota(it,max,rotulos){
    var o='';
    for(var i=1;i<=max;i++) o+='<button type="button" class="nt" data-q="'+esc(it.id)+'" data-v="'+i+'">'+i+'</button>';
    return '<div class="qa"><div class="qt">'+esc(it.q)+(it.sub?'<span>'+esc(it.sub)+'</span>':'')+'</div>'
          +'<div class="nts" data-grupo="'+esc(it.id)+'">'+o+'</div></div>';
  }
  function nps(it){
    var o='';
    for(var i=0;i<=10;i++) o+='<button type="button" class="nt nt-s" data-q="'+esc(it.id)+'" data-v="'+i+'">'+i+'</button>';
    return '<div class="qa"><div class="qt">'+esc(it.q)+'</div><div class="nts nts-w" data-grupo="'+esc(it.id)+'">'+o+'</div>'
          +'<div class="small muted" style="display:flex;justify-content:space-between;margin-top:4px"><span>0 · de jeito nenhum</span><span>10 · com certeza</span></div></div>';
  }
  function ops(b){
    var multi=b.tipo==='multi';
    return '<div class="ops" data-op="'+esc(b.id)+'" data-multi="'+(multi?1:0)+'">'
      +b.opcoes.map(function(o){return '<button type="button" class="op" data-v="'+esc(o)+'">'+esc(o)+'</button>';}).join('')+'</div>';
  }
  var corpo=A.blocos.map(function(b){
    var dentro='';
    if(b.tipo==='nota')      dentro=b.itens.map(function(it){return nota(it,5,rot);}).join('');
    else if(b.tipo==='nps')  dentro=b.itens.map(nps).join('');
    else                     dentro=ops(b);
    return '<section class="section"><div class="section-h"><h2>'+esc(b.t)+'</h2></div>'
      +(b.obs?'<p class="small muted" style="margin:-4px 2px 8px">'+esc(b.obs)+'</p>':'')
      +'<div class="card">'+dentro+'</div></section>';
  }).join('');

  h('<div class="card"><p class="kicker">VI Fórum · 20 de outubro de 2026</p><h3>'+esc(A.titulo)+'</h3>'
   +'<p class="small">'+esc(A.intro)+'</p>'
   +'<p class="small muted" style="margin-top:6px">Escala: <b>1</b> muito insatisfeito · <b>5</b> muito satisfeito.</p>'
   +'<div class="notice" style="margin-top:10px;border-color:#9fd3dc;background:#eef9fb">🔒 <b>Esta avaliação é anônima.</b> Não pedimos seu nome nem o CPF, e não temos como saber quem escreveu o quê. Pode ser sincero: é assim que a gente melhora.</div></div>'
   +corpo
   +'<section class="section"><div class="section-h"><h2>'+esc(A.comentario)+'</h2></div>'
   +'<div class="card"><div class="field"><textarea id="av-txt" rows="5" placeholder="'+esc(A.comentario_ph||'')+'"></textarea></div>'
   +'<button class="btn btn-teal btn-block btn-xl" id="av-env">Enviar minha avaliação</button>'
   +'<div id="av-msg"></div></div></section>');

  view.querySelectorAll('.nts .nt').forEach(function(b){
    b.onclick=function(){
      var g=b.parentNode;
      g.querySelectorAll('.nt').forEach(function(x){x.classList.remove('on');});
      b.classList.add('on');
    };
  });
  view.querySelectorAll('.ops .op').forEach(function(b){
    b.onclick=function(){
      var g=b.parentNode, multi=g.getAttribute('data-multi')==='1';
      if(!multi) g.querySelectorAll('.op').forEach(function(x){x.classList.remove('on');});
      b.classList.toggle('on');
    };
  });

  document.getElementById('av-env').onclick=function(){
    var notas={}, escolhas={};
    view.querySelectorAll('.nts').forEach(function(g){
      var on=g.querySelector('.nt.on');
      if(on) notas[g.getAttribute('data-grupo')]=parseInt(on.getAttribute('data-v'),10);
    });
    view.querySelectorAll('.ops').forEach(function(g){
      var sel=[].map.call(g.querySelectorAll('.op.on'),function(x){return x.getAttribute('data-v');});
      if(sel.length) escolhas[g.getAttribute('data-op')]= g.getAttribute('data-multi')==='1'?sel:sel[0];
    });
    var txt=(document.getElementById('av-txt').value||'').trim();
    var m=document.getElementById('av-msg');
    if(!Object.keys(notas).length && !Object.keys(escolhas).length && !txt){
      m.innerHTML='<div class="notice">Responda ao menos uma pergunta antes de enviar.</div>';return;
    }
    m.innerHTML='<p class="small muted">Enviando…</p>';
    fetch(API+'/avaliacao',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({id:devId(),notas:notas,escolhas:escolhas,comentario:txt})})
      .then(function(r){return r.json();})
      .then(function(){LS.set('avaliou',true);toast('Avaliação enviada. Obrigado!');avaliacao();window.scrollTo(0,0);})
      .catch(function(){m.innerHTML='<div class="notice">Não deu para enviar agora. Verifique a conexão e tente de novo.</div>';});
  };
}

function rotuloDe(id){
  var A=D.avaliacao||{};
  var achou=null;
  (A.blocos||[]).forEach(function(b){
    (b.itens||[]).forEach(function(it){ if(it.id===id) achou=it.q; });
    if(b.id===id) achou=b.t;
  });
  return achou||id;
}
function barra(v,max,cor){
  var pct=Math.round(v/max*100);
  return '<div style="height:7px;background:#e6ecf2;border-radius:99px;overflow:hidden;margin-top:5px">'
       +'<i style="display:block;height:100%;width:'+pct+'%;background:'+cor+'"></i></div>';
}
function resultados(){
  var pin=LS.get('painel_pin','');
  if(!pin){
    h('<div class="card"><p class="kicker">Equipe ACATMAR</p><h3>Resultados da avaliação</h3>'
     +'<p class="small muted">Área da organização. Digite o PIN do painel.</p>'
     +'<form id="f-rp"><div class="field"><label>PIN</label><input name="pin" type="password" inputmode="numeric" required></div>'
     +'<button class="btn btn-navy btn-block" type="submit">Entrar</button></form></div>');
    document.getElementById('f-rp').onsubmit=function(ev){ev.preventDefault();
      LS.set('painel_pin',ev.target.pin.value.trim());resultados();};
    return;
  }
  h('<div class="card"><p class="small muted">Carregando as respostas…</p></div>');
  fetch(API+'/avaliacoes?pin='+encodeURIComponent(pin)).then(function(r){
    if(r.status===401){LS.set('painel_pin','');throw new Error('pin');}
    return r.json();
  }).then(function(d){
    if(!d.total){h('<div class="card"><h3>Resultados da avaliação</h3><p class="small">Ninguém respondeu ainda.</p></div>');return;}
    var ord=Object.keys(d.medias||{}).sort(function(a,b){return d.medias[b].media-d.medias[a].media;});
    var nps=d.medias&&d.medias.nps;
    var notas=ord.filter(function(k){return k!=='nps';}).map(function(k){
      var m=d.medias[k];
      return '<div class="qa"><div class="qt" style="margin-bottom:4px">'+esc(rotuloDe(k))
        +'<span>'+m.media.toFixed(1).replace('.',',')+' de 5 · '+m.respostas+' resposta'+(m.respostas>1?'s':'')+'</span></div>'
        +barra(m.media,5,'var(--teal,#00727e)')+'</div>';
    }).join('');
    var escolhas=Object.keys(d.contagens||{}).map(function(k){
      var c=d.contagens[k];
      var itens=Object.keys(c).sort(function(a,b){return c[b]-c[a];});
      var topo=itens.length?c[itens[0]]:1;
      return '<section class="section"><div class="section-h"><h2>'+esc(rotuloDe(k))+'</h2></div><div class="card">'
        +itens.map(function(o){
          return '<div class="qa"><div class="qt" style="margin-bottom:4px;font-weight:500">'+esc(o)
                +'<span>'+c[o]+'</span></div>'+barra(c[o],topo,'var(--navy,#0a2540)')+'</div>';
        }).join('')+'</div></section>';
    }).join('');
    var coment=(d.comentarios||[]).map(function(c){
      return '<div class="card" style="padding:12px 14px"><p class="small">'+esc(c.texto)+'</p>'
        +'<p class="small muted" style="margin-top:6px">'+esc(c.nome||'Anônimo')+' · '+esc((c.quando||'').slice(0,10).split('-').reverse().join('/'))+'</p></div>';
    }).join('');
    h('<div class="card"><p class="kicker">Equipe ACATMAR</p><h3>'+d.total+' avaliaç'+(d.total>1?'ões':'ão')+' recebida'+(d.total>1?'s':'')+'</h3>'
      +(nps?'<p class="small">Nota média de recomendação (0 a 10): <b>'+nps.media.toFixed(1).replace('.',',')+'</b></p>':'')
      +'<div class="btn-row"><button class="btn btn-outline btn-sm" id="rp-rec">Atualizar</button>'
      +'<button class="btn btn-light btn-sm" id="rp-sair">Sair</button></div></div>'
      +(notas?'<section class="section"><div class="section-h"><h2>Notas, da maior para a menor</h2></div><div class="card">'+notas+'</div></section>':'')
      +escolhas
      +(coment?'<section class="section"><div class="section-h"><h2>Comentários</h2></div>'+coment+'</section>':''));
    document.getElementById('rp-rec').onclick=function(){resultados();};
    document.getElementById('rp-sair').onclick=function(){LS.set('painel_pin','');resultados();};
  }).catch(function(){
    h('<div class="card"><p class="small">Não foi possível carregar. Confira o PIN e a conexão.</p>'
     +'<div class="btn-row"><button class="btn btn-navy btn-sm" id="rp-t">Tentar de novo</button></div></div>');
    var b=document.getElementById('rp-t'); if(b)b.onclick=function(){resultados();};
  });
}

function faq(){h(D.faq.map(function(q){return '<details><summary>'+esc(q.p)+'</summary><p>'+esc(q.r)+'</p></details>';}).join(''));}
function mais(){var POS=status()==='depois';var me=LS.get('me',null);
  h('<a class="card" href="#/credencial" style="display:flex;gap:12px;align-items:center;text-decoration:none;color:inherit"><div class="spk"><div class="av">'+esc(me?me.nome.split(' ').map(function(w){return w[0];}).slice(0,2).join(''):'?')+'</div><div><b>'+esc(me?me.nome:'Crie sua credencial')+'</b><span>'+esc(me?[me.cargo,me.empresa].filter(Boolean).join(' · ')||(me.tipo||''):'Toque para criar seu QR Code')+'</span></div></div><span style="margin-left:auto;font-size:1.6rem;color:#aab7bf">›</span></a>'
   +(POS?'<div class="menu"><a href="#/posevento"><i>📸</i>VI Fórum: como foi</a><a href="#/certificado"><i>📜</i>Certificado</a><a href="#/avaliacao"><i>⭐</i>Avaliar o Fórum</a><a href="#/programacao"><i>🗓️</i>O que teve na programação</a><a href="#/palestrantes"><i>🎤</i>Palestrantes</a><a href="#/patrocinadores"><i>🤝</i>Quem fez acontecer</a>':'<div class="menu"><a href="#/posevento"><i>📸</i>VI Fórum: como foi</a><a href="#/diario"><i>🎯</i>Fórum todo dia · quiz e enquete</a><a href="#/palestrantes"><i>🎤</i>Palestrantes</a><a href="#/patrocinadores"><i>🤝</i>Patrocinadores e apoio</a><a href="#/local"><i>📍</i>Local e como chegar</a><a href="#/interagir"><i>💬</i>Interagir e perguntar</a><a href="#/certificado"><i>📜</i>Certificado</a>')+'<a href="#/edicoes"><i>📷</i>Todas as edições ('+anosEdicoes()+')</a><a href="#/sobre"><i>⚓</i>Sobre o Fórum</a><a href="#/faq"><i>❓</i>Perguntas frequentes</a><a href="#/instalar"><i>📲</i>Instalar o app</a></div>'
   +(POS?'':'<div class="menu"><a href="#/credenciamento"><i>📷</i>Credenciamento (equipe ACATMAR)</a><a href="#/controle"><i>📊</i>Controle do app (equipe ACATMAR)</a><a href="#/resultados"><i>📈</i>Resultados da avaliação (equipe)</a></div>')
   +'<div class="menu">'+(POS?'':'<a href="#/inscricao"><i>📝</i>Inscrição gratuita</a>')+'<a href="https://www.acatmar.org/" target="_blank" rel="noopener"><i>🌐</i>Site da ACATMAR</a><a href="https://www.acatmar.org/privacidade.html" target="_blank" rel="noopener"><i>🔒</i>Política de Privacidade</a></div>'
   +'<p class="small muted" style="text-align:center">Sua credencial fica salva neste aparelho. Nome, empresa e contato também ficam com a organização do Fórum.<br>App oficial · ACATMAR · conteúdo '+esc(D.versao)+' · app v'+APP_V+'</p>');}

/* ---------- Controle do app (equipe) ---------- */
function controle(){
  var pin=LS.get('painel_pin','');
  if(!pin){
    h('<div class="card"><p class="kicker">Equipe ACATMAR</p><h3>Controle do app</h3><p class="small muted">Quantas pessoas instalaram e usam o app do Fórum, e quem são. Digite o PIN do painel.</p><form id="f-cpin"><div class="field"><label>PIN do painel</label><input name="pin" type="password" inputmode="numeric" required></div><button class="btn btn-navy btn-block" type="submit">Entrar</button></form></div>');
    document.getElementById('f-cpin').onsubmit=function(ev){ev.preventDefault();LS.set('painel_pin',ev.target.pin.value.trim());controle();};
    return;
  }
  h('<div class="card"><p class="small muted" style="margin:0">Carregando os dados...</p></div>');
  fetch(API+'/resumo?pin='+encodeURIComponent(pin),{cache:'no-store'}).then(function(r){
    if(r.status===403){LS.set('painel_pin','');toast('PIN incorreto');controle();return null;}
    return r.json();
  }).then(function(j){
    if(!j)return;
    var l=j.lista||[];
    var linhas=l.map(function(r){
      var quando=(r.primeiro||'').slice(0,10).split('-').reverse().join('/');
      var sub=[r.cargo,r.empresa].filter(Boolean).join(' · ')||r.tipo||'sem identificação';
      var marcas=[r.instalado?'instalado':'navegador',r.plataforma,r.cidade].filter(Boolean).join(' · ');
      return '<div class="card" style="padding:12px"><b>'+esc(r.nome||'(não identificado)')+'</b><div class="small muted">'+esc(sub)+'</div><div class="small muted">'+esc(marcas)+' · '+esc(quando)+' · '+r.aberturas+(r.aberturas===1?' abertura':' aberturas')+'</div>'+((r.email||r.fone)?'<div class="small">'+esc([r.email,r.fone].filter(Boolean).join(' · '))+'</div>':'')+'</div>';
    }).join('');
    h('<div class="kpis" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px">'
      +'<div class="card" style="text-align:center;padding:14px 6px"><b style="font-size:1.7rem;display:block">'+j.total+'</b><span class="small muted">aparelhos</span></div>'
      +'<div class="card" style="text-align:center;padding:14px 6px"><b style="font-size:1.7rem;display:block">'+j.instalados+'</b><span class="small muted">instalados</span></div>'
      +'<div class="card" style="text-align:center;padding:14px 6px"><b style="font-size:1.7rem;display:block">'+j.identificados+'</b><span class="small muted">identificados</span></div></div>'
      +'<div class="btn-row" style="margin:12px 0"><a class="btn btn-teal btn-sm" href="'+API+'/csv?pin='+encodeURIComponent(pin)+'" target="_blank" rel="noopener">Baixar planilha</a><button class="btn btn-outline btn-sm" id="c-reload">Atualizar</button><button class="btn btn-outline btn-sm" id="c-sair">Sair</button></div>'
      +'<div class="section-h"><h2>Quem está no app</h2></div>'
      +(linhas||'<div class="card"><p class="small muted" style="margin:0">Ninguém registrado ainda.</p></div>')
      +'<p class="small muted" style="text-align:center;margin-top:14px">"Aparelhos" conta celulares e navegadores diferentes. "Instalados" são os que adicionaram o app à tela inicial. Quem ainda não criou a credencial aparece sem nome.</p>');
    document.getElementById('c-reload').onclick=function(){controle();};
    document.getElementById('c-sair').onclick=function(){LS.set('painel_pin','');controle();};
  }).catch(function(){h('<div class="card"><p class="small">Não foi possível carregar agora. Verifique a conexão e tente de novo.</p><div class="btn-row"><button class="btn btn-navy btn-sm" id="c-retry">Tentar de novo</button></div></div>');var b=document.getElementById('c-retry');if(b)b.onclick=function(){controle();};});
}

/* ---------- Credenciamento (equipe) ---------- */
var scan={stream:null,raf:null,last:'',lastT:0};
function stopScan(){if(scan.raf)cancelAnimationFrame(scan.raf);scan.raf=null;if(scan.stream){scan.stream.getTracks().forEach(function(t){t.stop();});scan.stream=null;}}
window.addEventListener('hashchange',stopScan);
function parseVCard(t){var o={raw:t};if(!/BEGIN:VCARD/i.test(t))return o;t.split(/\r?\n/).forEach(function(l){var i=l.indexOf(':');if(i<0)return;var k=l.slice(0,i).split(';')[0].toUpperCase(),v=l.slice(i+1);if(k==='FN')o.nome=v;else if(k==='ORG')o.empresa=v;else if(k==='TITLE')o.cargo=v;else if(k==='EMAIL')o.email=v;else if(k==='TEL')o.fone=v;else if(k==='NOTE'&&/TIPO=/.test(v))o.tipo=v.split('TIPO=')[1];});return o;}
function credenciamento(){
  if(LS.get('staff',false)!==D.credenciamento_pin){
    h('<div class="card"><p class="kicker">Equipe ACATMAR</p><h3>Credenciamento</h3><p class="small muted">Área da organização. Digite o PIN da equipe para ler os QR Codes dos participantes na entrada.</p><form id="f-pin"><div class="field"><label>PIN</label><input name="pin" type="password" inputmode="numeric" required></div><button class="btn btn-navy btn-block" type="submit">Entrar</button></form></div>');
    document.getElementById('f-pin').onsubmit=function(ev){ev.preventDefault();var v=ev.target.pin.value.trim();if(v===String(D.credenciamento_pin)){LS.set('staff',v);credenciamento();}else toast('PIN incorreto');};
    return;
  }
  var lista=LS.get('checkins',[]);
  h('<div class="card" style="padding:10px"><div id="cam" style="position:relative;background:#000;border-radius:12px;overflow:hidden;aspect-ratio:1/1"><video id="vid" playsinline muted style="width:100%;height:100%;object-fit:cover"></video><div style="position:absolute;inset:12%;border:3px solid rgba(53,201,218,.9);border-radius:16px;box-shadow:0 0 0 999px rgba(0,0,0,.35)"></div><div id="cam-msg" style="position:absolute;left:0;right:0;bottom:0;padding:10px;color:#fff;text-align:center;font-size:.85rem;background:linear-gradient(transparent,rgba(0,0,0,.7))">Aponte a câmera para o QR Code do participante</div></div><div class="btn-row"><button class="btn btn-teal btn-sm" id="btn-cam">Ligar câmera</button><button class="btn btn-outline btn-sm" id="btn-manual">Registrar sem QR</button></div></div>'
   +'<label class="check" style="margin:10px 2px 6px"><input type="checkbox" id="auto-print"'+(LS.get('auto_print',false)?' checked':'')+'> Imprimir etiqueta automaticamente a cada leitura</label>'
   +'<div id="result"></div>'
   +'<div class="section-h" style="margin-top:16px"><h2>Credenciados <span class="tag">'+lista.length+'</span></h2><a href="#" id="btn-export">Exportar</a></div><div id="lista">'+listaHtml(lista)+'</div>'
   +'<p class="small muted" style="text-align:center;margin-top:14px">A lista fica salva neste aparelho. Use "Exportar" para enviar ao WhatsApp/e-mail da organização.</p>');
  document.getElementById('btn-cam').onclick=startScan;bindPrints();
  document.getElementById('auto-print').onchange=function(){LS.set('auto_print',this.checked);};
  document.getElementById('btn-manual').onclick=function(){registrar({nome:prompt('Nome do participante:')||''},true);};
  document.getElementById('btn-export').onclick=function(ev){ev.preventDefault();var l=LS.get('checkins',[]);var csv='hora;nome;empresa;cargo;email;fone\n'+l.map(function(c){return [c.hora,c.nome,c.empresa||'',c.cargo||'',c.email||'',c.fone||''].map(function(x){return String(x).replace(/;/g,',');}).join(';');}).join('\n');share('Credenciados '+D.evento.curto,csv);};
  if(scan.stream===null&&LS.get('cam_auto',false))startScan();
}
function listaHtml(l){if(!l.length)return '<div class="card"><p class="small muted">Ninguém credenciado ainda.</p></div>';return l.slice().reverse().slice(0,50).map(function(c){return '<div class="card spk" style="padding:10px 14px"><div class="av" style="flex-basis:40px;height:40px;font-size:.95rem">'+esc((c.nome||'?').split(' ').map(function(w){return w[0];}).slice(0,2).join(''))+'</div><div><b>'+esc(c.nome)+'</b><span>'+esc([c.cargo,c.empresa].filter(Boolean).join(' · '))+'</span></div><span class="small muted" style="margin-left:auto">'+esc(c.hora.slice(11,16))+'</span><button class="fav" data-print="'+esc(c.hora)+'" aria-label="Imprimir etiqueta" style="font-size:1.3rem;color:var(--navy)">🖨️</button></div>';}).join('');}
function bindPrints(){view.querySelectorAll('[data-print]').forEach(function(b){b.onclick=function(){var l=LS.get('checkins',[]);var c=null;l.forEach(function(x){if(x.hora===b.getAttribute('data-print'))c=x;});if(c)imprimirEtiqueta(c);};});}
function registrar(p,manual){
  if(!p.nome){toast('QR sem nome');return;}
  var l=LS.get('checkins',[]);var key=(p.nome+'|'+(p.email||'')).toLowerCase();var dup=l.some(function(c){return (c.nome+'|'+(c.email||'')).toLowerCase()===key;});
  var r=document.getElementById('result');
  if(dup){var ex=null;l.forEach(function(c){if((c.nome+'|'+(c.email||'')).toLowerCase()===key)ex=c;});r.innerHTML='<div class="notice" style="border-color:#f2b54a;background:#fff3d6">⚠️ <b>'+esc(p.nome)+'</b> já foi credenciado(a).<div class="btn-row"><button class="btn btn-outline btn-sm" id="btn-reprint">🖨️ Reimprimir etiqueta</button></div></div>';document.getElementById('btn-reprint').onclick=function(){imprimirEtiqueta(ex);};if(navigator.vibrate)navigator.vibrate([80,60,80]);return;}
  var now=new Date();var c={nome:p.nome,empresa:p.empresa||'',cargo:p.cargo||'',email:p.email||'',fone:p.fone||'',tipo:p.tipo||'Participante',hora:new Date(now-now.getTimezoneOffset()*6e4).toISOString().slice(0,19),manual:!!manual};
  l.push(c);LS.set('checkins',l);
  r.innerHTML='<div class="ok-box" style="text-align:left">✅ <b>'+esc(c.nome)+'</b><br><span class="small">'+esc([c.cargo,c.empresa].filter(Boolean).join(' · '))+'</span><div class="btn-row"><button class="btn btn-navy btn-sm" id="btn-print">🖨️ Imprimir etiqueta</button></div></div>';
  document.getElementById('btn-print').onclick=function(){imprimirEtiqueta(c);};
  if(navigator.vibrate)navigator.vibrate(120);
  if(LS.get('auto_print',false)){imprimirEtiqueta._auto=true;imprimirEtiqueta(c);}
  document.getElementById('lista').innerHTML=listaHtml(l);document.querySelector('.section-h .tag').textContent=l.length;bindPrints();
}
function imprimirEtiqueta(c){
  var et=D.etiqueta||{largura_mm:90,altura_mm:62};var W=et.largura_mm,H=et.altura_mm;
  var vc='BEGIN:VCARD\nVERSION:3.0\nFN:'+c.nome+(c.empresa?'\nORG:'+c.empresa:'')+(c.cargo?'\nTITLE:'+c.cargo:'')+(c.email?'\nEMAIL:'+c.email:'')+'\nEND:VCARD';
  var tmp=document.createElement('div');var qrData='';
  try{new QRCode(tmp,{text:vc.normalize('NFD').replace(/[̀-ͯ]/g,''),width:120,height:120,correctLevel:QRCode.CorrectLevel.L});var cv=tmp.querySelector('canvas');qrData=cv?cv.toDataURL():'';}catch(x){}
  var fs=c.nome.length>26?'5.2mm':(c.nome.length>18?'6.5mm':'8mm');
  var old=document.getElementById('et-overlay');if(old)old.remove();
  var ov=document.createElement('div');ov.id='et-overlay';
  ov.innerHTML='<style id="et-style">#et-overlay{position:fixed;inset:0;z-index:200;background:rgba(6,23,38,.92);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;padding:16px}#et-overlay .et{box-sizing:border-box;width:'+W+'mm;height:'+H+'mm;max-width:100%;padding:4mm 5mm;display:flex;flex-direction:column;justify-content:space-between;background:#fff;color:#0a2540;font-family:Helvetica,Arial,sans-serif;border-radius:6px;box-shadow:0 10px 30px rgba(0,0,0,.5)}#et-overlay .top{display:flex;justify-content:space-between;align-items:center;font-size:2.6mm;letter-spacing:.3mm;text-transform:uppercase;font-weight:700;border-bottom:.5mm solid #0a2540;padding-bottom:1.5mm}#et-overlay .top span{color:#00727e}#et-overlay .mid{display:flex;align-items:center;gap:3mm;flex:1}#et-overlay .nome{font-size:'+fs+';font-weight:800;line-height:1.05;text-transform:uppercase;word-break:break-word}#et-overlay .sub{font-size:3.4mm;margin-top:1.5mm;color:#334}#et-overlay .qr{flex:0 0 18mm;width:18mm;height:18mm}#et-overlay .qr img{width:100%;height:100%}#et-overlay .bot{display:flex;justify-content:space-between;align-items:center;gap:3mm;font-size:2.5mm;color:#556;text-transform:uppercase;letter-spacing:.2mm}#et-overlay .loc{flex:1;text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}#et-overlay .tipo{flex:0 0 auto;background:#0a2540;color:#fff;padding:.6mm 2mm;border-radius:1mm;font-weight:700}#et-overlay .bar{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}#et-overlay .hint{color:#fff;opacity:.75;font-size:.8rem;text-align:center;max-width:320px}@media print{@page{size:'+W+'mm '+H+'mm;margin:0}html,body{position:static!important;overflow:visible!important;height:auto!important;background:#fff!important}body>*:not(#et-overlay){display:none!important}#et-overlay{position:static;background:#fff;padding:0;display:block}#et-overlay .et{margin:0;border-radius:0;box-shadow:none;width:'+W+'mm;height:'+H+'mm}#et-overlay .bar,#et-overlay .hint{display:none!important}}</style>'
   +'<div class="et"><div class="top"><div>'+esc(D.evento.curto)+'</div><span>'+esc(D.evento.data_iso.split('-').reverse().join('/'))+'</span></div><div class="mid"><div style="flex:1;min-width:0"><div class="nome">'+esc(c.nome)+'</div><div class="sub">'+esc([c.cargo,c.empresa].filter(Boolean).join(' · '))+'</div></div>'+(qrData?'<div class="qr"><img src="'+qrData+'"></div>':'')+'</div><div class="bot"><span class="tipo">'+esc(c.tipo||'Participante')+'</span><span class="loc">IFSC Florianópolis-Continente</span></div></div>'
   +'<div class="bar"><button class="btn btn-teal" id="et-print">🖨️ Imprimir etiqueta</button><button class="btn btn-light" id="et-close">Fechar</button></div><div class="hint">Na caixa de impressão, escolha a impressora de etiquetas. Se não aparecer, confira se ela está na mesma rede Wi-Fi.</div>';
  document.body.appendChild(ov);
  document.getElementById('et-close').onclick=function(){ov.remove();};
  var usaPDF=isStandalone()||isIOS();
  if(usaPDF){document.getElementById('et-print').textContent='🖨️ Imprimir / salvar etiqueta';document.querySelector('#et-overlay .hint').textContent='Vai abrir o menu do iPhone: escolha "Imprimir" para mandar à impressora, ou salve/compartilhe o PDF.';}
  document.getElementById('et-print').onclick=function(){if(usaPDF)etiquetaPDF(c,qrData,W,H);else window.print();};
  if(LS.get('auto_print',false)&&imprimirEtiqueta._auto){setTimeout(function(){if(usaPDF)etiquetaPDF(c,qrData,W,H);else window.print();},400);}
  imprimirEtiqueta._auto=false;
}
function etiquetaPDF(c,qrData,W,H){
  function go(){
    var doc=new window.jspdf.jsPDF({orientation:W>=H?'landscape':'portrait',unit:'mm',format:[W,H]});
    var pad=5;doc.setTextColor(10,37,64);doc.setFont('helvetica','bold');doc.setFontSize(7);
    doc.text(D.evento.curto.toUpperCase(),pad,pad+2);doc.setTextColor(0,114,126);doc.text(D.evento.data_iso.split('-').reverse().join('/'),W-pad,pad+2,{align:'right'});
    doc.setDrawColor(10,37,64);doc.setLineWidth(.5);doc.line(pad,pad+4,W-pad,pad+4);
    var qrS=18,textW=W-pad*2-(qrData?qrS+3:0);
    doc.setTextColor(10,37,64);var fs=c.nome.length>26?15:(c.nome.length>18?19:23);doc.setFontSize(fs);
    var lines=doc.splitTextToSize(c.nome.toUpperCase(),textW);var y=H/2-(lines.length*fs*0.42)/2+2;
    doc.text(lines,pad,y);
    var sub=[c.cargo,c.empresa].filter(Boolean).join(' · ');if(sub){doc.setFont('helvetica','normal');doc.setFontSize(9.5);doc.setTextColor(51,51,68);doc.text(doc.splitTextToSize(sub,textW),pad,y+lines.length*fs*0.42+2);}
    if(qrData)doc.addImage(qrData,'PNG',W-pad-qrS,H/2-qrS/2-1,qrS,qrS);
    doc.setFont('helvetica','bold');doc.setFontSize(7);var tipoTxt=(c.tipo||'Participante').toUpperCase();var tw=doc.getTextWidth(tipoTxt)+5;
    doc.setFillColor(10,37,64);doc.roundedRect(pad,H-pad-5,tw,5,1,1,'F');doc.setTextColor(255,255,255);doc.text(tipoTxt,pad+2.5,H-pad-1.5);
    doc.setTextColor(85,85,102);doc.setFont('helvetica','normal');doc.text('IFSC FLORIANÓPOLIS-CONTINENTE',W-pad,H-pad-1.5,{align:'right'});
    var blob=doc.output('blob');var nome='etiqueta-'+c.nome.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-')+'.pdf';
    var file=null;try{file=new File([blob],nome,{type:'application/pdf'});}catch(x){}
    if(file&&navigator.canShare&&navigator.canShare({files:[file]})){navigator.share({files:[file],title:'Etiqueta '+c.nome}).catch(function(){});}
    else{var u=URL.createObjectURL(blob);var a=document.createElement('a');a.href=u;a.download=nome;a.target='_blank';document.body.appendChild(a);a.click();a.remove();}
  }
  if(window.jspdf)go();else{var sc=document.createElement('script');sc.src='lib/jspdf.umd.min.js';sc.onload=go;sc.onerror=function(){toast('Não foi possível carregar o gerador de PDF.');};document.body.appendChild(sc);}
}
function startScan(){
  var vid=document.getElementById('vid'),msg=document.getElementById('cam-msg');if(!vid)return;
  if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){msg.textContent='Este navegador não dá acesso à câmera. Abra pelo Safari (iPhone) ou Chrome (Android).';return;}
  navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'},width:{ideal:1280},height:{ideal:1280}},audio:false}).then(function(st){
    scan.stream=st;vid.srcObject=st;vid.play();LS.set('cam_auto',true);msg.textContent='Lendo… aproxime o QR Code';
    var det=('BarcodeDetector' in window)?new BarcodeDetector({formats:['qr_code']}):null;
    var cv=document.createElement('canvas'),cx=cv.getContext('2d',{willReadFrequently:true});
    function tick(){
      if(!scan.stream)return;
      if(vid.readyState>=2){
        if(det){det.detect(vid).then(function(codes){if(codes.length)onCode(codes[0].rawValue);}).catch(function(){});}
        else if(window.jsQR){var w=Math.min(640,vid.videoWidth),hh=Math.round(w*vid.videoHeight/vid.videoWidth);cv.width=w;cv.height=hh;cx.drawImage(vid,0,0,w,hh);var im=cx.getImageData(0,0,w,hh);var code=jsQR(im.data,w,hh,{inversionAttempts:'dontInvert'});if(code&&code.data)onCode(code.data);}
      }
      scan.raf=requestAnimationFrame(tick);
    }
    if(!('BarcodeDetector' in window)&&!window.jsQR){var sc=document.createElement('script');sc.src='lib/jsQR.min.js';sc.onload=tick;document.body.appendChild(sc);}else tick();
  }).catch(function(){msg.textContent='Sem permissão para a câmera. Permita o acesso nos ajustes do navegador e tente de novo.';});
}
function onCode(txt){var t=Date.now();if(txt===scan.last&&t-scan.lastT<4000)return;scan.last=txt;scan.lastT=t;registrar(parseVCard(txt));}

/* ---------- Inscrição (dentro do app) ---------- */
/* CPF obrigatorio e CNPJ opcional: mascara e validacao dos digitos verificadores */
function soDigitos(v){return String(v||'').replace(/\D/g,'');}
function mascaraCPF(v){v=soDigitos(v).slice(0,11);return v.replace(/(\d{3})(\d)/,'$1.$2').replace(/(\d{3})(\d)/,'$1.$2').replace(/(\d{3})(\d{1,2})$/,'$1-$2');}
function mascaraCNPJ(v){v=soDigitos(v).slice(0,14);return v.replace(/^(\d{2})(\d)/,'$1.$2').replace(/^(\d{2})\.(\d{3})(\d)/,'$1.$2.$3').replace(/\.(\d{3})(\d)/,'.$1/$2').replace(/(\d{4})(\d)/,'$1-$2');}
function validaCPF(c){c=soDigitos(c);if(c.length!==11||/^(\d)\1+$/.test(c))return false;for(var t=9;t<11;t++){var s=0;for(var i=0;i<t;i++)s+=c[i]*(t+1-i);if(((s*10)%11)%10!=c[t])return false;}return true;}
function validaCNPJ(c){c=soDigitos(c);if(c.length!==14||/^(\d)\1+$/.test(c))return false;var p=[5,4,3,2,9,8,7,6,5,4,3,2];for(var t=12;t<14;t++){var w=t===12?p:[6].concat(p);var s=0;for(var i=0;i<t;i++)s+=c[i]*w[i];var d=s%11<2?0:11-s%11;if(d!=c[t])return false;}return true;}
function inscricao(){
  var e=D.evento,me=LS.get('me',{})||{},ins=LS.get('inscrito',null);
  if(ins){h('<div class="ok-box" style="text-align:left"><div style="font-size:1.6rem">⚓</div><b>Inscrição enviada!</b><p class="small" style="margin:6px 0 0">'+esc(ins.nome)+', sua inscrição foi recebida em '+esc(ins.quando)+'. A programação e os avisos chegam aqui no app e no seu e-mail e WhatsApp.</p></div><div class="btn-row"><a class="btn btn-teal" href="#/credencial">Criar minha credencial</a><a class="btn btn-outline btn-sm" href="#/programacao">Ver programação</a></div><p class="small muted" style="margin-top:14px">Precisa corrigir algo? <a href="#" id="ins-again">Enviar de novo</a>.</p>');
    document.getElementById('ins-again').onclick=function(ev){ev.preventDefault();LS.set('inscrito',null);inscricao();};return;}
  h('<div class="card"><p class="kicker">'+esc(e.data_texto)+'</p><h3>Inscrição gratuita</h3><p class="small muted">Vagas limitadas. Preencha e você recebe a programação e os avisos em primeira mão.</p><form id="f-ins"><input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off"><input type="hidden" name="_subject" value="Inscrição — VI Fórum de Capacitação Técnica ACATMAR (out/2026)"><input type="hidden" name="_template" value="table"><input type="hidden" name="_captcha" value="false"><input type="hidden" name="Origem" value="Inscrição VI Fórum ACATMAR 2026 (pelo app)"><div class="field"><label>Nome completo</label><input name="Nome" required autocomplete="name" value="'+esc(me.nome||'')+'"></div><div class="field"><label>E-mail</label><input name="email" type="email" required autocomplete="email" value="'+esc(me.email||'')+'"></div><div class="field"><label>WhatsApp</label><input name="WhatsApp" type="tel" required autocomplete="tel" placeholder="(48) 99999-9999" value="'+esc(me.fone||'')+'"></div><div class="field"><label>CPF</label><input name="CPF" id="ins-cpf" required inputmode="numeric" maxlength="14" autocomplete="off" placeholder="000.000.000-00"><p class="small muted" style="margin:4px 0 0">Usado para a sua inscrição, o certificado e a organização do Fórum.</p></div><div class="field"><label>Empresa ou instituição (opcional)</label><input name="Empresa" autocomplete="organization" value="'+esc(me.empresa||'')+'"></div><div class="field"><label>CNPJ da empresa (opcional)</label><input name="CNPJ" id="ins-cnpj" inputmode="numeric" maxlength="18" autocomplete="off" placeholder="00.000.000/0000-00"></div><label class="check"><input type="checkbox" required> Autorizo o contato sobre o VI Fórum por e-mail e WhatsApp, conforme a <a href="https://www.acatmar.org/privacidade.html" target="_blank" rel="noopener">Política de Privacidade</a>.</label><button class="btn btn-teal btn-block btn-xl" type="submit">Quero me inscrever</button></form></div>');
  var cpfEl=document.getElementById('ins-cpf'),cnpjEl=document.getElementById('ins-cnpj');
  cpfEl.oninput=function(){this.value=mascaraCPF(this.value);};cnpjEl.oninput=function(){this.value=mascaraCNPJ(this.value);};
  document.getElementById('f-ins').onsubmit=function(ev){ev.preventDefault();var f=ev.target;var btn=f.querySelector('button');
    if(!validaCPF(cpfEl.value)){toast('CPF inválido. Confira os números.');cpfEl.focus();return;}
    if(soDigitos(cnpjEl.value)&&!validaCNPJ(cnpjEl.value)){toast('CNPJ inválido. Confira ou deixe em branco.');cnpjEl.focus();return;}
    btn.disabled=true;btn.textContent='Enviando…';var fd=new FormData(f);
    fetch(e.formsubmit,{method:'POST',headers:{'Accept':'application/json'},body:fd}).then(function(r){return r.json();}).then(function(j){if(!(j&&(j.success==='true'||j.success===true)))throw 0;
      var now=new Date();LS.set('inscrito',{nome:String(fd.get('Nome')).trim(),quando:now.toLocaleDateString('pt-BR')+' às '+now.toLocaleTimeString('pt-BR').slice(0,5)});
      if(!LS.get('me',null))LS.set('me',{nome:String(fd.get('Nome')).trim(),email:String(fd.get('email')).trim(),fone:String(fd.get('WhatsApp')).trim(),empresa:String(fd.get('Empresa')||'').trim(),cargo:'',tipo:'Participante'});
      inscricao();toast('Inscrição enviada!');}).catch(function(){btn.disabled=false;btn.textContent='Tentar de novo';toast('Não foi possível enviar. Verifique a conexão ou escreva para '+e.email);});};
}

/* ---------- Edições anteriores ---------- */
function edicoes(){
  var eds=(D.edicoes||[]).slice().reverse();
  h('<p class="small muted" style="margin:0 0 14px">'+numEdicoes()+', de '+anosEdicoes()+'. Toque nas fotos para ampliar.</p>'
   +eds.map(function(e){return '<div class="card ed"><img class="ed-capa" src="'+e.capa+'" alt="" loading="lazy"><div class="ed-b"><p class="kicker">'+e.ed+' Fórum · '+e.ano+'</p><h3>'+esc(e.tema)+'</h3><p class="small muted" style="margin:0 0 8px">'+esc(e.data)+' · '+esc(e.onde)+'</p><p class="small">'+esc(e.resumo)+'</p></div><div class="gal gal-sm">'+e.fotos.map(function(f){return '<img src="'+f+'" alt="" loading="lazy" data-zoom="'+f+'">';}).join('')+'</div>'+(e.link?'<div class="btn-row"><a class="btn btn-outline btn-sm" href="'+e.link+'" target="_blank" rel="noopener">Matéria completa no site</a></div>':'')+'</div>';}).join(''));
  view.querySelectorAll('[data-zoom]').forEach(function(im){im.onclick=function(){var ov=document.createElement('div');ov.className='zoom-ov';ov.innerHTML='<img src="'+im.getAttribute('data-zoom')+'" alt="">';ov.onclick=function(){ov.remove();};document.body.appendChild(ov);};});
}

/* ---------- Fórum todo dia (quiz + enquete + contagem) ---------- */
function diaDiario(){var base=(D.diario&&D.diario.base)||D.evento.data_iso;var b=new Date(base+'T00:00:00-03:00');var n=Math.floor((Date.now()-b.getTime())/864e5);return n<0?0:n;}
function diarioHomeCard(st,d){
  if(st==='depois'||!D.diario||!(D.diario.quiz||D.diario.enquetes))return '';
  var diasEv=Math.ceil((d.start-new Date())/864e5);
  var selo=(st==='agora'||diasEv<=0)?'é hoje!':('faltam '+diasEv+' dia'+(diasEv>1?'s':''));
  var q=D.diario.quiz&&D.diario.quiz.length?D.diario.quiz[diaDiario()%D.diario.quiz.length]:null;
  return '<section class="section"><a class="card card-dia" href="#/diario"><div class="card-dia-h"><span class="kicker">Fórum todo dia</span><span class="card-dia-cd">'+selo+'</span></div><h3>Quiz do dia, enquete e novidades</h3>'+(q?'<p class="small card-dia-q">Hoje: '+esc(q.pergunta)+'</p>':'<p class="small">Responda o quiz do dia e diga o que quer que os palestrantes abordem.</p>')+'<span class="card-dia-go">Participar ›</span></a></section>';
}
function diario(){
  var dd=D.diario||{};var quiz=dd.quiz||[],enqs=dd.enquetes||[];var di=diaDiario();
  var ps=D.palestrantes||[];var byId={};ps.forEach(function(p){byId[p.id]=p;});
  var st=status();var ev=eventDate();var diasEv=Math.ceil((ev.start-new Date())/864e5);
  var cd=st==='agora'?'<b>Hoje!</b> O Fórum é agora':(st==='depois'?'O Fórum já aconteceu. Obrigado!':(diasEv<=0?'<b>É hoje!</b>':'Faltam <b>'+diasEv+'</b> dia'+(diasEv>1?'s':'')+' para o Fórum'));
  var pdia=ps.length?ps[di%ps.length]:null;
  var destaque=pdia?'<div class="dia-spk"><div class="av">'+(pdia.foto?'<img src="'+pdia.foto+'" alt="">':esc((pdia.nome||'?')[0]))+'</div><div><span class="small muted">Palestra em destaque'+(pdia.hora?' · '+esc(pdia.hora):'')+'</span><b>'+esc(pdia.tema||pdia.nome)+'</b><span class="small">'+esc(pdia.nome)+(pdia.empresa?' · '+esc(pdia.empresa):'')+'</span></div></div><div class="btn-row"><a class="btn btn-light btn-sm" href="#/interagir">Enviar pergunta</a><a class="btn btn-light btn-sm" href="#/palestrantes">Ver palestrantes</a></div>':'';
  var topo='<div class="card card-dia-hero"><div class="dia-cd">📅 '+cd+'</div>'+destaque+'</div>';
  if(typeof diario._qi!=='number')diario._qi=quiz.length?di%quiz.length:0;
  var qbloco=quiz.length?quizBloco(quiz,byId):'';
  if(typeof diario._ei!=='number')diario._ei=enqs.length?di%enqs.length:0;
  var ebloco=enqs.length?enqueteBloco(enqs):'';
  h(topo+qbloco+ebloco+'<p class="small muted" style="text-align:center;margin-top:16px">Conteúdo novo todo dia até o Fórum. Volte amanhã para o próximo quiz.</p>');
  ligarQuiz(quiz,byId);ligarEnquete(enqs);
}
function quizBloco(quiz,byId){
  var qi=((diario._qi%quiz.length)+quiz.length)%quiz.length;var q=quiz[qi];
  var resp=LS.get('quiz_resp',{});var minha=resp[q.id];var feita=minha!=null;
  var feitas=0,acertos=0;quiz.forEach(function(x){if(resp[x.id]!=null){feitas++;if(resp[x.id]===x.correta)acertos++;}});
  var sp=q.palestrante?byId[q.palestrante]:null;
  var opts=q.opcoes.map(function(o,idx){var cls='quiz-opt';if(feita){if(idx===q.correta)cls+=' ok';else if(idx===minha)cls+=' no';}return '<button class="'+cls+'" data-qopt="'+idx+'"'+(feita?' disabled':'')+'><span class="ql">'+String.fromCharCode(65+idx)+'</span><span class="qt">'+esc(o)+'</span>'+(feita&&idx===q.correta?'<b class="qr">✓</b>':(feita&&idx===minha?'<b class="qr qx">✗</b>':''))+'</button>';}).join('');
  var exp=feita?'<div class="quiz-exp'+(minha===q.correta?' ok':'')+'"><b>'+(minha===q.correta?'Acertou! ✅':'Quase! A resposta certa é a letra '+String.fromCharCode(65+q.correta)+'.')+'</b><p>'+esc(q.explicacao)+'</p>'+(sp?'<a class="btn btn-outline btn-sm" href="#/palestrantes">Ver '+esc(sp.nome)+'</a>':'')+'</div>':'';
  var nav='<div class="quiz-nav"><button class="qnav" data-qnav="-1" aria-label="Anterior">‹</button><span class="small muted">Quiz '+(qi+1)+' de '+quiz.length+(feitas?' · você acertou '+acertos+' de '+feitas:'')+'</span><button class="qnav" data-qnav="1" aria-label="Próximo">›</button></div>';
  return '<div class="section-h" style="margin-top:18px"><h2>Quiz do dia</h2></div><div class="card quiz-card"><p class="kicker">'+esc(q.tema||'Náutica')+'</p><h3 class="quiz-q">'+esc(q.pergunta)+'</h3><div class="quiz-opts">'+opts+'</div>'+exp+nav+'</div>';
}
function ligarQuiz(quiz){
  if(!quiz.length)return;var qi=((diario._qi%quiz.length)+quiz.length)%quiz.length;var q=quiz[qi];
  view.querySelectorAll('[data-qopt]').forEach(function(b){b.onclick=function(){var resp=LS.get('quiz_resp',{});if(resp[q.id]!=null)return;resp[q.id]=+b.getAttribute('data-qopt');LS.set('quiz_resp',resp);diario();};});
  view.querySelectorAll('[data-qnav]').forEach(function(b){b.onclick=function(){diario._qi=qi+ +b.getAttribute('data-qnav');diario();};});
}
function enqueteBloco(enqs){
  var ei=((diario._ei%enqs.length)+enqs.length)%enqs.length;var e=enqs[ei];
  var voto=LS.get('enq_voto',{});var meu=voto[e.id];var votada=meu!=null;
  var corpo=votada?'<div id="enq-res" class="enq-res"><p class="small muted">Carregando resultados…</p></div>':'<div class="enq-opts">'+e.opcoes.map(function(o,idx){return '<button class="enq-opt" data-evote="'+idx+'"><span>'+esc(o)+'</span></button>';}).join('')+'</div>';
  var nav=enqs.length>1?'<div class="quiz-nav"><button class="qnav" data-enav="-1" aria-label="Anterior">‹</button><span class="small muted">Enquete '+(ei+1)+' de '+enqs.length+'</span><button class="qnav" data-enav="1" aria-label="Próximo">›</button></div>':'';
  return '<div class="section-h" style="margin-top:18px"><h2>O que você quer saber</h2></div><div class="card enq-card"><p class="kicker">'+esc(e.tema||'')+'</p><h3 class="quiz-q">'+esc(e.pergunta)+'</h3>'+corpo+'<a class="enq-ask small" href="#/interagir">Tem uma pergunta específica? Mande para o palestrante ›</a>'+nav+'</div>';
}
function ligarEnquete(enqs){
  if(!enqs.length)return;var ei=((diario._ei%enqs.length)+enqs.length)%enqs.length;var e=enqs[ei];
  var meu=(LS.get('enq_voto',{}))[e.id];
  view.querySelectorAll('[data-enav]').forEach(function(b){b.onclick=function(){diario._ei=ei+ +b.getAttribute('data-enav');diario();};});
  if(meu!=null){carregarEnquete(e,meu);return;}
  view.querySelectorAll('[data-evote]').forEach(function(b){b.onclick=function(){var idx=+b.getAttribute('data-evote');var v=LS.get('enq_voto',{});v[e.id]=idx;LS.set('enq_voto',v);try{sessionStorage.setItem('enqts_'+e.id,String(Date.now()));}catch(x){}fetch(API+'/voto',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enquete:e.id,opcao:idx,id:devId()})}).catch(function(){});diario();};});
}
function enqMesclar(server,meu,recent){var c={};var sc=(server&&server.contagem)||{};for(var k in sc)c[k]=sc[k];var total=(server&&server.total)||0;if(recent&&meu!=null&&!(c[meu]>0)){c[meu]=(c[meu]||0)+1;total+=1;}return {total:total,contagem:c};}
function enqBarras(e,data,meu){var total=data.total||0;return e.opcoes.map(function(o,idx){var v=(data.contagem&&data.contagem[idx])||0;var pct=total?Math.round(v*100/total):0;return '<div class="enq-row'+(idx===meu?' meu':'')+'"><div class="enq-top"><span>'+esc(o)+(idx===meu?' <b>· seu voto</b>':'')+'</span><span class="enq-pct">'+pct+'%</span></div><div class="enq-bg"><i style="width:'+pct+'%"></i></div></div>';}).join('')+'<p class="small muted" style="margin:10px 0 0">'+total+' voto'+(total===1?'':'s')+' · atualiza em instantes</p>';}
function carregarEnquete(e,meu){
  var recent=false;try{var s=+(sessionStorage.getItem('enqts_'+e.id)||0);recent=s&&(Date.now()-s)<120000;}catch(x){}
  fetch(API+'/enquete?id='+encodeURIComponent(e.id),{cache:'no-store'}).then(function(r){return r.json();}).then(function(d){var box=document.getElementById('enq-res');if(!box)return;box.innerHTML=enqBarras(e,enqMesclar(d,meu,recent),meu);}).catch(function(){var box=document.getElementById('enq-res');if(box)box.innerHTML='<p class="small muted">Não foi possível carregar os resultados agora.</p>';});
}

/* ---------- compartilhar ---------- */
function share(title,text,url){if(navigator.share){navigator.share({title:title,text:text,url:url}).catch(function(){});}else{var s=text+(url?'\n'+url:'');(navigator.clipboard?navigator.clipboard.writeText(s):Promise.reject()).then(function(){toast('Copiado');},function(){prompt('Copie:',s);});}}
function shareApp(){share('App do VI Fórum ACATMAR','Instale o app oficial do VI Fórum de Capacitação Técnica ACATMAR: programação, avisos, credencial com QR Code e certificado.',D.evento.app_url);}
document.getElementById('btn-share').addEventListener('click',function(){if(!D)return;if(!isStandalone()){location.hash='#/instalar';}else shareApp();});
(function(){if(!isStandalone()){var b=document.getElementById('btn-share');b.innerHTML='<span style="font-family:var(--f-cond);font-weight:700;text-transform:uppercase;letter-spacing:.06em;font-size:.8rem;padding:0 4px">Instalar</span>';b.style.width='auto';b.style.padding='0 10px';b.style.background='var(--teal)';b.setAttribute('aria-label','Instalar o app');b.title='Instalar o app';}})();

/* ---------- service worker ---------- */
if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('sw.js').then(function(reg){reg.addEventListener('updatefound',function(){var nw=reg.installing;nw.addEventListener('statechange',function(){if(nw.state==='installed'&&navigator.serviceWorker.controller){var t=document.getElementById('toast');t.innerHTML='Nova versão do app disponível. <b style="text-decoration:underline">Atualizar agora</b>';t.hidden=false;t.style.cursor='pointer';t.onclick=function(){location.reload();};clearTimeout(toast._t);}});});}).catch(function(){});});}
window.addEventListener('appinstalled',function(){toast('App instalado!');LS.set('instalado',true);pingUso(true,{instalado:true});document.getElementById('install-banner').hidden=true;});

document.addEventListener('visibilitychange',function(){if(!document.hidden&&D)fetch('data/forum.json?t='+Date.now(),{cache:'no-store'}).then(function(r){return r.json();}).then(function(j){if(j.versao!==D.versao){D=j;LS.set('data',j);render();updateBadge();toast('Conteúdo atualizado');}}).catch(function(){});});

load();
try{setTimeout(function(){pingUso(false);},2500);}catch(e){}
})();
