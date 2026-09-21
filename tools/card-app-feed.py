# -*- coding: utf-8 -*-
"""Dois cards 1080x1080 para o feed: (1) Baixe ja o app  (2) Como instalar.
Linha visual: foto do IFSC, emblema do Forum, bloco de data, frase manuscrita,
celular com o app, icones, painel branco ondulado com as cotas, rodape.
Uso: python3 tools/card-app-feed.py -> media/cards/feed-app-1.jpg / feed-app-2.jpg"""
import json, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(RAIZ, 'app/data/forum.json'), encoding='utf-8'))
L = A = 1080
NAVY = (10, 37, 64); DEEP = (4, 14, 30); CYAN = (53, 201, 218); CYAN2 = (0, 163, 180); BR = (255, 255, 255)
SYS = '/System/Library/Fonts/Supplemental/'

def F(n, t):
    cam = {'osw': RAIZ + '/assets/fonts/Oswald.ttf', 'bar': RAIZ + '/assets/fonts/BarlowCondensed-SemiBold.ttf',
           'black': SYS + 'Arial Black.ttf', 'ab': SYS + 'Arial Bold.ttf', 'a': SYS + 'Arial.ttf',
           'script': SYS + 'SnellRoundhand.ttc'}[n]
    f = ImageFont.truetype(cam, t)
    if n == 'script':
        try: f = ImageFont.truetype(cam, t, index=2)   # Snell Roundhand Black
        except Exception: pass
    return f

def logo(cam, alt):
    im = Image.open(os.path.join(RAIZ, 'app', cam)).convert('RGBA')
    b = Image.new('RGB', im.size, BR); b.paste(im, mask=im.split()[3])
    return b.resize((max(1, int(b.width * alt / b.height)), alt), Image.LANCZOS)

def tw(d, s, f): return d.textbbox((0, 0), s, font=f)[2]
def sombra(d, xy, s, f, cor=BR, forca=3):
    x, y = xy
    for dx, dy in ((0, forca + 1), (forca, forca), (-forca, forca)): d.text((x + dx, y + dy), s, font=f, fill=(3, 12, 26))
    d.text((x, y), s, font=f, fill=cor)

# ---------- base: foto + escurecimentos + emblema + tagline ----------
def base(topo_escuro=0.75):
    ph = Image.open(os.path.join(RAIZ, 'media/noticias/ifsc-continente-marina-escola-2026.jpg')).convert('RGB')
    r = 1180 / ph.width; ph = ph.resize((int(ph.width * r), int(ph.height * r)), Image.LANCZOS)   # 1180x664
    im = Image.new('RGB', (L, A), DEEP)
    x = (ph.width - L) // 2; im.paste(ph.crop((x, 0, x + L, ph.height)), (0, 60))
    # ceu escuro no topo (para emblema e textos) e degrade para o painel embaixo
    mask = Image.new('L', (L, A)); md = ImageDraw.Draw(mask)
    for y in range(A):
        if y < 330: t = topo_escuro * (1 - y / 330) ** 0.7
        elif y > 560: t = min(1, (y - 560) / 170) * 0.92
        else: t = 0
        md.line([(0, y), (L, y)], fill=int(255 * t))
    im = Image.composite(Image.new('RGB', (L, A), DEEP), im, mask)
    # emblema flutuando no canto (fundo da arte funde com o ceu escurecido)
    arte = Image.open(os.path.join(RAIZ, 'media/noticias/vi-forum-2026.jpg')).convert('RGB')
    emb = arte.crop((55, 20, 875, 925)); emb = emb.resize((int(820 * 268 / 905), 268), Image.LANCZOS)
    # suaviza a borda do retangulo da arte
    fade = Image.new('L', emb.size, 255); fd = ImageDraw.Draw(fade)
    for i in range(26): fd.rectangle([i, i, emb.width - 1 - i, emb.height - 1 - i], outline=int(255 * i / 26))
    im.paste(emb, (34, 22), fade)
    d = ImageDraw.Draw(im)
    f = F('bar', 19)
    for k, s in enumerate(['CONHECIMENTO QUE FORTALECE', 'TODO O SETOR NÁUTICO']):
        d.text((34 + (emb.width - tw(d, s, f)) // 2, 292 + k * 22), s, font=f, fill=BR)
    return im, d

# ---------- icones simples ----------
def icone_circulo(d, cx, cy, r, tipo, cor=CYAN):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=cor, width=3)
    w = 3
    if tipo == 'calendario':
        d.rounded_rectangle([cx - 14, cy - 10, cx + 14, cy + 12], 3, outline=cor, width=w)
        d.line([(cx - 14, cy - 3), (cx + 14, cy - 3)], fill=cor, width=w)
        d.line([(cx - 7, cy - 15), (cx - 7, cy - 7)], fill=cor, width=w); d.line([(cx + 7, cy - 15), (cx + 7, cy - 7)], fill=cor, width=w)
        for i in range(3): d.rectangle([cx - 9 + i * 8, cy + 1, cx - 6 + i * 8, cy + 4], fill=cor)
    elif tipo == 'sino':
        d.pieslice([cx - 12, cy - 14, cx + 12, cy + 10], 180, 360, outline=cor, width=w)
        d.line([(cx - 12, cy - 2), (cx - 12, cy + 8), (cx + 12, cy + 8), (cx + 12, cy - 2)], fill=cor, width=w)
        d.ellipse([cx - 4, cy + 9, cx + 4, cy + 15], fill=cor)
    elif tipo == 'credencial':
        d.rounded_rectangle([cx - 16, cy - 11, cx + 16, cy + 11], 3, outline=cor, width=w)
        d.ellipse([cx - 11, cy - 6, cx - 3, cy + 2], outline=cor, width=2)
        d.line([(cx + 1, cy - 4), (cx + 11, cy - 4)], fill=cor, width=2); d.line([(cx + 1, cy + 3), (cx + 11, cy + 3)], fill=cor, width=2)
    elif tipo == 'certificado':
        d.rounded_rectangle([cx - 12, cy - 15, cx + 12, cy + 12], 2, outline=cor, width=w)
        for i in range(3): d.line([(cx - 7, cy - 8 + i * 6), (cx + 7, cy - 8 + i * 6)], fill=cor, width=2)
        d.ellipse([cx + 4, cy + 6, cx + 14, cy + 16], fill=cor)
    elif tipo == 'pin':
        d.ellipse([cx - 11, cy - 15, cx + 11, cy + 7], outline=cor, width=w)
        d.polygon([(cx - 7, cy + 2), (cx + 7, cy + 2), (cx, cy + 16)], fill=cor)
        d.ellipse([cx - 4, cy - 8, cx + 4, cy], fill=cor)
    elif tipo == 'check':
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cor)
        d.line([(cx - 8, cy), (cx - 2, cy + 6), (cx + 9, cy - 7)], fill=BR, width=4)

def safari(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(18, 110, 220)); d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], outline=BR, width=3)
    d.polygon([(cx + r * .55, cy - r * .55), (cx - 6, cy + 4), (cx + 4, cy - 6)], fill=(230, 50, 40))
    d.polygon([(cx - r * .55, cy + r * .55), (cx + 6, cy - 4), (cx - 4, cy + 6)], fill=BR)
def chrome(d, cx, cy, r):
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 210, 330, fill=(219, 68, 55)); d.pieslice([cx - r, cy - r, cx + r, cy + r], 330, 90, fill=(244, 180, 0))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 90, 210, fill=(15, 157, 88)); d.ellipse([cx - r * .55, cy - r * .55, cx + r * .55, cy + r * .55], fill=BR)
    d.ellipse([cx - r * .38, cy - r * .38, cx + r * .38, cy + r * .38], fill=(66, 133, 244))

TELA = os.path.expanduser('~/ACATMAR/oficios/assets/app-home.png')
if not os.path.exists(TELA): TELA = TELA
def celular(im, x, y, h, tela):
    w = int(h * 0.5); fr = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0)); fd = ImageDraw.Draw(fr)
    fd.rounded_rectangle([24, 30, w + 16, h + 24], 34, fill=(0, 0, 0, 110)); fr = fr.filter(ImageFilter.GaussianBlur(10))
    im.paste(fr, (x - 20, y - 20), fr)
    d = ImageDraw.Draw(im); d.rounded_rectangle([x, y, x + w, y + h], 30, fill=(16, 18, 24))
    scr = Image.open(tela).convert('RGB'); sw, sh = w - 16, h - 16
    scr = scr.resize((sw, int(scr.height * sw / scr.width)), Image.LANCZOS).crop((0, 0, sw, sh))
    m = Image.new('L', scr.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, sw - 1, sh - 1], 22, fill=255)
    im.paste(scr, (x + 8, y + 8), m); d.rounded_rectangle([x + w // 2 - 28, y + 12, x + w // 2 + 28, y + 20], 4, fill=(16, 18, 24))

# ---------- painel de patrocinadores com onda ----------
BASEH = {'Patrocínio': 58, 'Realização': 34}
def grupo(cota):
    c = [c for c in D['patrocinadores'] if c['cota'] == cota][0]
    return [logo(e['logo'], int(BASEH.get(cota, 29) * (e.get('escala') or 1))) for e in c['empresas'] if e.get('logo')]

def painel(im, y_top):
    d = ImageDraw.Draw(im)
    pts = [(x, y_top + 12 * math.sin(x / 95.0)) for x in range(0, L + 1, 8)] + [(L, A), (0, A)]
    d.polygon(pts, fill=BR)
    fl = F('a', 16); cz = (60, 72, 84); y = y_top + 26
    def linha(y, grupos, gap=20):
        larg = [sum(i.width for i in ims) + gap * (len(ims) - 1) for _, ims in grupos]
        total = sum(larg) + 84 * (len(grupos) - 1); x = (L - total) // 2
        h = max(i.height for _, ims in grupos for i in ims)
        for k, ((rot, ims), lw) in enumerate(zip(grupos, larg)):
            d.text((x, y), rot, font=fl, fill=cz); xx = x
            for i in ims: im.paste(i, (xx, y + 22 + (h - i.height) // 2)); xx += i.width + gap
            if k < len(grupos) - 1: d.line([(x + lw + 42, y + 2), (x + lw + 42, y + 22 + h)], fill=(190, 205, 218), width=2)
            x += lw + 84
        return y + 22 + h
    y = linha(y, [('Patrocínio:', grupo('Patrocínio'))])
    y += 9; d.line([(50, y), (L - 50, y)], fill=(215, 222, 230), width=2); y += 7
    y = linha(y, [('Realização:', grupo('Realização')), ('Apoio oficial:', grupo('Apoio oficial'))], gap=16)
    y += 9; d.line([(50, y), (L - 50, y)], fill=(215, 222, 230), width=2); y += 7
    y = linha(y, [('Apoio institucional:', grupo('Apoio institucional'))], gap=22)
    return y

def rodape(im):
    d = ImageDraw.Draw(im); d.rectangle([0, A - 52, L, A], fill=NAVY)
    f = F('bar', 22); s1, s2 = 'CAPACITAÇÃO HOJE. UM SETOR NÁUTICO SEMPRE MAIS FORTE ', 'AMANHÃ.'
    esp = lambda s: ' '.join(s)     # espacado
    w1, w2 = tw(d, esp(s1), f), tw(d, esp(s2), f); x = (L - w1 - w2) // 2
    d.text((x, A - 38), esp(s1), font=f, fill=BR); d.text((x + w1, A - 38), esp(s2), font=f, fill=CYAN)

# ---------- card 1 ----------
def card1():
    im, d = base()
    # bloco data/local (direita, topo)
    x0 = 470; d.line([(x0 - 24, 40), (x0 - 24, 240)], fill=CYAN, width=3)
    sombra(d, (x0, 36), '20 DE', F('osw', 66), CYAN); sombra(d, (x0, 100), 'OUTUBRO', F('osw', 66), BR)
    icone_circulo(d, x0 + 296, 92, 24, 'calendario')
    d.text((x0 + 328, 74), 'TERÇA-FEIRA', font=F('bar', 21), fill=BR); d.text((x0 + 328, 98), 'EVENTO GRATUITO', font=F('bar', 17), fill=(210, 225, 240))
    icone_circulo(d, x0 + 20, 208, 24, 'pin'); d.text((x0 + 56, 186), 'FLORIANÓPOLIS/SC', font=F('bar', 28), fill=BR)
    d.text((x0 + 56, 216), 'IFSC · CÂMPUS CONTINENTE', font=F('bar', 21), fill=(210, 225, 240))
    lx = 958; d.line([(lx - 20, 40), (lx - 20, 190)], fill=(120, 150, 180), width=2)
    for k, s in enumerate(['CAPACITAÇÃO', 'INOVAÇÃO', 'PESSOAS', 'NEGÓCIOS', 'UM MAR', 'MAIS FORTE']):
        d.text((lx, 40 + k * 25), s, font=F('bar', 20), fill=CYAN if k >= 4 else BR)
    fs = F('script', 38); s = 'Juntos pelo futuro da náutica!'
    txt = Image.new('RGBA', (640, 120), (0, 0, 0, 0)); td = ImageDraw.Draw(txt)
    td.text((13, 23), s, font=fs, fill=(3, 12, 26)); td.text((10, 20), s, font=fs, fill=CYAN)
    txt = txt.rotate(5, resample=Image.BICUBIC, expand=True); im.paste(txt, (222, 252), txt); d = ImageDraw.Draw(im)
    # celular com o app
    celular(im, 816, 312, 296, TELA); d = ImageDraw.Draw(im)
    f = F('bar', 24); s = 'ACATMAR.ORG/APP'; w = tw(d, s, f)
    d.rounded_rectangle([775, 616, 775 + w + 40, 654], 19, fill=BR); d.text((795, 622), s, font=f, fill=NAVY)
    # chamada
    f = F('black', 52); x, y = 44, 438
    sombra(d, (x, y), 'BAIXE JÁ O ', f); sombra(d, (x + tw(d, 'BAIXE JÁ O ', f), y), 'APP', f, CYAN)
    sombra(d, (x, y + 60), 'DO ', f); sombra(d, (x + tw(d, 'DO ', f), y + 60), 'EVENTO!', f, CYAN)
    sombra(d, (x, y + 132), 'Programação, avisos, credencial com QR Code e certificado', F('a', 23), BR, 2)
    sombra(d, (x, y + 160), 'tudo em um só lugar, na palma da sua mão.', F('a', 23), BR, 2)
    for k, (t, a, b) in enumerate([('calendario', 'PROGRAMAÇÃO', 'COMPLETA'), ('sino', 'AVISOS', 'EM TEMPO REAL'),
                                   ('credencial', 'CREDENCIAL', 'COM QR CODE'), ('certificado', 'CERTIFICADO', 'DE PARTICIPAÇÃO')]):
        cx = 76 + k * 250; icone_circulo(d, cx, 682, 25, t)
        d.text((cx + 36, 666), a, font=F('bar', 20), fill=BR); d.text((cx + 36, 688), b, font=F('bar', 17), fill=(200, 218, 235))
    painel(im, 728); rodape(im)
    im.save(os.path.join(RAIZ, 'media/cards/feed-app-1.jpg'), quality=93); print('feed-app-1.jpg')

# ---------- card 2 ----------
def card2():
    im, d = base()
    x0 = 470
    sombra(d, (x0, 30), 'COMO INSTALAR', F('osw', 58)); sombra(d, (x0, 88), 'O ', F('osw', 58))
    sombra(d, (x0 + tw(d, 'O ', F('osw', 58)), 88), 'APP DO EVENTO', F('osw', 58), CYAN)
    f = F('ab', 34); s = 'acatmar.org/app'; w = tw(d, s, f)
    d.rounded_rectangle([x0, 160, x0 + w + 110, 216], 28, fill=BR); d.text((x0 + 26, 170), s, font=f, fill=NAVY)
    d.ellipse([x0 + w + 52, 168, x0 + w + 92, 208], fill=NAVY); d.ellipse([x0 + w + 62, 178, x0 + w + 78, 194], outline=BR, width=3)
    d.line([(x0 + w + 76, 192), (x0 + w + 84, 200)], fill=BR, width=3)
    d.text((x0, 228), 'iPhone e Android, sem loja de aplicativos', font=F('a', 23), fill=BR)
    fs = F('script', 38); txt = Image.new('RGBA', (300, 170), (0, 0, 0, 0)); td = ImageDraw.Draw(txt)
    for k, s in enumerate(['Fácil,', 'rápido e', 'prático!']): td.text((12, 12 + k * 44), s, font=fs, fill=(3, 12, 26)); td.text((10, 10 + k * 44), s, font=fs, fill=CYAN)
    txt = txt.rotate(-12, resample=Image.BICUBIC, expand=True); im.paste(txt, (884, 118), txt); d = ImageDraw.Draw(im)
    # cartoes de passos
    def cartao(x, titulo, passos, nav):
        w, h = 490, 236; d.rounded_rectangle([x, 342, x + w, 342 + h], 22, fill=BR)
        nav(d, x + 40, 372, 20); d.text((x + 72, 354), titulo, font=F('bar', 32), fill=NAVY)
        yy = 400
        for n, (a, b) in enumerate(passos, 1):
            d.ellipse([x + 24, yy, x + 54, yy + 30], fill=CYAN2); d.text((x + 33, yy + 3), str(n), font=F('ab', 20), fill=BR)
            d.text((x + 66, yy - 1), a, font=F('ab', 22), fill=(20, 30, 40)); d.text((x + 66, yy + 24), b, font=F('a', 20), fill=(60, 70, 80))
            yy += 56
        celular(im, x + w - 118, 364, 196, TELA)
    cartao(40, 'iPhone (Safari)', [('Abra acatmar.org/app', 'no Safari'), ('Toque em Compartilhar', '(quadrado com seta, na barra)'),
                                   ('Toque em "Adicionar', 'à Tela de Início"')], safari)
    cartao(550, 'Android (Chrome)', [('Abra acatmar.org/app', 'no Chrome'), ('Toque em "Instalar"', 'no aviso que aparece'),
                                     ('Pronto: o ícone fica', 'na tela inicial')], chrome)
    d = ImageDraw.Draw(im)
    # QR + checks
    qr = qrcode.make('https://www.acatmar.org/app/', border=1).convert('RGB').resize((118, 118), Image.NEAREST)
    d.rounded_rectangle([40, 596, 160, 716], 12, fill=BR); im.paste(qr.resize((108, 108), Image.NEAREST), (46, 602))
    d.rounded_rectangle([176, 612, 560, 700], 20, outline=CYAN, width=3, fill=(8, 34, 62))
    d.text((198, 634), 'OU ESCANEIE O QR CODE', font=F('bar', 24), fill=BR); d.text((198, 661), 'E ACESSE AGORA', font=F('bar', 24), fill=CYAN)
    d.polygon([(520, 644), (540, 656), (520, 668)], fill=CYAN)
    for k, s in enumerate(['PROGRAMAÇÃO', 'AVISOS', 'CREDENCIAL', 'CERTIFICADO']):
        cx = 620 + (k % 2) * 230; cy = 632 + (k // 2) * 48
        icone_circulo(d, cx, cy, 15, 'check'); d.text((cx + 26, cy - 13), s, font=F('bar', 24), fill=BR)
    painel(im, 728); rodape(im)
    im.save(os.path.join(RAIZ, 'media/cards/feed-app-2.jpg'), quality=93); print('feed-app-2.jpg')

card1(); card2()
