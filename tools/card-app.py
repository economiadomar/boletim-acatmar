# -*- coding: utf-8 -*-
"""Cards 4:5 (1080x1350) do app do VI Forum: 'Baixe ja o app' e 'Como instalar'.
Painel de patrocinadores no estilo linhas/rotulos, com a escala otica de forum.json.
Uso: python3 tools/card-app.py  -> media/cards/app-baixe.jpg e app-como-instalar.jpg"""
import json, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(RAIZ, 'app/data/forum.json'), encoding='utf-8'))
L, A = 1080, 1350
NAVY = (10, 37, 64); TEAL = (0, 163, 180); DEEP = (5, 12, 26)

def F(nome, tam):
    cam = {'osw': 'assets/fonts/Oswald.ttf', 'bar': 'assets/fonts/BarlowCondensed-SemiBold.ttf'}.get(nome)
    if cam: return ImageFont.truetype(os.path.join(RAIZ, cam), tam)
    m = {'black': 'Arial Black', 'ab': 'Arial Bold', 'a': 'Arial'}[nome]
    return ImageFont.truetype('/System/Library/Fonts/Supplemental/%s.ttf' % m, tam)

def logo(cam, alt):
    im = Image.open(os.path.join(RAIZ, 'app', cam)).convert('RGBA')
    b = Image.new('RGB', im.size, (255, 255, 255)); b.paste(im, mask=im.split()[3])
    return b.resize((max(1, int(b.width * alt / b.height)), alt), Image.LANCZOS)

def fundo():
    ph = Image.open(os.path.join(RAIZ, 'media/noticias/itajai-marina-aerea.jpg')).convert('RGB')
    r = max(L / ph.width, A / ph.height); ph = ph.resize((int(ph.width * r), int(ph.height * r)), Image.LANCZOS)
    x = (ph.width - L) // 2; ph = ph.crop((x, 0, x + L, A)).filter(ImageFilter.GaussianBlur(1.2))
    tint = Image.new('RGB', (L, A), (8, 40, 80)); ph = Image.blend(ph, tint, 0.42)
    mask = Image.new('L', (L, A)); md = ImageDraw.Draw(mask)
    for y in range(A):           # escurece topo e base para o texto e o painel
        t = min(1, (abs(y - A * 0.42) / (A * 0.42)) ** 1.6) * 0.5
        md.line([(0, y), (L, y)], fill=int(255 * t))
    return Image.composite(Image.new('RGB', (L, A), (3, 10, 22)), ph, mask)

def emblema_topo(im):
    arte = Image.open(os.path.join(RAIZ, 'media/noticias/vi-forum-2026.jpg')).convert('RGB')
    emb = arte.crop((55, 20, 875, 925)); emb = emb.resize((int(820 * 300 / 905), 300), Image.LANCZOS)
    borda = emb.crop((0, 0, 6, emb.height)).resize((1, 1)).getpixel((0, 0))
    pw = emb.width + 56; painel = Image.new('RGB', (pw, 340), borda)
    painel.paste(emb, ((pw - emb.width) // 2, 18))
    im.paste(painel, ((L - pw) // 2, 0))

def sombra_txt(d, xy, s, f, cor=(255, 255, 255)):
    x, y = xy
    for dx, dy in ((0, 6), (4, 6), (-4, 6)): d.text((x + dx, y + dy), s, font=f, fill=(6, 20, 40))
    d.text((x, y), s, font=f, fill=cor)

def centro(d, y, s, f, cor=(255, 255, 255), sombra=True):
    w = d.textbbox((0, 0), s, font=f)[2]
    (sombra_txt if sombra else lambda d, xy, s, f, cor: d.text(xy, s, font=f, fill=cor))(d, ((L - w) // 2, y), s, f, cor)
    return d.textbbox((0, 0), s, font=f)[3]

BASE = {'Patrocínio': 92, 'Realização': 50}
def grupo(cota):
    c = [c for c in D['patrocinadores'] if c['cota'] == cota][0]
    ims = [logo(e['logo'], int(BASE.get(cota, 40) * (e.get('escala') or 1))) for e in c['empresas'] if e.get('logo')]
    return ims

def painel_patrocinio(im, y0, alt):
    px, pw = 40, L - 80
    p = Image.new('RGB', (pw, alt), (255, 255, 255)); d = ImageDraw.Draw(p)
    fl = F('a', 20); cinza = (70, 80, 90)
    def linha(y, grupos, gap=26):
        # grupos: lista de (rotulo, [imgs]); distribui centralizado na largura
        larg = [sum(i.width for i in ims) + gap * (len(ims) - 1) for _, ims in grupos]
        total = sum(larg) + 70 * (len(grupos) - 1)
        x = (pw - total) // 2; h = max(i.height for _, ims in grupos for i in ims)
        for (rot, ims), lw in zip(grupos, larg):
            d.text((x, y), rot, font=fl, fill=cinza)
            xx = x
            for i in ims: p.paste(i, (xx, y + 34 + (h - i.height) // 2)); xx += i.width + gap
            x += lw + 70
        return y + 34 + h
    y = 26
    y = linha(y, [('Patrocínio:', grupo('Patrocínio'))])
    y += 22; d.line([(30, y), (pw - 30, y)], fill=(215, 222, 230), width=2); y += 16
    y = linha(y, [('Realização:', grupo('Realização')), ('Apoio oficial:', grupo('Apoio oficial'))], gap=20)
    y += 22; d.line([(30, y), (pw - 30, y)], fill=(215, 222, 230), width=2); y += 16
    y = linha(y, [('Apoio institucional:', grupo('Apoio institucional'))], gap=28)
    p = p.crop((0, 0, pw, y + 26))
    # cantos arredondados
    mask = Image.new('L', p.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, p.height - 1], 28, fill=255)
    im.paste(p, (px, A - p.height - 28), mask)
    return p.height

def card_baixe():
    im = fundo(); emblema_topo(im); d = ImageDraw.Draw(im)
    y = 372
    y += centro(d, y, 'Baixe já o app', F('black', 118)) + 2
    y += centro(d, y, 'do evento!', F('black', 118)) + 26
    s = 'SAIBA COMO FAZER'; f = F('bar', 52); w = d.textbbox((0, 0), s, font=f)[2]
    pw, ph = w + 150, 90; x0 = (L - pw) // 2
    d.rounded_rectangle([x0, y, x0 + pw, y + ph], 18, fill=NAVY); d.text((x0 + 44, y + 17), s, font=f, fill=(255, 255, 255))
    ax, ay = x0 + pw - 82, y + ph // 2       # seta
    d.line([(ax, ay), (ax + 42, ay)], fill=(255, 255, 255), width=8)
    d.polygon([(ax + 30, ay - 18), (ax + 56, ay), (ax + 30, ay + 18)], fill=(255, 255, 255))
    y += ph + 18
    centro(d, y, 'acatmar.org/app  ·  iPhone e Android, sem loja de aplicativos', F('ab', 28))
    painel_patrocinio(im, A - 440, 470)
    im.save(os.path.join(RAIZ, 'media/cards/app-baixe.jpg'), quality=93); print('app-baixe.jpg')

def card_como():
    im = fundo(); emblema_topo(im); d = ImageDraw.Draw(im)
    y = 366
    y += centro(d, y, 'Como instalar o app', F('black', 80)) + 18
    # caixa branca translucida com duas colunas
    bx, by, bw, bh = 40, y, L - 80, 322
    cx = Image.new('RGBA', (bw, bh), (255, 255, 255, 236)); im.paste(cx, (bx, by), cx)
    d = ImageDraw.Draw(im)
    col = bw // 2
    def coluna(x, titulo, passos):
        d.text((x + 28, by + 22), titulo, font=F('bar', 40), fill=NAVY)
        yy = by + 84
        for n, t in enumerate(passos, 1):
            d.ellipse([x + 28, yy, x + 66, yy + 38], fill=TEAL)
            d.text((x + 39, yy + 4), str(n), font=F('ab', 26), fill=(255, 255, 255))
            for k, ln in enumerate(t):
                d.text((x + 82, yy + 2 + k * 30), ln, font=F('ab' if k == 0 else 'a', 26), fill=(20, 30, 40))
            yy += 44 + 30 * (len(t) - 1) + 14
    coluna(bx, 'iPhone  (Safari)', [['Abra acatmar.org/app', 'no Safari'],
                                     ['Toque em Compartilhar', '(quadrado com seta, na barra)'],
                                     ['Toque em "Adicionar', 'à Tela de Início"']])
    d.line([(bx + col, by + 24), (bx + col, by + bh - 24)], fill=(205, 214, 224), width=2)
    coluna(bx + col, 'Android  (Chrome)', [['Abra acatmar.org/app', 'no Chrome'],
                                           ['Toque em "Instalar"', 'no aviso que aparece'],
                                           ['Pronto: o ícone fica', 'na tela inicial']])
    y = by + bh + 16
    centro(d, y, 'Programação, avisos, credencial com QR Code e certificado', F('ab', 26))
    painel_patrocinio(im, A - 440, 470)
    im.save(os.path.join(RAIZ, 'media/cards/app-como-instalar.jpg'), quality=93); print('app-como-instalar.jpg')

card_baixe(); card_como()
