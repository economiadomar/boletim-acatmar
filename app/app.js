/* App do VI Fórum ACATMAR — PWA sem framework. Conteúdo vem de data/forum.json */
(function(){
'use strict';
var D=null, view=document.getElementById('view');
var LS={get:function(k,d){try{var v=localStorage.getItem('forum_'+k);return v==null?d:JSON.parse(v);}catch(e){return d;}},set:function(k,v){try{localStorage.setItem('forum_'+k,JSON.stringify(v));}catch(e){}}};
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function h(html){view.innerHTML=html;view.scrollTop=0;window.scrollTo(0,0);}
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
    if(!cached)boot();else if(changed){render();toast('Conteúdo atualizado');}
    updateBadge();
  }).catch(function(){ if(!D){h('<div class="card"><h3>Sem conexão</h3><p>Abra o app com internet uma vez para baixar o conteúdo do Fórum.</p></div>');} });
}
var booted=false;
function boot(){if(booted)return;booted=true;render();updateBadge();setTimeout(function(){var s=document.getElementById('splash');s.classList.add('off');setTimeout(function(){s.remove();},400);},350);}

/* ---------- roteamento ---------- */
var routes={'/':home,'/programacao':programacao,'/palestrantes':palestrantes,'/avisos':avisos,'/aviso':aviso,'/credencial':credencial,'/patrocinadores':patrocinadores,'/local':local,'/interagir':interagir,'/certificado':certificado,'/instalar':instalar,'/sobre':sobre,'/mais':mais,'/anterior':anterior,'/faq':faq};
var titles={'/programacao':'Programação','/palestrantes':'Palestrantes','/avisos':'Avisos','/aviso':'Aviso','/credencial':'Minha credencial','/patrocinadores':'Patrocinadores','/local':'Local e como chegar','/interagir':'Interagir','/certificado':'Certificado','/instalar':'Instalar o app','/sobre':'Sobre o Fórum','/mais':'Mais','/anterior':'V Fórum (2025)','/faq':'Perguntas frequentes'};
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
function home(){
  var e=D.evento,st=status();var d=eventDate();
  var cd='';
  if(st==='antes'){var diff=d.start-new Date();var dd=Math.floor(diff/864e5),hh=Math.floor(diff%864e5/36e5),mm=Math.floor(diff%36e5/6e4);
    cd='<div class="countdown"><div class="cd"><b>'+dd+'</b><span>dias</span></div><div class="cd"><b>'+hh+'</b><span>horas</span></div><div class="cd"><b>'+mm+'</b><span>min</span></div></div>';}
  else if(st==='agora')cd='<div class="live-pill"><i></i> Acontecendo agora</div>';
  else cd='<div class="tag" style="background:var(--teal);color:#fff;margin-top:12px">Edição realizada. Obrigado por participar!</div>';
  var unread=unreadAvisos();
  var av=D.avisos.slice(0,2).map(avisoCard).join('');
  var spons=D.patrocinadores.map(function(p){return '<img src="'+p.logo+'" alt="'+esc(p.alt)+'" style="width:'+Math.round(p.largura*0.85)+'px">';}).join('');
  var regBtn=st==='antes'?'<a class="btn btn-teal btn-block" href="'+e.inscricao_url+'" target="_blank" rel="noopener">Inscrição gratuita</a>':'';
  h('<section class="hero"><img src="media/hero.jpg" alt=""><div class="hero-in"><p class="kicker">'+esc(e.edicao)+' · '+esc(e.mote)+'</p><h1>'+esc(e.nome)+'</h1><p>'+esc(e.data_texto)+' · '+esc(e.horario_texto)+'</p>'+cd+'</div></section>'
   +'<div class="quick"><a href="#/programacao"><i>🗓️</i>Programação</a><a href="#/local"><i>📍</i>Local</a><a href="#/credencial"><i>🎫</i>Credencial</a><a href="#/interagir"><i>💬</i>Interagir</a></div>'
   +'<section class="section"><div class="card"><div class="info"><div class="info-row"><div class="ic">📅</div><div><b>Quando</b><span>'+esc(e.data_texto)+'<br>'+esc(e.horario_texto)+'</span></div></div><div class="info-row"><div class="ic">📍</div><div><b>Onde</b><span>'+esc(e.local.nome)+'<br><small class="muted">'+esc(e.local.endereco)+'</small></span></div></div><div class="info-row"><div class="ic">🎟️</div><div><b>Participação</b><span>Gratuita, vagas limitadas'+(e.certificado?' · com certificado':'')+'</span></div></div></div>'+(regBtn?'<div class="btn-row">'+regBtn+'</div>':'')+'</div></section>'
   +'<section class="section"><div class="section-h"><h2>Avisos'+(unread?' <span class="tag red">'+unread+' novo'+(unread>1?'s':'')+'</span>':'')+'</h2><a href="#/avisos">Ver todos</a></div>'+av+'</section>'
   +'<section class="section"><div class="section-h"><h2>Sobre o Fórum</h2><a href="#/sobre">Mais</a></div><div class="card"><p>'+esc(D.sobre.resumo)+'</p><p class="small muted">'+esc(D.sobre.para_quem)+'</p></div></section>'
   +'<section class="section"><div class="section-h"><h2>Quem faz acontecer</h2><a href="#/patrocinadores">Ver</a></div><div class="spons-strip">'+spons+'</div></section>'
   +'<section class="section"><div class="card" style="background:var(--navy);color:#fff;border:0"><p class="kicker" style="color:var(--teal-b)">Dica</p><h3 style="color:#fff">Instale o app na tela inicial</h3><p class="small" style="opacity:.85">Assim ele abre em um toque, mostra sua credencial rápido no credenciamento e funciona mesmo sem sinal.</p><div class="btn-row"><a class="btn btn-light btn-sm" href="#/instalar">Como instalar</a></div></div></section>');
  if(st==='antes'){clearInterval(home._t);home._t=setInterval(function(){if(route().path==='/')home();else clearInterval(home._t);},60000);}
}

/* ---------- Programação ---------- */
var periodoSel=LS.get('periodo','Manhã');
function programacao(){
  var favs=LS.get('favs',[]);var st=status();var n=nowHM();
  var per=[];D.programacao.forEach(function(s){if(per.indexOf(s.periodo)<0)per.push(s.periodo);});
  if(per.indexOf(periodoSel)<0)periodoSel=per[0];
  if(st==='agora'){var cur=null;D.programacao.forEach(function(s){if(hm(s.hora)<=n)cur=s;});if(cur)periodoSel=cur.periodo;}
  var list=D.programacao.filter(function(s){return s.periodo===periodoSel;});
  var nowId=null;if(st==='agora'){for(var i=0;i<D.programacao.length;i++){var a=D.programacao[i],b=D.programacao[i+1];if(hm(a.hora)<=n&&(!b||hm(b.hora)>n))nowId=a.id;}}
  var items=list.map(function(s){var f=favs.indexOf(s.id)>=0;var cls='card sess '+(s.tipo||'')+(s.id===nowId?' now':'');
    return '<div class="'+cls+'"><div class="sess-h">'+esc(s.hora.replace(':','h'))+'</div><div class="sess-b"><h3>'+esc(s.titulo)+'</h3><div class="quem">'+esc(s.quem||'')+'</div>'+(s.desc?'<div class="desc">'+esc(s.desc)+'</div>':'')+(s.id===nowId?'<span class="tag red">Agora</span>':'')+(s.tipo==='bloco'||s.tipo==='palestra'?'<div class="btn-row"><a class="btn btn-outline btn-sm" href="#/interagir/'+encodeURIComponent(s.id)+'">Enviar pergunta</a></div>':'')+'</div>'+(s.tipo!=='pausa'?'<div class="sess-a"><button class="fav'+(f?' on':'')+'" data-fav="'+esc(s.id)+'" aria-label="Favoritar">★</button></div>':'')+'</div>';}).join('');
  h((D.programacao_status==='preliminar'?'<div class="notice">⚠️ '+esc(D.programacao_aviso)+'</div>':'')
   +'<div class="periodo">'+per.map(function(p){return '<button data-per="'+esc(p)+'" class="'+(p===periodoSel?'on':'')+'">'+esc(p)+'</button>';}).join('')+'</div>'
   +items
   +'<div class="btn-row"><button class="btn btn-navy btn-sm" id="btn-ics">Adicionar à minha agenda</button>'+(favs.length?'<span class="small muted" style="align-self:center">★ '+favs.length+' favorito'+(favs.length>1?'s':'')+'</span>':'')+'</div>'
   +'<section class="section" style="margin-top:22px"><div class="section-h"><h2>'+esc(D.edicao_anterior.titulo)+'</h2><a href="#/anterior">Ver</a></div><div class="card"><p class="small">'+esc(D.edicao_anterior.resumo)+'</p></div></section>');
  view.querySelectorAll('[data-per]').forEach(function(b){b.onclick=function(){periodoSel=b.getAttribute('data-per');LS.set('periodo',periodoSel);programacao();};});
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
  var body=ps.length?ps.map(function(p){return '<div class="card spk"><div class="av">'+(p.foto?'<img src="'+p.foto+'" alt="">':esc((p.nome||'?').split(' ').map(function(w){return w[0];}).slice(0,2).join('')))+'</div><div><b>'+esc(p.nome)+'</b><span>'+esc(p.cargo||'')+(p.empresa?' · '+esc(p.empresa):'')+'</span>'+(p.tema?'<div class="small" style="margin-top:4px">'+esc(p.tema)+'</div>':'')+'</div></div>';}).join('')
   :'<div class="card"><h3>Em breve</h3><p>Os palestrantes do VI Fórum serão anunciados aqui no app, em primeira mão para os inscritos. Você receberá um aviso.</p></div>';
  var prev=D.edicao_anterior.programacao.map(function(s){return '<div class="card"><h3 style="text-transform:none;letter-spacing:0;font-family:var(--f-body);font-size:.95rem">'+esc(s.titulo)+'</h3><p class="small muted">'+esc(s.quem)+'</p></div>';}).join('');
  h(body+'<section class="section" style="margin-top:22px"><div class="section-h"><h2>Quem já passou pelo Fórum</h2><a href="#/anterior">V Fórum</a></div>'+prev+'</section>');
}

/* ---------- Avisos ---------- */
function unreadAvisos(){var seen=LS.get('seen',[]);return D.avisos.filter(function(a){return seen.indexOf(a.id)<0;}).length;}
function updateBadge(){if(!D)return;var n=unreadAvisos();var b=document.getElementById('badge-avisos');b.hidden=!n;b.textContent=n;if(navigator.setAppBadge){if(n)navigator.setAppBadge(n);else if(navigator.clearAppBadge)navigator.clearAppBadge();}}
function avisoCard(a){var seen=LS.get('seen',[]);var un=seen.indexOf(a.id)<0;return '<a class="card aviso'+(un?' unread':'')+(a.destaque?' destaque':'')+'" href="#/aviso/'+esc(a.id)+'"><div class="aviso-dot"></div><div><div class="aviso-date">'+fmtData(a.data)+'</div><h3>'+esc(a.titulo)+'</h3><p>'+esc(a.texto.length>140?a.texto.slice(0,140)+'…':a.texto)+'</p></div></a>';}
function avisos(){h('<p class="small muted" style="margin:0 0 12px">As novidades do Fórum chegam aqui antes do e-mail. Toque para ler.</p>'+D.avisos.map(avisoCard).join('')+'<div class="card" style="margin-top:14px"><p class="small muted">Quer receber também por WhatsApp e e-mail? <a href="'+D.evento.inscricao_url+'" target="_blank" rel="noopener">Faça sua inscrição</a>.</p></div>');}
function aviso(id){var a=null;D.avisos.forEach(function(x){if(x.id===id)a=x;});if(!a){location.hash='#/avisos';return;}
  var seen=LS.get('seen',[]);if(seen.indexOf(id)<0){seen.push(id);LS.set('seen',seen);updateBadge();}
  h('<div class="card'+(a.destaque?' destaque':'')+'"><div class="aviso-date">'+fmtData(a.data)+'</div><h3 style="margin:6px 0 10px;font-size:1.2rem">'+esc(a.titulo)+'</h3>'+a.texto.split('\n').map(function(p){return '<p>'+esc(p)+'</p>';}).join('')+(a.imagem?'<img src="'+a.imagem+'" alt="" style="border-radius:12px;margin-top:10px">':'')+(a.link?'<div class="btn-row"><a class="btn btn-teal" href="'+a.link+'" target="_blank" rel="noopener">'+esc(a.link_label||'Abrir')+'</a></div>':'')+'</div><div class="btn-row"><button class="btn btn-outline btn-sm" id="share-aviso">Compartilhar aviso</button></div>');
  document.getElementById('share-aviso').onclick=function(){share(a.titulo,a.texto+'\n\n'+D.evento.app_url+'#/aviso/'+a.id);};
}

/* ---------- Credencial / QR ---------- */
function credencial(){
  var me=LS.get('me',null);var e=D.evento;
  if(!me){
    h('<div class="card"><p class="kicker">Sua credencial</p><h3>Crie seu QR Code</h3><p class="small muted">Preencha uma vez. Seu QR Code fica salvo neste aparelho e serve para o credenciamento e para trocar contato com outros participantes: quem escanear com a câmera do celular salva você direto na agenda.</p><form id="f-me"><div class="field"><label>Nome completo</label><input name="nome" required autocomplete="name"></div><div class="field"><label>Empresa ou instituição</label><input name="empresa" autocomplete="organization"></div><div class="field"><label>Cargo ou função</label><input name="cargo" autocomplete="organization-title"></div><div class="field"><label>E-mail</label><input name="email" type="email" autocomplete="email"></div><div class="field"><label>WhatsApp</label><input name="fone" type="tel" autocomplete="tel" placeholder="(48) 9 9999-9999"></div><div class="field"><label>Perfil</label><select name="tipo"><option>Participante</option><option>Palestrante</option><option>Patrocinador</option><option>Imprensa</option><option>Estudante</option><option>Organização</option></select></div><button class="btn btn-teal btn-block" type="submit">Gerar minha credencial</button></form></div>');
    document.getElementById('f-me').onsubmit=function(ev){ev.preventDefault();var fd=new FormData(ev.target);var o={};fd.forEach(function(v,k){o[k]=String(v).trim();});LS.set('me',o);credencial();toast('Credencial criada');};
    return;
  }
  var A=function(t){return String(t||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^\x20-\x7e]/g,'');};
  var vcard='BEGIN:VCARD\nVERSION:3.0\nN:'+A(me.nome)+'\nFN:'+A(me.nome)+(me.empresa?'\nORG:'+A(me.empresa):'')+(me.cargo?'\nTITLE:'+A(me.cargo):'')+(me.fone?'\nTEL;TYPE=CELL:'+me.fone.replace(/[^\d+]/g,''):'')+(me.email?'\nEMAIL:'+A(me.email):'')+'\nNOTE:VI Forum ACATMAR 2026\nEND:VCARD';
  h('<div class="badge-card"><div class="badge-top"><img src="../media/logos/acatmar-branca.png" alt="ACATMAR"><span>'+esc(e.nome)+'</span></div><div class="badge-name">'+esc(me.nome)+'</div><div class="badge-sub">'+esc([me.cargo,me.empresa].filter(Boolean).join(' · '))+'</div><span class="badge-tipo">'+esc(me.tipo||'Participante')+'</span><div class="badge-qr" id="qr"></div><div class="badge-foot"><span>'+esc(e.data_texto)+'</span><span>'+esc(e.local.bairro)+' · Fpolis</span></div></div>'
   +'<p class="small muted" style="text-align:center;margin:12px 0">Mostre este QR Code no credenciamento. Para networking, peça para escanearem com a câmera: seu contato é salvo na hora.</p>'
   +'<div class="btn-row"><button class="btn btn-outline btn-sm" id="me-edit">Editar dados</button><button class="btn btn-navy btn-sm" id="me-share">Compartilhar contato</button></div>');
  try{new QRCode(document.getElementById('qr'),{text:vcard,width:190,height:190,correctLevel:QRCode.CorrectLevel.L,colorDark:'#0a2540'});}catch(err){try{document.getElementById('qr').innerHTML='';new QRCode(document.getElementById('qr'),{text:'BEGIN:VCARD\nVERSION:3.0\nFN:'+A(me.nome)+'\nEND:VCARD',width:190,height:190,correctLevel:QRCode.CorrectLevel.L,colorDark:'#0a2540'});}catch(e2){document.getElementById('qr').innerHTML='<p class="small" style="color:#0a2540;margin:0">Não foi possível gerar o QR. Edite os dados e tente de novo.</p>';}}
  document.getElementById('me-edit').onclick=function(){LS.set('me',null);credencial();};
  document.getElementById('me-share').onclick=function(){share(me.nome+' · '+e.curto,[me.nome,me.cargo,me.empresa,me.email,me.fone].filter(Boolean).join('\n'));};
}

/* ---------- Patrocinadores ---------- */
function patrocinadores(){
  var c=D.patrocinio_cta;
  h(D.patrocinadores.map(function(p){return '<div class="cota"><p class="kicker">'+esc(p.cota)+'</p><img src="'+p.logo+'" alt="'+esc(p.alt)+'" style="width:'+p.largura+'px"></div>';}).join('')
   +'<div class="card" style="background:var(--navy);color:#fff;border:0;margin-top:14px"><p class="kicker" style="color:var(--teal-b)">Patrocínio e apoio</p><h3 style="color:#fff">'+esc(c.titulo)+'</h3><p class="small" style="opacity:.9">'+esc(c.texto)+'</p><div class="btn-row"><a class="btn btn-teal btn-sm" href="mailto:'+c.email+'?subject='+encodeURIComponent('Patrocínio '+D.evento.curto)+'">Falar com a ACATMAR</a></div></div>');
}

/* ---------- Local ---------- */
function local(){
  var l=D.evento.local;
  h('<div class="card"><p class="kicker">Local do evento</p><h3>'+esc(l.nome)+'</h3><p>'+esc(l.endereco)+'</p><div class="btn-row"><a class="btn btn-teal btn-sm" href="'+l.maps+'" target="_blank" rel="noopener">Google Maps</a><a class="btn btn-navy btn-sm" href="'+l.waze+'" target="_blank" rel="noopener">Waze</a><a class="btn btn-outline btn-sm" href="'+l.apple+'" target="_blank" rel="noopener">Apple Maps</a></div></div>'
   +'<div class="card"><h3>Como chegar e dicas</h3>'+l.dicas.map(function(d){return '<p class="small">• '+esc(d)+'</p>';}).join('')+'</div>'
   +'<div class="card"><h3>Horário</h3><p>'+esc(D.evento.data_texto)+'<br>'+esc(D.evento.horario_texto)+'. Credenciamento a partir das 8h.</p></div>');
}

/* ---------- Interagir ---------- */
function interagir(sessId){
  var e=D.evento;var sess=null;D.programacao.forEach(function(s){if(s.id===sessId)sess=s;});var me=LS.get('me',{})||{};
  var opts='<option value="">Geral / não sei</option>'+D.programacao.filter(function(s){return s.tipo!=='pausa'&&s.tipo!=='org';}).map(function(s){return '<option'+(sess&&sess.id===s.id?' selected':'')+'>'+esc(s.hora.replace(':','h')+' · '+s.titulo)+'</option>';}).join('');
  var wa=e.whatsapp_comunidade?'<a href="'+e.whatsapp_comunidade+'" target="_blank" rel="noopener"><i>💬</i>Grupo do Fórum no WhatsApp</a>':'';
  h('<div class="menu">'+wa+'<a href="'+e.instagram+'" target="_blank" rel="noopener"><i>📸</i>@acatmarassociacao no Instagram</a><a href="#" id="share-app"><i>📲</i>Convidar alguém para o app</a><a href="mailto:'+e.email+'"><i>✉️</i>Falar com a organização</a></div>'
   +'<div class="card" id="c-perg"><p class="kicker">Pergunte ao palestrante</p><h3>Envie sua pergunta</h3><p class="small muted">As perguntas chegam à organização e são levadas ao palestrante durante o Fórum.</p><form id="f-perg"><input type="hidden" name="_subject" value="[App VI Fórum] Pergunta ao palestrante"><input type="text" name="_honey" style="display:none"><div class="field"><label>Palestra</label><select name="palestra">'+opts+'</select></div><div class="field"><label>Sua pergunta</label><textarea name="pergunta" required maxlength="600"></textarea></div><div class="field"><label>Seu nome</label><input name="nome" value="'+esc(me.nome||'')+'" required></div><div class="field"><label>Seu e-mail</label><input name="email" type="email" value="'+esc(me.email||'')+'"></div><button class="btn btn-teal btn-block" type="submit">Enviar pergunta</button></form></div>'
   +'<div class="card" id="c-aval"><p class="kicker">Sua opinião</p><h3>Avalie o Fórum</h3><form id="f-aval"><input type="hidden" name="_subject" value="[App VI Fórum] Avaliação"><input type="text" name="_honey" style="display:none"><div class="field"><label>Nota geral</label><select name="nota"><option>5 · Excelente</option><option>4 · Muito bom</option><option>3 · Bom</option><option>2 · Regular</option><option>1 · Ruim</option></select></div><div class="field"><label>O que mais gostou e o que podemos melhorar?</label><textarea name="comentario" required maxlength="800"></textarea></div><div class="field"><label>Seu nome</label><input name="nome" value="'+esc(me.nome||'')+'"></div><button class="btn btn-navy btn-block" type="submit">Enviar avaliação</button></form></div>');
  document.getElementById('share-app').onclick=function(ev){ev.preventDefault();shareApp();};
  ['f-perg','f-aval'].forEach(function(id){var f=document.getElementById(id);f.onsubmit=function(ev){ev.preventDefault();var btn=f.querySelector('button');btn.disabled=true;btn.textContent='Enviando…';var fd=new FormData(f);fd.append('origem','App VI Fórum ACATMAR');
    fetch(e.formsubmit,{method:'POST',headers:{'Accept':'application/json'},body:fd}).then(function(r){if(!r.ok)throw 0;f.parentNode.innerHTML='<div class="ok-box">⚓ Recebido! Obrigado pela participação.</div>';}).catch(function(){btn.disabled=false;btn.textContent='Tentar de novo';toast('Não foi possível enviar agora. Verifique a conexão.');});};});
}

/* ---------- Certificado ---------- */
function certificado(){
  var c=D.certificado,me=LS.get('me',{})||{};
  if(!c.liberado){h('<div class="card"><p class="kicker">Certificado de participação</p><h3>Disponível após o evento</h3><p>'+esc(c.texto)+'</p><p class="small muted">Carga horária: '+esc(c.carga_horaria)+'.</p></div>');return;}
  h('<div class="card"><p class="kicker">Certificado de participação</p><h3>Emita seu certificado</h3><p class="small muted">Digite seu nome como deve aparecer e o código divulgado no encerramento do Fórum.</p><form id="f-cert"><div class="field"><label>Nome completo</label><input name="nome" required value="'+esc(me.nome||'')+'"></div><div class="field"><label>Código do evento</label><input name="codigo" required autocapitalize="characters"></div><button class="btn btn-teal btn-block" type="submit">Gerar PDF</button></form></div>');
  document.getElementById('f-cert').onsubmit=function(ev){ev.preventDefault();var fd=new FormData(ev.target);var cod=String(fd.get('codigo')).trim().toUpperCase();if(cod!==String(c.codigo).toUpperCase()){toast('Código inválido. Confira com a organização.');return;}
    var s=document.createElement('script');s.src='lib/jspdf.umd.min.js';s.onload=function(){gerarPDF(String(fd.get('nome')).trim());};document.body.appendChild(s);};
}
function gerarPDF(nome){
  var e=D.evento;var doc=new window.jspdf.jsPDF({orientation:'landscape',unit:'mm',format:'a4'});
  doc.setFillColor(10,37,64);doc.rect(0,0,297,210,'F');doc.setFillColor(0,163,180);doc.rect(0,0,297,6,'F');doc.rect(0,204,297,6,'F');
  doc.setTextColor(53,201,218);doc.setFont('helvetica','bold');doc.setFontSize(12);doc.text('ACATMAR · ASSOCIAÇÃO NÁUTICA BRASILEIRA',148.5,28,{align:'center'});
  doc.setTextColor(255,255,255);doc.setFontSize(30);doc.text('CERTIFICADO DE PARTICIPAÇÃO',148.5,52,{align:'center'});
  doc.setFont('helvetica','normal');doc.setFontSize(13);doc.text('Certificamos que',148.5,78,{align:'center'});
  doc.setFont('helvetica','bold');doc.setFontSize(26);doc.text(nome.toUpperCase(),148.5,96,{align:'center',maxWidth:250});
  doc.setFont('helvetica','normal');doc.setFontSize(13);
  var txt='participou do '+e.nome+', realizado em '+e.data_texto.replace(/^[^,]+, /,'')+', no '+e.local.nome+', em Florianópolis/SC, com carga horária de '+D.certificado.carga_horaria+'.';
  doc.text(doc.splitTextToSize(txt,230),148.5,114,{align:'center'});
  doc.setFontSize(11);doc.setTextColor(53,201,218);doc.text('Leandro "Mané" Ferrari · Presidente da ACATMAR',148.5,160,{align:'center'});
  doc.setDrawColor(53,201,218);doc.line(98,152,199,152);
  doc.setTextColor(200,210,220);doc.setFontSize(9);doc.text('Emitido pelo app oficial do Fórum · www.acatmar.org/app · Código '+D.certificado.codigo,148.5,190,{align:'center'});
  doc.save('certificado-vi-forum-acatmar.pdf');toast('Certificado gerado');
}

/* ---------- Instalar ---------- */
var deferredPrompt=null;
window.addEventListener('beforeinstallprompt',function(ev){ev.preventDefault();deferredPrompt=ev;maybeBanner();});
function isStandalone(){return window.matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;}
function isIOS(){return /iphone|ipad|ipod/i.test(navigator.userAgent)&&!window.MSStream;}
function maybeBanner(){if(isStandalone()||LS.get('banner_off',false))return;var b=document.getElementById('install-banner');b.hidden=false;
  document.getElementById('ib-install').onclick=function(){if(deferredPrompt){deferredPrompt.prompt();deferredPrompt.userChoice.then(function(){b.hidden=true;deferredPrompt=null;});}else{location.hash='#/instalar';b.hidden=true;}};
  document.getElementById('ib-close').onclick=function(){b.hidden=true;LS.set('banner_off',true);};}
function instalar(){
  var ios='<div class="steps"><div><span>Abra este endereço no <b>Safari</b> (no iPhone, só o Safari instala apps da web): <b>acatmar.org/app</b></span></div><div><span>Toque no botão <b>Compartilhar</b> (o quadrado com a seta para cima, na barra inferior).</span></div><div><span>Role e toque em <b>"Adicionar à Tela de Início"</b>.</span></div><div><span>Confirme em <b>Adicionar</b>. O ícone do Fórum aparece na sua tela inicial.</span></div></div>';
  var and='<div class="steps"><div><span>Abra <b>acatmar.org/app</b> no <b>Chrome</b>.</span></div><div><span>Toque em <b>Instalar</b> no aviso que aparece, ou no menu ⋮ escolha <b>"Instalar app"</b> / <b>"Adicionar à tela inicial"</b>.</span></div><div><span>Confirme. O app do Fórum aparece junto dos seus outros apps.</span></div></div>';
  h((isStandalone()?'<div class="ok-box" style="margin-bottom:14px">✅ O app já está instalado neste aparelho.</div>':'')
   +(deferredPrompt?'<div class="card" style="text-align:center"><h3>Instalar agora</h3><p class="small muted">Seu celular permite instalar em um toque.</p><button class="btn btn-teal btn-block" id="btn-inst">Instalar o app</button></div>':'')
   +'<div class="card"><p class="kicker">iPhone e iPad</p><h3>Safari</h3>'+ios+'</div><div class="card"><p class="kicker">Android</p><h3>Chrome</h3>'+and+'</div>'
   +'<div class="card"><h3>Por que instalar?</h3><p class="small">• Abre em um toque, como um app da loja.<br>• Sua credencial com QR Code aparece na hora no credenciamento.<br>• Programação, local e avisos ficam disponíveis mesmo sem sinal.<br>• Sem cadastro, sem senha, sem ocupar espaço.</p><div class="btn-row"><button class="btn btn-outline btn-sm" id="share-app2">Enviar o link para alguém</button></div></div>');
  var bi=document.getElementById('btn-inst');if(bi)bi.onclick=function(){deferredPrompt.prompt();};
  document.getElementById('share-app2').onclick=shareApp;
}

/* ---------- Sobre / Mais / Anterior / FAQ ---------- */
function sobre(){var s=D.sobre;h('<div class="card"><p class="kicker">'+esc(D.evento.edicao)+'</p><h3>'+esc(D.evento.nome)+'</h3><p>'+esc(s.resumo)+'</p><p>'+esc(s.para_quem)+'</p></div><div class="card"><h3>Por que participar</h3>'+s.motivos.map(function(m){return '<p class="small">✔ '+esc(m)+'</p>';}).join('')+'</div><section class="section"><div class="section-h"><h2>Edições anteriores</h2></div><div class="hist">'+s.historia.map(function(x){return '<div><b>'+x.ed+'</b><span>'+esc(x.tema)+'<small>'+x.ano+' · '+esc(x.onde)+'</small></span></div>';}).join('')+'</div></section><div class="btn-row"><a class="btn btn-outline btn-sm" href="'+D.evento.site_url+'" target="_blank" rel="noopener">Ver no site da ACATMAR</a></div>');}
function anterior(){var a=D.edicao_anterior;h('<div class="card"><p>'+esc(a.resumo)+'</p></div><div class="gal">'+a.fotos.map(function(f){return '<img src="'+f+'" alt="" loading="lazy">';}).join('')+'</div><section class="section" style="margin-top:16px"><div class="section-h"><h2>Programação de 2025</h2></div>'+a.programacao.map(function(s){return '<div class="card sess"><div class="sess-h" style="flex-basis:60px;font-size:.85rem">'+esc(s.periodo)+'</div><div class="sess-b"><h3>'+esc(s.titulo)+'</h3><div class="quem">'+esc(s.quem)+'</div></div></div>';}).join('')+'</section><div class="btn-row"><a class="btn btn-outline btn-sm" href="'+a.link+'" target="_blank" rel="noopener">Matéria completa no site</a></div>');}
function faq(){h(D.faq.map(function(q){return '<details><summary>'+esc(q.p)+'</summary><p>'+esc(q.r)+'</p></details>';}).join(''));}
function mais(){var me=LS.get('me',null);
  h('<div class="card" style="display:flex;gap:12px;align-items:center"><div class="spk"><div class="av">'+esc(me?me.nome.split(' ').map(function(w){return w[0];}).slice(0,2).join(''):'?')+'</div><div><b>'+esc(me?me.nome:'Crie sua credencial')+'</b><span>'+esc(me?[me.cargo,me.empresa].filter(Boolean).join(' · ')||(me.tipo||''):'Nome, empresa e QR Code')+'</span></div></div><a href="#/credencial" style="margin-left:auto;font-size:1.4rem;text-decoration:none">›</a></div>'
   +'<div class="menu"><a href="#/palestrantes"><i>🎤</i>Palestrantes</a><a href="#/patrocinadores"><i>🤝</i>Patrocinadores e apoio</a><a href="#/local"><i>📍</i>Local e como chegar</a><a href="#/interagir"><i>💬</i>Interagir e perguntar</a><a href="#/certificado"><i>📜</i>Certificado</a><a href="#/anterior"><i>📷</i>V Fórum (2025)</a><a href="#/sobre"><i>⚓</i>Sobre o Fórum</a><a href="#/faq"><i>❓</i>Perguntas frequentes</a><a href="#/instalar"><i>📲</i>Instalar o app</a></div>'
   +'<div class="menu"><a href="'+D.evento.inscricao_url+'" target="_blank" rel="noopener"><i>📝</i>Inscrição gratuita</a><a href="https://www.acatmar.org/" target="_blank" rel="noopener"><i>🌐</i>Site da ACATMAR</a><a href="https://www.acatmar.org/privacidade.html" target="_blank" rel="noopener"><i>🔒</i>Política de Privacidade</a></div>'
   +'<p class="small muted" style="text-align:center">Seus dados de credencial ficam somente neste aparelho.<br>App oficial · ACATMAR · versão '+esc(D.versao)+'</p>');}

/* ---------- compartilhar ---------- */
function share(title,text,url){if(navigator.share){navigator.share({title:title,text:text,url:url}).catch(function(){});}else{var s=text+(url?'\n'+url:'');(navigator.clipboard?navigator.clipboard.writeText(s):Promise.reject()).then(function(){toast('Copiado');},function(){prompt('Copie:',s);});}}
function shareApp(){share('App do VI Fórum ACATMAR','Instale o app oficial do VI Fórum de Capacitação Técnica ACATMAR: programação, avisos, credencial com QR Code e certificado.',D.evento.app_url);}
document.getElementById('btn-share').addEventListener('click',function(){if(D)shareApp();});

/* ---------- service worker ---------- */
if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('sw.js').then(function(reg){reg.addEventListener('updatefound',function(){var nw=reg.installing;nw.addEventListener('statechange',function(){if(nw.state==='installed'&&navigator.serviceWorker.controller)toast('Nova versão do app disponível. Feche e abra de novo.');});});}).catch(function(){});});}
window.addEventListener('appinstalled',function(){toast('App instalado!');document.getElementById('install-banner').hidden=true;});
setTimeout(maybeBanner,6000);
document.addEventListener('visibilitychange',function(){if(!document.hidden&&D)fetch('data/forum.json?t='+Date.now(),{cache:'no-store'}).then(function(r){return r.json();}).then(function(j){if(j.versao!==D.versao){D=j;LS.set('data',j);render();updateBadge();toast('Conteúdo atualizado');}}).catch(function(){});});

load();
})();
