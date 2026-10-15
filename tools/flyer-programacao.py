# -*- coding: utf-8 -*-
"""Flyers da programacao do VI Forum (manha e tarde), a partir de app/data/forum.json.
Dois formatos: flyer 1414x2000 (media/cards/flyer-programacao-N.jpg) e story 1080x1920
(media/cards/story-programacao-N.jpg). Rodape = painel de logos feito pela ACATMAR (media/painel-logos.png)."""
import json, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(RAIZ, 'app/data/forum.json'), encoding='utf-8'))
NAVY, DEEP, NAVY2 = (10, 37, 64), (6, 23, 38), (14, 53, 87)
TEAL, TEALB, TEALD, GOLD = (0, 163, 180), (53, 201, 218), (0, 114, 126), (242, 181, 74)
WHITE, MUTED = (255, 255, 255), (168, 194, 206)

FORMATOS = {
    'flyer': dict(W=1414, H=2000, arq='flyer-programacao', selo=272, selo_xy=(50, 36), xt=350,
                  f_kicker=30, f_tit=70, y_tit=100, pill_y=272, f_pill=26, pill_linhas=1,
                  xl=160, xf=330, xtx=440, wrap=900, f_titulo=40, lh=52, r_badge=50, f_badge=38,
                  r_foto=66, anel=6, r_cb=40, f_cb=30, f_ct=36, f_cs=24, f_nome=26, f_sub=24,
                  alt_talk=172, alt_compact=92, y0=390, painel=1300, f_frase=26, f_nota=20, y_folga=120),
    'story': dict(W=1080, H=1920, arq='story-programacao', selo=220, selo_xy=(40, 40), xt=290,
                  f_kicker=26, f_tit=54, y_tit=92, pill_y=226, f_pill=22, pill_linhas=2,
                  xl=118, xf=258, xtx=350, wrap=680, f_titulo=34, lh=44, r_badge=42, f_badge=30,
                  r_foto=56, anel=5, r_cb=34, f_cb=25, f_ct=31, f_cs=21, f_nome=23, f_sub=20,
                  alt_talk=150, alt_compact=80, y0=360, painel=1000, f_frase=20, f_nota=17, y_folga=100),
}

def fonte(nome, tam):
    cam = {'osw': 'assets/fonts/Oswald.ttf', 'bar': 'assets/fonts/BarlowCondensed-SemiBold.ttf',
           'ar': '/System/Library/Fonts/Supplemental/Arial.ttf',
           'ab': '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
           'ai': '/System/Library/Fonts/Supplemental/Arial Italic.ttf'}[nome]
    if not cam.startswith('/'): cam = os.path.join(RAIZ, cam)
    return ImageFont.truetype(cam, tam)

def fundo(W, H):
    col = Image.new('RGB', (1, H)); cp = col.load()
    for y in range(H):
        k = max(0, min(1, 1 - abs(y / H - 0.45) * 1.6))
        cp[0, y] = tuple(int(DEEP[i] + (NAVY[i] - DEEP[i]) * k) for i in range(3))
    im = col.resize((W, H))
    glow = Image.new('RGB', (W, H), (0, 0, 0)); g = ImageDraw.Draw(glow)
    g.ellipse((W - 700, -500, W + 500, 500), fill=(0, 70, 85))      # brilho do farol (alto, direita)
    g.ellipse((-400, H - 500, 500, H + 400), fill=(0, 40, 55))
    return ImageChops.add(im, glow.filter(ImageFilter.GaussianBlur(160)))

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

def foto_circular(cam, r, anel):
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

def pagina(P, kicker, linhas, arq):
    W, H = P['W'], P['H']
    im = fundo(W, H); d = ImageDraw.Draw(im)

    # --- cabecalho: selo branco com a logo + titulo + faixa de data
    selo = P['selo']; bx, by = P['selo_xy']
    d.rounded_rectangle((bx + 4, by + 6, bx + selo + 4, by + selo + 6), 44, fill=(3, 14, 26))
    d.rounded_rectangle((bx, by, bx + selo, by + selo), 44, fill=WHITE, outline=TEALB, width=3)
    logo = Image.open(os.path.join(RAIZ, 'media/logos/vi-forum-logo-fundo-branco.png')).convert('RGB')
    lh = selo - 26; logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
    im.paste(logo, (bx + (selo - logo.width) // 2, by + (selo - logo.height) // 2))
    xt = P['xt']
    espaco(d, (xt, by + 22), kicker, fonte('bar', P['f_kicker']), TEALB, 5)
    f1 = fonte('osw', P['f_tit']); yt = P['y_tit']; lt = int(P['f_tit'] * 1.11)
    d.text((xt, yt), 'VI FÓRUM DE CAPACITAÇÃO', font=f1, fill=WHITE)
    d.text((xt, yt + lt), 'TÉCNICA ', font=f1, fill=WHITE)
    d.text((xt + f1.getlength('TÉCNICA '), yt + lt), 'ACATMAR', font=f1, fill=TEALB)
    fp = fonte('bar', P['f_pill'])
    if P['pill_linhas'] == 1:
        infos = ['20 DE OUTUBRO · TERÇA-FEIRA · 8H ÀS 19H · IFSC FLORIANÓPOLIS-CONTINENTE · GRATUITO']
    else:
        infos = ['20 DE OUTUBRO · TERÇA-FEIRA · 8H ÀS 19H', 'IFSC FLORIANÓPOLIS-CONTINENTE · GRATUITO']
    ph = 56 if P['pill_linhas'] == 1 else 92
    pw = max(largura_esp(t, fp, 1.5) for t in infos) + 50
    if xt + pw > W - 40: fp = fonte('bar', P['f_pill'] - 2); pw = max(largura_esp(t, fp, 1) for t in infos) + 44
    py = P['pill_y']
    d.rounded_rectangle((xt, py, xt + pw, py + ph), 28, fill=NAVY2, outline=TEAL, width=2)
    for i, t in enumerate(infos):
        espaco(d, (xt + 22, py + 14 + i * 38), t, fp, WHITE, 1.5)

    # --- linha do tempo (alturas se adaptam ao espaco entre o cabecalho e o painel)
    xl, xf, xtx = P['xl'], P['xf'], P['xtx']
    pan = painel_logos(P['painel']); yf = H - pan.height - P['y_folga']
    base = {'talk': P['alt_talk'], 'compact': P['alt_compact']}
    total = sum(base[i[0]] for i in linhas)
    k = max(0.95, min(1.32, ((yf - 60) - P['y0']) / total))
    alturas = {t: int(v * k) for t, v in base.items()}
    y = P['y0']; tops = []
    for item in linhas: tops.append(y); y += alturas[item[0]]
    cy0 = tops[0] + alturas[linhas[0][0]] // 2; cy1 = tops[-1] + alturas[linhas[-1][0]] // 2
    d.line((xl, cy0, xl, cy1), fill=TEALD, width=4)
    for item, top in zip(linhas, tops):
        if item[0] == 'talk':
            s = item[1]; p = byid.get(s.get('palestrante'), {})
            cy = top + alturas['talk'] // 2; r = P['r_badge']
            d.ellipse((xl - r, cy - r, xl + r, cy + r), fill=TEAL)
            ft = fonte('osw', P['f_badge']); t = hora(s['hora'])
            d.text((xl - ft.getlength(t) / 2, cy - P['f_badge'] * 0.63), t, font=ft, fill=WHITE)
            if p.get('foto'):
                fo = foto_circular(p['foto'], P['r_foto'], P['anel']); im.paste(fo, (xf - fo.width // 2, cy - fo.height // 2), fo)
            ftit = fonte('osw', P['f_titulo']); LH = P['lh']
            ls = quebra(s['titulo'], ftit, P['wrap'])[:2]
            bloco = len(ls) * LH + 14 + int(P['f_nome'] * 1.25)
            ty = cy - bloco // 2
            for l in ls: d.text((xtx, ty), l, font=ftit, fill=WHITE); ty += LH
            ty += 14
            fn = fonte('ab', P['f_nome']); fs = fonte('ar', P['f_sub'])
            nome = p.get('nome', s.get('quem', '')); sub = ' · '.join(x for x in [p.get('cargo'), p.get('empresa')] if x)
            d.text((xtx, ty), nome, font=fn, fill=TEALB)
            xs = xtx + fn.getlength(nome) + 12
            if xs + fs.getlength(sub) > W - 30:                     # story: cargo/empresa na linha de baixo
                d.text((xtx, ty + int(P['f_nome'] * 1.3)), sub, font=fs, fill=MUTED)
            else:
                d.text((xs, ty + 2), sub, font=fs, fill=MUTED)
        else:
            _, hh, tit, sub = item
            cy = top + alturas['compact'] // 2; r = P['r_cb']
            d.ellipse((xl - r, cy - r, xl + r, cy + r), fill=GOLD)
            ft = fonte('osw', P['f_cb']); d.text((xl - ft.getlength(hh) / 2, cy - P['f_cb'] * 0.63), hh, font=ft, fill=NAVY)
            d.text((xtx, cy - int(P['f_ct'] * 0.95)), tit, font=fonte('osw', P['f_ct']), fill=GOLD)
            d.text((xtx, cy + 8), sub, font=fonte('ar', P['f_cs']), fill=MUTED)

    # --- chamada para inscricao, so quando sobra espaco entre a agenda e o painel
    sobra = (yf - 40) - y
    if sobra >= 170:
        ch = 128 if W > 1200 else 118; cw = min(W - 2 * P['xl'] + 40, 900); cx0 = (W - cw) // 2; cy0 = y + (sobra - ch) // 2
        d.rounded_rectangle((cx0, cy0, cx0 + cw, cy0 + ch), 26, fill=(12, 48, 78), outline=TEAL, width=2)
        fa = fonte('osw', 34 if W > 1200 else 30); fb = fonte('bar', 24 if W > 1200 else 21)
        t1 = 'INSCRIÇÃO GRATUITA  ·  VAGAS LIMITADAS  ·  CERTIFICADO'
        t2 = 'PROGRAMAÇÃO, AVISOS E CREDENCIAL NO APP:  ACATMAR.ORG/APP'
        d.text(((W - fa.getlength(t1)) / 2, cy0 + 18), t1, font=fa, fill=GOLD)
        w2 = largura_esp(t2, fb, 2); espaco(d, ((W - w2) / 2, cy0 + ch - 44), t2, fb, TEALB, 2)

    # --- rodape: painel de logos da ACATMAR + frase
    for xx in range(0, W, 2):
        yy = int(yf - 30 + 10 * math.sin(xx / 90.0))
        d.line((xx, yy, xx, H), fill=(8, 30, 52))
    im.paste(pan, ((W - pan.width) // 2, yf), pan)
    frase = 'CAPACITAÇÃO HOJE. UM SETOR NÁUTICO SEMPRE MAIS FORTE AMANHÃ.'
    ff = fonte('bar', P['f_frase']); esp = 4 if W > 1200 else 2.5; fw = largura_esp(frase, ff, esp)
    espaco(d, ((W - fw) // 2, yf + pan.height + 22), frase, ff, TEALB, esp)
    nota = '* A ordem das palestras pode sofrer alterações.'
    fi = fonte('ai', P['f_nota']); d.text((W - 40 - fi.getlength(nota), H - 40), nota, font=fi, fill=MUTED)
    d.text((40, H - 40), 'acatmar.org/app  ·  @acatmarassociacao', font=fonte('ar', P['f_nota']), fill=MUTED)
    im.save(os.path.join(RAIZ, arq), quality=92)
    print('gerado', arq)

prog = sorted(D['programacao'], key=lambda s: s['hora'])
manha = [s for s in prog if s['tipo'] == 'palestra' and s['periodo'] == 'Manhã']
tarde = [s for s in prog if s['tipo'] == 'palestra' and s['periodo'] == 'Tarde']
almoco = next((s for s in prog if s['id'] == 'almoco'), {})
p1 = [('compact', '7h30', 'Credenciamento', 'Apresente o QR Code do app na entrada do auditório'),
      ('compact', '8h30', 'Cerimônia de abertura', 'ACATMAR, Mundo Mar Consulting e IFSC')] + \
     [('talk', s) for s in manha] + \
     [('compact', '12h00', 'Intervalo para almoço', almoco.get('quem', 'Retorno às 12h45'))]
p2 = [('talk', s) for s in tarde] + \
     [('compact', '19h00', 'Encerramento', 'Certificados e agradecimentos')]

os.makedirs(os.path.join(RAIZ, 'media/cards'), exist_ok=True)
for nome, P in FORMATOS.items():
    pagina(P, 'PROGRAMAÇÃO  ·  MANHÃ', p1, 'media/cards/%s-1.jpg' % P['arq'])
    pagina(P, 'PROGRAMAÇÃO  ·  TARDE', p2, 'media/cards/%s-2.jpg' % P['arq'])
