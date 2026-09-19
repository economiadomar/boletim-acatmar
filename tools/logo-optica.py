# -*- coding: utf-8 -*-
"""Calibra o tamanho OTICO das logos (mesmo peso visual dentro da cota).
Mede proporcao (largura/altura) e densidade de tinta de cada logo e calcula 'escala'
em app/data/forum.json. Ver preview em media/cards/preview-logos.jpg."""
import json, os, math
from PIL import Image, ImageDraw
import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FJ = os.path.join(RAIZ, 'app/data/forum.json')
D = json.load(open(FJ, encoding='utf-8'))
H0 = {'Patrocínio institucional': 100, 'Patrocínio': 88, 'Realização': 56}   # alturas-base no app (px)
H0_PADRAO = 50
REF_R, REF_F = 2.5, 0.45      # logo "tipica" (palavra larga) que fica exatamente em H0
EXP = 0.38                    # forca da correcao otica (0 = altura igual; 0.5 = area de tinta igual)
LIM = (0.82, 1.32)            # limites da correcao

def metrica(cam):
    im = Image.open(os.path.join(RAIZ, 'app', cam)).convert('RGBA'); a = np.array(im)
    tinta = (a[:, :, 3] > 25) & (a[:, :, :3].astype(int).sum(axis=2) < 700)
    ys, xs = np.where(tinta)
    w, h = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
    f = tinta.sum() / (w * h)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)), w / h, f

def escala(r, f, piso=LIM[0]):
    e = ((REF_R * REF_F) / (r * f)) ** EXP
    return round(min(LIM[1], max(piso, e)), 2)

linhas = []
for c in D['patrocinadores']:
    base = H0.get(c['cota'], H0_PADRAO)
    for e in c['empresas']:
        if not e.get('logo'): continue
        im, r, f = metrica(e['logo'])
        e['escala'] = escala(r, f, 1.0 if c['cota'] == 'Patrocínio institucional' else LIM[0])
        linhas.append((c['cota'], e['nome'], im, r, f, e['escala'], int(base * e['escala'])))
json.dump(D, open(FJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# preview no tamanho do app (largura 375) x2 para nitidez
S = 2; W = 375 * S
alt = 40 * S + sum(0 for _ in linhas)
blocos = {}
for cota, nome, im, r, f, esc, hpx in linhas: blocos.setdefault(cota, []).append((im, hpx * S, nome, r, f, esc))
Hs = []
for cota, itens in blocos.items():
    h = max(x[1] for x in itens); n = len(itens)
    por_linha = 1 if cota in ('Patrocínio institucional', 'Patrocínio') else 2
    Hs.append(40 * S + math.ceil(n / por_linha) * (h + 22 * S))
img = Image.new('RGB', (W, sum(Hs) + 20 * S), (255, 255, 255)); d = ImageDraw.Draw(img); y = 10 * S
for (cota, itens), Hc in zip(blocos.items(), Hs):
    d.text((W // 2 - len(cota) * 3 * S, y), cota.upper(), fill=(120, 136, 148)); y += 26 * S
    por_linha = 1 if cota in ('Patrocínio institucional', 'Patrocínio') else 2
    h = max(x[1] for x in itens)
    for i in range(0, len(itens), por_linha):
        fila = itens[i:i + por_linha]; cw = W // por_linha
        for j, (im, hp, nome, r, f, esc) in enumerate(fila):
            ww = int(im.width * hp / im.height)
            if ww > cw - 30 * S: ww = cw - 30 * S; hp = int(im.height * ww / im.width)
            g = im.resize((ww, hp), Image.LANCZOS)
            x = j * cw + (cw - ww) // 2
            bg = Image.new('RGB', g.size, (255, 255, 255)); bg.paste(g, mask=g.split()[3]); img.paste(bg, (x, y + (h - hp) // 2))
        y += h + 22 * S
img.save(os.path.join(RAIZ, 'media/cards/preview-logos.jpg'), quality=88)
for cota, nome, im, r, f, esc, hpx in linhas:
    print('%-24s %-32s prop %.2f  tinta %.2f  escala %.2f  -> %3d px' % (cota[:24], nome[:32], r, f, esc, hpx))
