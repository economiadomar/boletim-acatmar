#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera a agenda do VI Fórum (programação + palestrantes) na pagina vi-forum-2026.html
a partir de app/data/forum.json, entre os marcadores <!-- agenda:inicio --> e <!-- agenda:fim -->.
Rodar sempre no publicar.sh, depois de editar o forum.json."""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAG  = os.path.join(ROOT, 'vi-forum-2026.html')
DADOS= os.path.join(ROOT, 'app', 'data', 'forum.json')
e = lambda s: html.escape(str(s or ''))

PERIODO_EN = {'Manhã': 'Morning', 'Tarde': 'Afternoon', 'Noite': 'Evening'}
ICONE = {'org': '⚓', 'pausa': '☕', 'bloco': '🎯', 'palestra': '🎤'}

def main():
    d = json.load(open(DADOS, encoding='utf-8'))
    prog = d.get('programacao') or []
    spks = d.get('palestrantes') or []

    out = ['<section class="agenda" id="programacao"><div class="agenda-inner">']
    out.append('<h2 class="agenda-titulo" data-en="Program">Programação</h2>')
    if d.get('programacao_status') == 'preliminar':
        aviso = d.get('programacao_aviso') or 'Programação preliminar.'
        # o texto do JSON e escrito para dentro do app; no site vira 'no app do Forum'
        aviso = aviso.replace('aqui no app', 'no app do Fórum').replace('aqui no aplicativo', 'no app do Fórum')
        out.append('<p class="agenda-aviso" data-en="Preliminary program. Talks and speakers are confirmed first-hand in the Forum app.">'+e(aviso)+'</p>')

    porid = {s.get('id'): s for s in spks if s.get('id')}

    periodo = None
    for it in prog:
        p = it.get('periodo')
        if p != periodo:
            periodo = p
            out.append('<div class="ag-per"><span data-en="'+e(PERIODO_EN.get(p, p))+'">'+e(p)+'</span></div>')
        cls = ' ag-' + e(it.get('tipo') or 'org')
        desc = '<span class="ag-desc">'+e(it['desc'])+'</span>' if it.get('desc') else ''
        # palestra com palestrante confirmado leva a foto redonda no lugar do icone
        s = porid.get(it.get('palestrante'))
        if s and s.get('foto'):
            rosto = ('<img class="ag-item-foto" loading="lazy" src="app/'+e(s['foto'])+'" alt="'+e(s.get('nome'))+'">')
            marca = ''
        else:
            rosto = ''
            marca = ICONE.get(it.get('tipo'), '•') + ' '
        out.append('<div class="ag-item'+cls+'"><div class="ag-hora">'+e(it.get('hora'))+'</div>'+rosto+
                   '<div class="ag-txt"><b>'+marca+e(it.get('titulo'))+'</b>'
                   '<span class="ag-quem">'+e(it.get('quem'))+'</span>'+desc+'</div></div>')

    if spks:
        out.append('<h2 class="agenda-titulo ag-h2b" data-en="Confirmed speakers">Palestrantes confirmados</h2>')
        out.append('<div class="ag-spks">')
        for s in spks:
            foto = 'app/' + s['foto'] if s.get('foto') else ''
            img = ('<img class="ag-foto" loading="lazy" src="'+e(foto)+'" alt="'+e(s.get('nome'))+'">'
                   if foto else '<div class="ag-foto ag-foto-vazia">'+e((s.get('nome') or '?')[0])+'</div>')
            cargo = ' · '.join([x for x in [s.get('cargo'), s.get('empresa')] if x])
            hora = '<span class="ag-spk-hora">'+e(s['hora'])+'</span>' if s.get('hora') else ''
            out.append('<div class="ag-spk">'+img+'<b>'+e(s.get('nome'))+'</b>'
                       '<span class="ag-cargo">'+e(cargo)+'</span>'
                       '<span class="ag-tema">'+e(s.get('tema'))+'</span>'+hora+'</div>')
        out.append('</div>')

    out.append('<p class="agenda-pe"><a href="app/" data-en="Full program, updates and your credential are in the Forum app">'
               'A programação completa, as atualizações e a sua credencial ficam no app do Fórum</a></p>')
    out.append('</div></section>')
    novo = ''.join(out)

    t = open(PAG, encoding='utf-8').read()
    m = re.search(r'(<!-- agenda:inicio -->).*?(<!-- agenda:fim -->)', t, re.S)
    if not m:
        raise SystemExit('marcadores <!-- agenda:inicio --> / <!-- agenda:fim --> nao encontrados em vi-forum-2026.html')
    t = t[:m.start()] + '<!-- agenda:inicio -->' + novo + '<!-- agenda:fim -->' + t[m.end():]
    open(PAG, 'w', encoding='utf-8').write(t)
    print(f'agenda do Fórum: {len(prog)} itens de programação e {len(spks)} palestrantes na página')

if __name__ == '__main__':
    main()
