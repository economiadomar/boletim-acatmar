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
ALT = {'Patrocínio': 170, 'Realização': 100}
ALT_PADRAO = 85           # apoios
ESCALA_SITE = 0.62        # imagem -> pixels na tela
LARG_MAX = 520; GAP = 56; PAD = 24
SLUG = {'Patrocínio': 'patrocinio',
        'Realização': 'realizacao', 'Apoio oficial': 'apoio-oficial', 'Apoio institucional': 'apoio-institucional'}
EN = {'Patrocínio': 'Sponsorship', 'Realização': 'Organization',
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

# 0) Patrocinio em 1o lugar: Prefeitura e Floripa lado a lado, logos ORIGINAIS (copiadas de app/media/logos), acima da arte
TOPO = [p for c in D['patrocinadores'] for p in c['empresas'] if p.get('topo')]
INST = next(p for p in TOPO if p.get('institucional'))
def _img(p, alt_h):
    return '<img loading="lazy" src="' + p['logo'] + '" alt="' + html.escape(p['nome']) + '" style="height:%dpx;width:auto;max-width:46%%;display:block">' % alt_h
def bloco_inst(en, inline=False):
    rot = 'Sponsorship' if en else 'Patrocínio'
    logos = '<div style="display:flex;justify-content:center;align-items:center;gap:30px;flex-wrap:wrap">' + ''.join(_img(p, 46 if p['nome'] == 'Floripa' else 54) for p in TOPO) + '</div>'
    if inline:
        return ('<div style="margin-bottom:1.6rem"><p style="margin:0 0 .9rem;font-family:\'Barlow Condensed\',sans-serif;font-size:.82rem;letter-spacing:.14em;text-transform:uppercase;color:#5b6b7c">' + rot + '</p>'
                '<a href="' + INST['site'] + '" target="_blank" rel="noopener" style="display:block">' + logos + '</a></div>')
    return ('<div class="creditos-bloco"><p class="creditos-rotulo" data-en="Sponsorship">Patrocínio</p>'
            '<a href="' + INST['site'] + '" target="_blank" rel="noopener" style="display:block">' + logos + '</a></div>')

# 1) pagina de inscricao — arte unica feita pela ACATMAR (media/quem-faz-acontecer.jpg)
ARTE = 'media/quem-faz-acontecer.jpg'
ALT_ARTE_PT = 'Quem faz o VI Fórum acontecer: patrocinadores e apoiadores'
ALT_ARTE_EN = 'Who makes the VI Forum happen: sponsors and supporters'
h = open(os.path.join(RAIZ, 'vi-forum-2026.html'), encoding='utf-8').read()
sec = ('<!-- creditos:inicio --><section class="creditos-forum"><div class="creditos-inner">\n'
       '    <h2 class="creditos-titulo" data-en="Who makes the VI Forum happen">Quem faz o VI Fórum acontecer</h2>\n'
       '    ' + bloco_inst(False) + '\n'
       '    <img class="creditos-arte" loading="lazy" src="%s" alt="%s" style="width:100%%;max-width:560px;height:auto;display:block;margin:0 auto">\n'
       '  </div></section><!-- creditos:fim -->' % (ARTE, html.escape(ALT_ARTE_PT)))
if '<!-- creditos:inicio -->' in h:
    h = re.sub(r'<!-- creditos:inicio -->.*?<!-- creditos:fim -->', lambda m: sec, h, flags=re.S)
else:
    h = re.sub(r'<section class="creditos-forum">.*?</section>', lambda m: sec, h, count=1, flags=re.S)
open(os.path.join(RAIZ, 'vi-forum-2026.html'), 'w', encoding='utf-8').write(h)

# 2) bloco para projeto e materia
def bloco(en):
    tit = 'Who makes the VI Forum happen' if en else 'Quem faz o VI Fórum acontecer'
    alt = ALT_ARTE_EN if en else ALT_ARTE_PT
    return ('<div style="background:#fff;border:1px solid #e3e8ee;border-radius:14px;padding:20px 16px;margin:1.8rem 0;'
            'text-align:center"><div style="font-family:\'Oswald\',sans-serif;font-weight:600;text-transform:uppercase;'
            'color:#0a2540;font-size:1.05rem;letter-spacing:.03em;margin-bottom:1.3rem">' + tit + '</div>'
            + bloco_inst(en, inline=True) +
            '<img loading="lazy" src="' + ARTE + '" alt="' + html.escape(alt) + '" '
            'style="width:100%;max-width:520px;height:auto;display:block;margin:0 auto"></div>')

for arq, chave, ident in (('projetos.json', 'projetos', 'vi-forum-acatmar-2026'), ('noticias.json', 'noticias', 'vi-forum-2026'), ('noticias.json', 'noticias', 'vi-forum-acatmar-recorde-229-inscritos-2026')):
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
