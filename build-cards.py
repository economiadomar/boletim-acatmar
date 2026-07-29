#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera um card de compartilhamento 1200x630 para cada materia (formato que o
LinkedIn e o Facebook mostram GRANDE): foto no topo + faixa navy com a marca
ACATMAR e o titulo. Salvo em media/share/<id>.jpg.
"""
import os, json, textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BAND = 232                       # altura da faixa inferior
NAVY = (10, 37, 64)
DEEP = (6, 23, 38)
TEAL = (53, 201, 218)
WHITE = (255, 255, 255)
FONT_TITLE = "assets/fonts/Oswald.ttf"
FONT_EYE   = "assets/fonts/BarlowCondensed-SemiBold.ttf"

def cobrir(img, w, h):
    r = max(w/img.width, h/img.height)
    img = img.resize((int(img.width*r), int(img.height*r)), Image.LANCZOS)
    excesso = img.height-h
    # foto larga: foca no centro; foto alta/retrato: foca no terco superior (rostos)
    frac = 0.42 if img.width >= img.height*1.4 else 0.20
    x = (img.width-w)//2; y = int(excesso*frac)
    y = max(0, min(excesso, y))
    return img.crop((x, y, x+w, y+h))

def make_card(foto, titulo, saida):
    card = Image.new("RGB", (W, H), NAVY)
    # foto no topo
    try:
        ph = Image.open(foto).convert("RGB")
        card.paste(cobrir(ph, W, H-BAND), (0, 0))
    except Exception as e:
        print("  foto:", e)
    d = ImageDraw.Draw(card)
    # faixa navy inferior com leve gradiente
    top = H-BAND
    for i in range(BAND):
        f = i/BAND
        col = tuple(int(DEEP[j] + (NAVY[j]-DEEP[j])*f) for j in range(3))
        d.line([(0, top+i), (W, top+i)], fill=col)
    # barra teal de acento
    d.rectangle([0, top, W, top+6], fill=TEAL)

    pad = 56
    # eyebrow
    eye = ImageFont.truetype(FONT_EYE, 27)
    d.text((pad, top+30), "ACATMAR · ASSOCIAÇÃO NÁUTICA BRASILEIRA", font=eye, fill=TEAL)

    # titulo: ajusta tamanho e quebra em ate 3 linhas
    def wrap(fs):
        f = ImageFont.truetype(FONT_TITLE, fs)
        palavras = titulo.upper().split()
        linhas, atual = [], ""
        for p in palavras:
            teste = (atual+" "+p).strip()
            if d.textlength(teste, font=f) <= W-pad*2:
                atual = teste
            else:
                linhas.append(atual); atual = p
        if atual: linhas.append(atual)
        return f, linhas
    fs = 46
    while fs > 26:
        f, linhas = wrap(fs)
        if len(linhas) <= 3: break
        fs -= 2
    if len(linhas) > 3:
        linhas = linhas[:3]; linhas[2] = linhas[2].rstrip('.')+"…"
    y = top+72
    for ln in linhas:
        d.text((pad, y), ln, font=f, fill=WHITE)
        y += int(fs*1.14)

    # url no canto
    url = ImageFont.truetype(FONT_EYE, 25)
    tw = d.textlength("WWW.ACATMAR.ORG", font=url)
    d.text((W-pad-tw, H-42), "WWW.ACATMAR.ORG", font=url, fill=(159, 192, 208))

    os.makedirs(os.path.dirname(saida), exist_ok=True)
    card.save(saida, quality=88, optimize=True)

def main():
    todas = json.load(open("noticias.json", encoding="utf-8"))["noticias"]
    for n in todas:
        if n.get("sem_card"):            # a imagem ja e um card pronto de compartilhamento
            import os
            p=f"media/share/{n['id']}.jpg"
            if os.path.exists(p): os.remove(p)
            continue
        make_card(n["imagem"], n["titulo"], f"media/share/{n['id']}.jpg")
    print(f"{len(todas)} cards de compartilhamento gerados em media/share/")

if __name__ == "__main__":
    main()
