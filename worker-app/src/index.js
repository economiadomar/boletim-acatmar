// Controle de uso do app do Forum ACATMAR.
// POST /registro  -> grava/atualiza um aparelho (chave d:<id>)
// GET  /resumo?pin= -> totais + lista
// GET  /csv?pin=     -> planilha
// POST /voto        -> registra voto numa enquete (chave v:<enquete>:<id>, opcao na metadata)
// GET  /enquete?id= -> contagem de votos de uma enquete (publico)
const ORIGENS = ['https://www.acatmar.org', 'https://acatmar.org'];

function cors(origin) {
  const o = ORIGENS.includes(origin) ? origin : ORIGENS[0];
  return {
    'Access-Control-Allow-Origin': o,
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400'
  };
}
const json = (data, origin, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...cors(origin) } });

const lim = (v, n) => (typeof v === 'string' ? v.trim().slice(0, n) : '');

async function todos(env) {
  const out = [];
  let cursor;
  do {
    const r = await env.FORUM_APP.list({ prefix: 'd:', limit: 1000, cursor });
    for (const k of r.keys) out.push(k.name);
    cursor = r.list_complete ? null : r.cursor;
  } while (cursor);
  return out;
}

// Soma os votos de uma enquete usando a metadata das chaves (sem ler valor a valor).
async function apurar(env, enq) {
  const contagem = {};
  let total = 0, cursor;
  do {
    const r = await env.FORUM_APP.list({ prefix: 'v:' + enq + ':', limit: 1000, cursor });
    for (const k of r.keys) {
      const o = k.metadata && k.metadata.o;
      if (Number.isInteger(o)) { contagem[o] = (contagem[o] || 0) + 1; total++; }
    }
    cursor = r.list_complete ? null : r.cursor;
  } while (cursor);
  return { total, contagem };
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const origin = req.headers.get('Origin') || '';
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(origin) });

    if (url.pathname === '/registro' && req.method === 'POST') {
      let b;
      try { b = await req.json(); } catch (e) { return json({ erro: 'json' }, origin, 400); }
      const id = lim(b.id, 40);
      if (!id) return json({ erro: 'id' }, origin, 400);
      const chave = 'd:' + id;
      const antes = await env.FORUM_APP.get(chave, 'json');
      const agora = new Date().toISOString();
      const reg = {
        id,
        nome: lim(b.nome, 80) || (antes && antes.nome) || '',
        empresa: lim(b.empresa, 80) || (antes && antes.empresa) || '',
        cargo: lim(b.cargo, 80) || (antes && antes.cargo) || '',
        email: lim(b.email, 90) || (antes && antes.email) || '',
        fone: lim(b.fone, 30) || (antes && antes.fone) || '',
        tipo: lim(b.tipo, 40) || (antes && antes.tipo) || '',
        plataforma: lim(b.plataforma, 40) || (antes && antes.plataforma) || '',
        instalado: !!(b.instalado || (antes && antes.instalado)),
        aberturas: ((antes && antes.aberturas) || 0) + 1,
        primeiro: (antes && antes.primeiro) || agora,
        ultimo: agora,
        cidade: req.cf && req.cf.city ? String(req.cf.city).slice(0, 40) : (antes && antes.cidade) || ''
      };
      await env.FORUM_APP.put(chave, JSON.stringify(reg));
      return json({ ok: true, novo: !antes }, origin);
    }

    if ((url.pathname === '/resumo' || url.pathname === '/csv') && req.method === 'GET') {
      if (url.searchParams.get('pin') !== env.PAINEL_PIN) return json({ erro: 'pin' }, origin, 403);
      const chaves = await todos(env);
      const regs = [];
      for (let i = 0; i < chaves.length; i += 30) {
        const parte = await Promise.all(chaves.slice(i, i + 30).map(k => env.FORUM_APP.get(k, 'json')));
        for (const r of parte) if (r) regs.push(r);
      }
      regs.sort((a, b) => (b.primeiro || '').localeCompare(a.primeiro || ''));
      if (url.pathname === '/csv') {
        const esc = v => '"' + String(v == null ? '' : v).replace(/"/g, '""') + '"';
        const linhas = [['Nome', 'Empresa', 'Cargo', 'E-mail', 'WhatsApp', 'Perfil', 'Instalado', 'Aparelho', 'Cidade', 'Aberturas', 'Primeiro acesso', 'Ultimo acesso'].join(',')];
        for (const r of regs) linhas.push([r.nome, r.empresa, r.cargo, r.email, r.fone, r.tipo, r.instalado ? 'sim' : 'nao', r.plataforma, r.cidade, r.aberturas, r.primeiro, r.ultimo].map(esc).join(','));
        return new Response('﻿' + linhas.join('\n'), { headers: { 'Content-Type': 'text/csv; charset=utf-8', 'Content-Disposition': 'attachment; filename="app-forum-acatmar.csv"', ...cors(origin) } });
      }
      return json({
        total: regs.length,
        instalados: regs.filter(r => r.instalado).length,
        identificados: regs.filter(r => r.nome).length,
        lista: regs
      }, origin);
    }

    if (url.pathname === '/voto' && req.method === 'POST') {
      let b;
      try { b = await req.json(); } catch (e) { return json({ erro: 'json' }, origin, 400); }
      const enq = lim(b.enquete, 40);
      const id = lim(b.id, 40);
      const opc = Number(b.opcao);
      if (!enq || !id) return json({ erro: 'dados' }, origin, 400);
      if (!Number.isInteger(opc) || opc < 0 || opc > 15) return json({ erro: 'opcao' }, origin, 400);
      await env.FORUM_APP.put('v:' + enq + ':' + id, '1', { metadata: { o: opc } });
      const res = await apurar(env, enq);
      return json({ ok: true, ...res }, origin);
    }

    if (url.pathname === '/enquete' && req.method === 'GET') {
      const enq = lim(url.searchParams.get('id') || '', 40);
      if (!enq) return json({ erro: 'id' }, origin, 400);
      const res = await apurar(env, enq);
      return json(res, origin);
    }

    return json({ erro: 'rota' }, origin, 404);
  }
};
