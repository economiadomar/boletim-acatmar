# -*- coding: utf-8 -*-
"""Patrocinadores do VI Forum no SITE, a partir de app/data/forum.json.
Gera as imagens por cota (media/logos/vi-forum-*.png) com a hierarquia de tamanhos
e escreve o bloco na pagina de inscricao (vi-forum-2026.html), na pagina do projeto
e na materia do Forum. Roda dentro do publicar.sh."""
import json, os, re, html
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FJ = os.path.join(RAIZ, 'app/data/forum.json')
D = json.load(open(FJ, encoding='utf-8'))

# altura da logo por cota (px no espaco da imagem) = hierarquia
ALT = {'Patrocínio institucional': 170, 'Patrocínio': 140, 'Realização': 105}
ALT_PADRAO = 85           # apoios
ESCALA_SITE = 0.62        # imagem -> pixels na tela
LARG_MAX = 1000; GAP = 56; PAD = 24
SLUG = {'Patrocínio institucional': 'patrocinio-institucional', 'Patrocínio': 'patrocinio',
        'Realização': 'realizacao', 'Apoio oficial': 'apoio-oficial', 'Apoio institucional': 'apoio-institucional'}
EN = {'Patrocínio institucional': 'Institutional sponsor', 'Patrocínio': 'Sponsorship', 'Realização': 'Organization',
      'Apoio oficial': 'Official support', 'Apoio institucional': 'Institutional support'}

def logo(cam, alt):
    im = Image.open(os.path.join(RAIZ, 'app', cam)).convert('RGBA')
    b = Image.new('RGB', im.size, (255, 255, 255)); b.paste(im, mask=im.split()[3])
    r = alt / b.height
    return b.resize((max(1, int(b.width * r)), alt), Image.LANCZOS)

def composite(cota):
    base = ALT.get(cota['cota'], ALT_PADRAO)
    ims = [logo(e['logo'], int(base * (e.get('escala') or 1))) for e in cota['empresas'] if e.get('logo')]
    linhas, atual, larg = [], [], 0
    for im in ims:                                     # quebra em linhas
        w = im.width + (GAP if atual else 0)
        if atual and larg + w > LARG_MAX: linhas.append(atual); atual, larg = [], 0; w = im.width
        atual.append(im); larg += w
    if atual: linhas.append(atual)
    W = max(sum(i.width for i in l) + GAP * (len(l) - 1) for l in linhas) + PAD * 2
    H = sum(max(i.height for i in l) for l in linhas) + GAP // 2 * (len(linhas) - 1) + PAD * 2
    bg = Image.new('RGB', (W, H), (255, 255, 255)); y = PAD
    for l in linhas:
        lw = sum(i.width for i in l) + GAP * (len(l) - 1); x = (W - lw) // 2; h = max(i.height for i in l)
        for i in l: bg.paste(i, (x, y + (h - i.height) // 2)); x += i.width + GAP
        y += h + GAP // 2
    nome = 'vi-forum-%s.png' % SLUG[cota['cota']]
    bg.save(os.path.join(RAIZ, 'media/logos', nome), optimize=True)
    return nome, int(W * ESCALA_SITE), ', '.join(e['nome'] for e in cota['empresas'])

# imagens por cota + campos legados usados por versoes antigas do app
saidas = []
for c in D['patrocinadores']:
    nome, larg, alt = composite(c)
    c['logo'] = '../media/logos/' + nome; c['alt'] = alt; c['largura'] = larg
    saidas.append((c['cota'], nome, larg, alt))
json.dump(D, open(FJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 1) pagina de inscricao
h = open(os.path.join(RAIZ, 'vi-forum-2026.html'), encoding='utf-8').read()
sec = '<!-- creditos:inicio --><section class="creditos-forum"><div class="creditos-inner">\n' \
      '    <h2 class="creditos-titulo" data-en="Who makes the VI Forum happen">Quem faz o VI Fórum acontecer</h2>\n'
for cota, nome, larg, alt in saidas:
    sec += ('    <div class="creditos-bloco"><p class="creditos-rotulo" data-en="%s">%s</p>'
            '<img class="creditos-logo" loading="lazy" src="media/logos/%s" alt="%s" style="width:%dpx"></div>\n'
            % (EN[cota], cota, nome, html.escape(alt), larg))
sec += '  </div></section><!-- creditos:fim -->'
if '<!-- creditos:inicio -->' in h:
    h = re.sub(r'<!-- creditos:inicio -->.*?<!-- creditos:fim -->', lambda m: sec, h, flags=re.S)
else:
    h = re.sub(r'<section class="creditos-forum">.*?</section>', lambda m: sec, h, count=1, flags=re.S)
open(os.path.join(RAIZ, 'vi-forum-2026.html'), 'w', encoding='utf-8').write(h)

# 2) bloco para projeto e materia
def bloco(en):
    tit = 'Who makes the VI Forum happen' if en else 'Quem faz o VI Fórum acontecer'
    b = ('<div style="background:#fff;border:1px solid #e3e8ee;border-radius:14px;padding:20px 16px 6px;margin:1.8rem 0;'
         'text-align:center"><div style="font-family:\'Oswald\',sans-serif;font-weight:600;text-transform:uppercase;'
         'color:#0a2540;font-size:1.05rem;letter-spacing:.03em;margin-bottom:1.3rem">' + tit + '</div>')
    for cota, nome, larg, alt in saidas:
        b += ('<div style="margin-bottom:1.5rem"><p style="margin:0 0 .7rem;font-family:\'Barlow Condensed\',sans-serif;'
              'font-size:.82rem;letter-spacing:.14em;text-transform:uppercase;color:#5b6f7a">' + (EN[cota] if en else cota) +
              '</p><img loading="lazy" src="media/logos/' + nome + '" alt="' + html.escape(alt) + '" style="width:' +
              str(larg) + 'px;max-width:100%;height:auto;display:block;margin:0 auto"></div>')
    return b + '</div>'

for arq, chave, ident in (('projetos.json', 'projetos', 'vi-forum-acatmar-2026'), ('noticias.json', 'noticias', 'vi-forum-2026')):
    cam = os.path.join(RAIZ, arq); j = json.load(open(cam, encoding='utf-8'))
    for x in j[chave]:
        if x['id'] != ident: continue
        for campo, en in (('corpo', False), ('corpo_en', True)):
            if campo not in x: continue
            marca = 'Who makes the VI' if en else 'Quem faz o VI'
            idx = [i for i, t in enumerate(x[campo]) if marca in t]
            if idx: x[campo][idx[0]] = bloco(en)
            else: x[campo].append(bloco(en))
    json.dump(j, open(cam, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print('patrocinadores do Fórum no site: ' + ', '.join('%s (%d)' % (c, len([e for e in D['patrocinadores'] if e['cota'] == c][0]['empresas'])) for c, _, _, _ in saidas))
