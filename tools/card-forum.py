# -*- coding: utf-8 -*-
"""Cards de divulgacao do VI Forum ACATMAR (feed 1080x1080 e story 1080x1920).
Uso: python3 tools/card-forum.py  -> grava em media/cards/
Le os patrocinadores de app/data/forum.json: entrou logo nova, e so rodar de novo."""
import json, os
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(RAIZ, 'app/data/forum.json'), encoding='utf-8'))
EV = D['evento']
NAVY, TEAL, TEALB = (10, 37, 64), (0, 163, 180), (53, 201, 218)
GRANDES = ('okean-world.png', 'veleiros-da-ilha.png', 'capitania-sc.png')  # logos redondas: um pouco maiores

def F(nome, tam):
    cam = {'osw': 'assets/fonts/Oswald.ttf', 'bar': 'assets/fonts/BarlowCondensed-SemiBold.ttf'}.get(nome)
    if cam: return ImageFont.truetype(os.path.join(RAIZ, cam), tam)
    return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial%s.ttf' % (' Bold' if nome == 'ab' else ''), tam)

def logo(cam, alt):
    im = Image.open(os.path.join(RAIZ, 'app', cam)).convert('RGBA')
    b = Image.new('RGB', im.size, (255, 255, 255)); b.paste(im, mask=im.split()[3])
    r = alt / b.height
    return b.resize((max(1, int(b.width * r)), alt), Image.LANCZOS)

def txt_c(d, y, s, f, cor, L):
    x0, y0, x1, y1 = d.textbbox((0, 0), s, font=f)
    d.text(((L - x1) // 2, y - y0), s, font=f, fill=cor)
    return y1 - y0

def faixa(L, alt_logo, gap, tam_lab):
    grupos = []
    for c in D['patrocinadores']:
        ims = [logo(e['logo'], int(alt_logo * (1.2 if e['logo'].endswith(GRANDES) else 1)))
               for e in c['empresas'] if e.get('logo')]
        if ims: grupos.append((c['cota'].upper(), ims))
    fl = F('bar', tam_lab)
    tmp = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    linhas, alt = [], 14
    for cota, ims in grupos:
        larg = sum(i.width for i in ims) + gap * (len(ims) - 1)
        if larg > L - 90:
            f = (L - 90) / larg
            ims = [i.resize((int(i.width * f), int(i.height * f)), Image.LANCZOS) for i in ims]
            larg = sum(i.width for i in ims) + gap * (len(ims) - 1)
        h = max(i.height for i in ims)
        linhas.append((cota, ims, larg, h))
        alt += tam_lab + 10 + h + gap + 2
    faixa = Image.new('RGB', (L, alt), (255, 255, 255))
    d = ImageDraw.Draw(faixa)
    y = 14
    for cota, ims, larg, h in linhas:
        w = d.textbbox((0, 0), cota, font=fl)[2]
        d.text(((L - w) // 2, y), cota, font=fl, fill=(128, 144, 156))
        y += tam_lab + 10
        x = (L - larg) // 2
        for i in ims:
            faixa.paste(i, (x, y + (h - i.height) // 2)); x += i.width + gap
        y += h + gap + 2
    return faixa

def card(L, A, nome, emb_alt, alt_logo, gap_logo, tam_lab, t_data, t_tit, t_info, rodape_tam):
    im = Image.new('RGB', (L, A), NAVY)
    d = ImageDraw.Draw(im)
    for y in range(A):
        t = y / A
        d.line([(0, y), (L, y)], fill=(int(4 + 8 * t), int(11 + 30 * t), int(24 + 50 * t)))

    arte = Image.open(os.path.join(RAIZ, 'media/noticias/vi-forum-2026.jpg')).convert('RGB')
    emb = arte.crop((55, 20, 875, 925))
    r = emb_alt / emb.height
    emb = emb.resize((int(emb.width * r), emb_alt), Image.LANCZOS)
    im.paste(emb, ((L - emb.width) // 2, int(A * 0.022)))

    fx = faixa(L, alt_logo, gap_logo, tam_lab)
    rodape_h = rodape_tam + 52
    y_fx = A - fx.height - rodape_h

    # bloco de texto centrado entre a arte e a faixa
    topo = int(A * 0.022) + emb_alt
    linhas = [('bar', t_data, TEALB, '20 DE OUTUBRO DE 2026 · 8H ÀS 19H', 20),
              ('osw', t_tit, (255, 255, 255), 'VI FÓRUM DE CAPACITAÇÃO', 12),
              ('osw', t_tit, (255, 255, 255), 'TÉCNICA ACATMAR', 22),
              ('ab', t_info, (219, 231, 240), 'IFSC · Câmpus Florianópolis-Continente', 8),
              ('a', int(t_info * .84), (150, 174, 192), 'R. Quatorze de Julho, 150 · Coqueiros · Florianópolis', 26)]
    alturas = [d.textbbox((0, 0), s, font=F(f, t))[3] - d.textbbox((0, 0), s, font=F(f, t))[1] for f, t, _, s, _ in linhas]
    pill_h = int(t_info * 1.15) + 34
    total = sum(alturas) + sum(l[4] for l in linhas) + pill_h + 22 + int(t_info * .86) + 6
    y = topo + max(10, (y_fx - topo - total) // 2)
    for (f, t, cor, s, dep), h in zip(linhas, alturas):
        txt_c(d, y, s, F(f, t), cor, L); y += h + dep
    fs = F('bar', int(t_info * 1.15)); s = 'INSCRIÇÃO GRATUITA'
    tw = d.textbbox((0, 0), s, font=fs)[2]
    pw = tw + 70; x0 = (L - pw) // 2
    d.rounded_rectangle([x0, y, x0 + pw, y + pill_h], radius=pill_h // 2, fill=TEAL)
    d.text((x0 + 35, y + 14), s, font=fs, fill=(255, 255, 255))
    y += pill_h + 22
    txt_c(d, y, 'Programação e inscrição no app: acatmar.org/app', F('a', int(t_info * .86)), (196, 214, 228), L)

    im.paste(fx, (0, y_fx))
    d.rectangle([0, y_fx + fx.height, L, A], fill=(255, 255, 255))
    fr = F('bar', rodape_tam)
    s = 'ACATMAR · ASSOCIAÇÃO NÁUTICA BRASILEIRA · @ACATMARASSOCIACAO'
    w = d.textbbox((0, 0), s, font=fr)[2]
    d.text(((L - w) // 2, y_fx + fx.height + (rodape_h - rodape_tam) // 2 - 4), s, font=fr, fill=(91, 111, 122))

    cam = os.path.join(RAIZ, 'media/cards', nome)
    im.save(cam, quality=93)
    print(nome, im.size)

card(1080, 1080, 'vi-forum-feed.jpg', 205, 26, 16, 17, 28, 52, 24, 24)
card(1080, 1920, 'vi-forum-story.jpg', 520, 44, 28, 25, 40, 80, 35, 29)
