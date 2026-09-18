# -*- coding: utf-8 -*-
"""Gera o bloco "Palestrantes confirmados" na pagina do projeto do VI Forum,
a partir de app/data/forum.json. Rodar sempre que entrar palestrante novo:
    python3 tools/bloco-palestrantes.py && ./publicar.sh "..."
"""
import json, os, html

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(RAIZ, 'app/data/forum.json'), encoding='utf-8'))
MARCA_PT, MARCA_EN = 'Palestrantes confirmados', 'Confirmed speakers'

def ordem(p):
    h = (p.get('hora') or '').replace('h', ':')[:5]
    return (0, h) if h and h[0].isdigit() else (1, p['nome'])

def bloco(en=False):
    ps = sorted([p for p in D.get('palestrantes', []) if p.get('tema')], key=ordem)
    if not ps: return None
    tit = MARCA_EN if en else MARCA_PT
    sub = ('New names are announced first on the official event app.' if en
           else 'Novos nomes são anunciados em primeira mão no aplicativo oficial do evento.')
    h = ('<div style="margin:1.8rem 0">'
         '<div style="font-family:\'Oswald\',sans-serif;font-weight:600;text-transform:uppercase;color:#0a2540;'
         'font-size:1.05rem;letter-spacing:.03em;margin:0 0 .4rem">' + tit + '</div>'
         '<p style="margin:0 0 1.1rem;color:#5b6f7a;font-size:.95rem">' + sub + '</p>')
    for p in ps:
        hora = p.get('hora') or ('Time to be confirmed' if en else 'Horário a confirmar')
        sub2 = ' · '.join(x for x in [p.get('cargo'), p.get('empresa')] if x)
        h += ('<div style="display:flex;gap:14px;align-items:center;background:#fff;border:1px solid #e3e8ee;'
              'border-left:4px solid #00a3b4;border-radius:12px;padding:12px 14px;margin:0 0 10px">'
              '<img loading="lazy" src="/app/' + p['foto'] + '" alt="' + html.escape(p['nome']) + '" '
              'style="width:62px;height:62px;border-radius:50%;object-fit:cover;flex:0 0 62px">'
              '<div style="flex:1;min-width:0">'
              '<div style="font-weight:700;color:#0a2540;line-height:1.25">' + html.escape(p['tema']) + '</div>'
              '<div style="color:#33454f;font-size:.93rem;margin-top:3px">' + html.escape(p['nome']) +
              ('<span style="color:#5b6f7a"> · ' + html.escape(sub2) + '</span>' if sub2 else '') + '</div>'
              '<div style="color:#00727e;font-size:.88rem;margin-top:2px">' + html.escape(hora) + '</div>'
              '</div></div>')
    return h + '</div>'

arq = os.path.join(RAIZ, 'projetos.json')
j = json.load(open(arq, encoding='utf-8'))
for x in j['projetos']:
    if x['id'] != 'vi-forum-acatmar-2026': continue
    for campo, en, marca in (('corpo', False, MARCA_PT), ('corpo_en', True, MARCA_EN)):
        if campo not in x: continue
        b = bloco(en)
        if not b: continue
        x[campo] = [t for t in x[campo] if marca not in t]
        alvo = [i for i, t in enumerate(x[campo]) if ('Who makes the VI' if en else 'Quem faz o VI') in t]
        x[campo].insert(alvo[0] if alvo else len(x[campo]), b)
    print('palestrantes no site:', len([p for p in D.get('palestrantes', []) if p.get('tema')]))
json.dump(j, open(arq, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
