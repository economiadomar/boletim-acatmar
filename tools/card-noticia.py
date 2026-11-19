#!/usr/bin/env python3
# Card de noticia no padrao ACATMAR (foto em cima, bloco azul embaixo).
# uso: python3 tools/card-noticia.py --foto X.jpg --olho "..." --titulo "..." --sub "..." --saida nome
import argparse, os, textwrap
from PIL import Image, ImageDraw, ImageFont

RAIZ   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAVY   = (10, 37, 64)
TEAL   = (55, 203, 217)
OLHO_C = (74, 196, 219)
BRANCO = (255, 255, 255)
SUAVE  = (214, 228, 238)
OSWALD = os.path.join(RAIZ, 'assets/fonts/Oswald.ttf')
BARLOW = os.path.join(RAIZ, 'assets/fonts/BarlowCondensed-SemiBold.ttf')
LOGO   = os.path.join(RAIZ, 'media/logos/acatmar-completa-branca.png')

FORMATOS = {'linkedin': (1200, 1200, 0.505), 'instagram': (1080, 1350, 0.56)}

def fonte(p, s):
    f = ImageFont.truetype(p, s)
    try: f.set_variation_by_name('SemiBold')
    except Exception: pass
    return f

def larg(d, t, f): return d.textbbox((0, 0), t, font=f)[2]

def quebra(d, txt, f, maxw):
    linhas, atual = [], ''
    for p in txt.split():
        teste = (atual + ' ' + p).strip()
        if larg(d, teste, f) <= maxw or not atual: atual = teste
        else: linhas.append(atual); atual = p
    if atual: linhas.append(atual)
    return linhas

def monta(foto, olho, titulo, sub, credito, destino, fmt, foco=0.5):
    W, H, corte = FORMATOS[fmt]
    yfoto = int(H * corte)
    card = Image.new('RGB', (W, H), NAVY)

    # foto preenchendo a faixa de cima, com ancora vertical ajustavel
    im = Image.open(foto).convert('RGB')
    esc = max(W / im.width, yfoto / im.height)
    im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    top = max(0, min(im.height - yfoto, int((im.height - yfoto) * foco)))
    card.paste(im.crop((max(0, (im.width - W)//2), top, max(0, (im.width - W)//2) + W, top + yfoto)), (0, 0))

    d = ImageDraw.Draw(card)
    m = int(W * 0.065)                      # margem lateral
    if credito:
        f = fonte(BARLOW, int(W * 0.019))
        y = yfoto - int(W * 0.047)
        hs = int(W*0.13)
        sombra = Image.new('RGBA', (W, hs), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sombra)
        for i in range(hs):
            ds.line([(0, i), (W, i)], fill=(0, 0, 0, int(105 * (i/hs)**1.6)))
        card.paste(Image.alpha_composite(card.crop((0, yfoto-hs, W, yfoto)).convert('RGBA'), sombra).convert('RGB'), (0, yfoto-hs))
        d.text((m, y), credito, font=f, fill=BRANCO)

    d.rectangle([0, yfoto, W, yfoto + int(H*0.0067)], fill=TEAL)   # regua teal

    y = yfoto + int(H * 0.055)
    f_olho = fonte(BARLOW, int(W * 0.0275))
    d.text((m, y), olho.upper(), font=f_olho, fill=OLHO_C)
    y += int(W * 0.047)

    # titulo: diminui a fonte ate caber em no maximo 4 linhas
    for tam in range(int(W * 0.062), int(W * 0.036), -2):
        f_tit = fonte(OSWALD, tam)
        ls = quebra(d, titulo.upper(), f_tit, W - 2*m)
        if len(ls) <= 4: break
    for ln in ls:
        d.text((m, y), ln, font=f_tit, fill=BRANCO)
        y += int(tam * 1.16)

    y += int(W * 0.030)
    f_sub = fonte(BARLOW, int(W * 0.0305))
    for ln in quebra(d, sub, f_sub, W - 2*m)[:4]:
        d.text((m, y), ln, font=f_sub, fill=SUAVE)
        y += int(W * 0.0385)

    # rodape: logo + site
    lg = Image.open(LOGO).convert('RGBA')
    alt = int(W * 0.072)
    lg = lg.resize((int(lg.width * alt / lg.height), alt), Image.LANCZOS)
    ylg = H - int(W * 0.062) - alt
    card.paste(lg, (m, ylg), lg)
    f_site = fonte(BARLOW, int(W * 0.0235))
    txt = 'WWW.ACATMAR.ORG'
    d.text((W - m - larg(d, txt, f_site), ylg + alt - int(W * 0.028)), txt, font=f_site, fill=OLHO_C)

    card.save(destino, 'JPEG', quality=92, optimize=True)
    print('gerado', destino, card.size)

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--foto', required=True); a.add_argument('--olho', required=True)
    a.add_argument('--titulo', required=True); a.add_argument('--sub', required=True)
    a.add_argument('--credito', default='Divulgação ACATMAR')
    a.add_argument('--saida', required=True); a.add_argument('--foco', type=float, default=0.5)
    a.add_argument('--dir', default=os.path.expanduser('~/Downloads/ACATMAR-cards'))
    p = a.parse_args()
    os.makedirs(p.dir, exist_ok=True)
    for fmt in ('linkedin', 'instagram'):
        monta(p.foto, p.olho, p.titulo, p.sub, p.credito,
              os.path.join(p.dir, f'{p.saida}-{fmt}.jpg'), fmt, p.foco)
