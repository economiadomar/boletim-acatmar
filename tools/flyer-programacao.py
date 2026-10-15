# -*- coding: utf-8 -*-
"""Flyer da programacao do VI Forum (2 paginas: manha e tarde), a partir de app/data/forum.json.
Saida: media/cards/flyer-programacao-1.jpg e -2.jpg (1414x2000).
Rodape = painel de logos feito pela ACATMAR (media/painel-logos.png)."""
import json, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(RAIZ, 'app/data/forum.json'), encoding='utf-8'))
W, H = 1414, 2000
NAVY, DEEP, NAVY2 = (10, 37, 64), (6, 23, 38), (14, 53, 87)
TEAL, TEALB, TEALD, GOLD = (0, 163, 180), (53, 201, 218), (0, 114, 126), (242, 181, 74)
WHITE, MUTED = (255, 255, 255), (168, 194, 206)

def fonte(nome, tam):
    cam = {'osw': 'assets/fonts/Oswald.ttf', 'bar': 'assets/fonts/BarlowCondensed-SemiBold.ttf',
           'ar': '/System/Library/Fonts/Supplemental/Arial.ttf',
           'ab': '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
           'ai': '/System/Library/Fonts/Supplemental/Arial Italic.ttf'}[nome]
    if not cam.startswith('/'): cam = os.path.join(RAIZ, cam)
    return ImageFont.truetype(cam, tam)

def fundo():
    # degrade vertical DEEP -> NAVY -> DEEP (coluna 1xH esticada)
    col = Image.new('RGB', (1, H)); cp = col.load()
    for y in range(H):
        k = max(0, min(1, 1 - abs(y / H - 0.45) * 1.6))
        cp[0, y] = tuple(int(DEEP[i] + (NAVY[i] - DEEP[i]) * k) for i in range(3))
    im = col.resize((W, H))
    glow = Image.new('RGB', (W, H), (0, 0, 0)); g = ImageDraw.Draw(glow)
    g.ellipse((W - 700, -500, W + 500, 500), fill=(0, 70, 85))      # brilho do farol (alto, direita)
    g.ellipse((-400, H - 500, 500, H + 400), fill=(0, 40, 55))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    return ImageChops.add(im, glow)

def espaco(d, xy, txt, f, fill, esp=3):
    x, y = xy
    for ch in txt:
        d.text((x, y), ch, font=f, fill=fill); x += f.getlength(ch) + esp
    return x

def largura_esp(txt, f, esp=3): return sum(f.getlength(c) + esp for c in txt)

def quebra(txt, f, maxw):
    pal, linhas, cur = txt.split(), [], ''
    for p in pal:
        t = (cur + ' ' + p).strip()
        if f.getlength(t) <= maxw: cur = t
        else: linhas.append(cur); cur = p
    if cur: linhas.append(cur)
    return linhas

def foto_circular(cam, r, anel=6):
    im = Image.open(os.path.join(RAIZ, 'app', cam)).convert('RGB').resize((2 * r, 2 * r), Image.LANCZOS)
    m = Image.new('L', (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    out = Image.new('RGBA', (2 * (r + anel), 2 * (r + anel)), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, out.width - 1, out.height - 1), fill=TEALB + (255,))
    ImageDraw.Draw(out).ellipse((anel // 2, anel // 2, out.width - 1 - anel // 2, out.height - 1 - anel // 2), fill=NAVY + (255,))
    out.paste(im, (anel, anel), m)
    return out

def painel_logos(larg):
    p = Image.open(os.path.join(RAIZ, 'media/painel-logos.png')).convert('RGB')
    r = larg / p.width; p = p.resize((larg, int(p.height * r)), Image.LANCZOS)
    m = Image.new('L', p.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 30, fill=255)
    out = Image.new('RGBA', p.size, (0, 0, 0, 0)); out.paste(p, (0, 0), m)
    return out

byid = {p['id']: p for p in D['palestrantes']}
def hora(h): return h.replace(':', 'h')

def pagina(num, kicker, linhas, arq):
    im = fundo(); d = ImageDraw.Draw(im)
    # --- cabecalho
    logo = Image.open(os.path.join(RAIZ, 'media/logos/vi-forum-logo.png')).convert('RGBA')
    lh = 270; logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
    im.paste(logo, (50, 40), logo)
    xt = 350
    espaco(d, (xt, 62), kicker, fonte('bar', 30), TEALB, 5)
    f1 = fonte('osw', 70)
    d.text((xt, 100), 'VI FÓRUM DE CAPACITAÇÃO', font=f1, fill=WHITE)
    d.text((xt, 178), 'TÉCNICA ', font=f1, fill=WHITE)
    d.text((xt + f1.getlength('TÉCNICA '), 178), 'ACATMAR', font=f1, fill=TEALB)
    fp = fonte('bar', 26)
    info = '20 DE OUTUBRO · TERÇA-FEIRA · 8H ÀS 19H · IFSC FLORIANÓPOLIS-CONTINENTE · GRATUITO'
    pw = largura_esp(info, fp, 1.5) + 50
    if xt + pw > W - 50:                      # garante que a faixa cabe na pagina
        fp = fonte('bar', 24); pw = largura_esp(info, fp, 1) + 44
    d.rounded_rectangle((xt, 272, xt + pw, 328), 28, fill=NAVY2, outline=TEAL, width=2)
    espaco(d, (xt + 22, 286), info, fp, WHITE, 1.5 if fp.size == 26 else 1)

    # --- linha do tempo (alturas se adaptam ao espaco entre o cabecalho e o painel)
    xl, xf, xtx = 160, 330, 440
    pan_h = painel_logos(1300).height; yf_prev = H - pan_h - 120
    base = {'talk': 172, 'compact': 92}
    total = sum(base[i[0]] for i in linhas)
    disp = (yf_prev - 60) - 390
    k = max(0.95, min(1.32, disp / total))
    alturas = {t: int(v * k) for t, v in base.items()}
    y = 390; tops = []
    for item in linhas: tops.append(y); y += alturas[item[0]]
    y_fim = y
    # linha vertical por tras dos circulos
    cy0 = tops[0] + (alturas[linhas[0][0]] // 2); cy1 = tops[-1] + (alturas[linhas[-1][0]] // 2)
    d.line((xl, cy0, xl, cy1), fill=TEALD, width=4)
    for item, top in zip(linhas, tops):
        if item[0] == 'talk':
            s = item[1]; p = byid.get(s.get('palestrante'), {})
            cy = top + alturas['talk'] // 2
            d.ellipse((xl - 50, cy - 50, xl + 50, cy + 50), fill=TEAL)
            ft = fonte('osw', 38); t = hora(s['hora'])
            d.text((xl - ft.getlength(t) / 2, cy - 24), t, font=ft, fill=WHITE)
            if p.get('foto'):
                fo = foto_circular(p['foto'], 66); im.paste(fo, (xf - fo.width // 2, cy - fo.height // 2), fo)
            ftit = fonte('osw', 40)
            ls = quebra(s['titulo'], ftit, 900)[:2]
            ty = cy - (len(ls) * 46 + 34) // 2
            for l in ls: d.text((xtx, ty), l, font=ftit, fill=WHITE); ty += 46
            fn = fonte('ab', 26); fs = fonte('ar', 24)
            nome = p.get('nome', s.get('quem', '')); sub = ' · '.join(x for x in [p.get('cargo'), p.get('empresa')] if x)
            d.text((xtx, ty + 4), nome, font=fn, fill=TEALB)
            d.text((xtx + fn.getlength(nome) + 14, ty + 6), sub, font=fs, fill=MUTED)
        else:
            _, hh, tit, sub = item
            cy = top + alturas['compact'] // 2
            d.ellipse((xl - 40, cy - 40, xl + 40, cy + 40), fill=GOLD)
            ft = fonte('osw', 30); d.text((xl - ft.getlength(hh) / 2, cy - 19), hh, font=ft, fill=NAVY)
            d.text((xtx, cy - 34), tit, font=fonte('osw', 36), fill=GOLD)
            d.text((xtx, cy + 8), sub, font=fonte('ar', 24), fill=MUTED)

    # --- rodape: painel de logos da ACATMAR + frase
    pan = painel_logos(1300); yf = H - pan.height - 120
    # onda discreta atras do painel
    for xx in range(0, W, 2):
        yy = int(yf - 30 + 10 * math.sin(xx / 90.0))
        d.line((xx, yy, xx, H), fill=(8, 30, 52))
    im.paste(pan, ((W - pan.width) // 2, yf), pan)
    frase = 'CAPACITAÇÃO HOJE. UM SETOR NÁUTICO SEMPRE MAIS FORTE AMANHÃ.'
    ff = fonte('bar', 26); fw = largura_esp(frase, ff, 4)
    espaco(d, ((W - fw) // 2, yf + pan.height + 26), frase, ff, TEALB, 4)
    nota = '* A ordem das palestras pode sofrer alterações.'
    fi = fonte('ai', 20); d.text((W - 60 - fi.getlength(nota), H - 42), nota, font=fi, fill=MUTED)
    d.text((60, H - 42), 'acatmar.org/app  ·  @acatmarassociacao', font=fonte('ar', 20), fill=MUTED)
    im.save(os.path.join(RAIZ, arq), quality=92)
    print('gerado', arq, '| fim das linhas em y =', y_fim, '| painel em y =', yf)

prog = sorted(D['programacao'], key=lambda s: s['hora'])
manha = [s for s in prog if s['tipo'] == 'palestra' and s['periodo'] == 'Manhã']
tarde = [s for s in prog if s['tipo'] == 'palestra' and s['periodo'] == 'Tarde']

p1 = [('compact', '7h30', 'Credenciamento', 'Apresente o QR Code do app na entrada do auditório'),
      ('compact', '8h30', 'Cerimônia de abertura', 'ACATMAR, Mundo Mar Consulting e IFSC')] + \
     [('talk', s) for s in manha] + \
     [('compact', '12h00', 'Intervalo para almoço', 'Retorno às 13h00')]
p2 = [('talk', s) for s in tarde] + \
     [('compact', '19h00', 'Encerramento', 'Certificados e agradecimentos')]

os.makedirs(os.path.join(RAIZ, 'media/cards'), exist_ok=True)
pagina(1, 'PROGRAMAÇÃO  ·  MANHÃ', p1, 'media/cards/flyer-programacao-1.jpg')
pagina(2, 'PROGRAMAÇÃO  ·  TARDE', p2, 'media/cards/flyer-programacao-2.jpg')
