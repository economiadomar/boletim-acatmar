#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera uma pagina ESTATICA por materia, em /n/<id>.html (PT) e /en/n/<id>.html (EN),
com a foto, o titulo, a descricao e o texto ja embutidos no HTML.

Por que: WhatsApp, Facebook e LinkedIn NAO rodam JavaScript. A pagina noticia.html
monta o conteudo por JS, entao o robo desses apps nunca via a foto certa. Com paginas
estaticas, a foto de cada materia aparece no compartilhamento e o Google le o texto real.

Rode:  python3 build-noticias.py   (o publicar.sh ja chama automaticamente)
"""
import re, os, json, html
from PIL import Image

BASE = "https://www.acatmar.org"
LOGO = BASE + "/media/logos/acatmar-vertical-02.png"

MESES_PT = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
MESES_EN = ['January','February','March','April','May','June','July','August','September','October','November','December']

def data_fmt(iso, en):
    a,m,d = iso.split('-'); mi=int(m)-1
    return f"{MESES_EN[mi]} {int(d)}, {a}" if en else f"{int(d)} de {MESES_PT[mi]} de {a}"

def dimensoes(caminho):
    try:
        with Image.open(caminho) as im: return im.size
    except Exception: return (1200, 630)

def sem_html(s):
    return re.sub(r'\s+',' ', re.sub(r'<[^>]+>','', s)).strip()

# ---- pega estilo, cabecalho e rodape da noticia.html (fonte unica de estilo) ----
base_html = open("noticia.html", encoding="utf-8").read()
STYLE  = re.search(r'<style>.*?</style>', base_html, re.S).group(0)
CHROME = re.search(r'<a class="promobar".*?<div class="mobmenu" id="mobmenu">.*?</div>', base_html, re.S).group(0)
FOOTER = re.search(r'<footer>.*?</footer>', base_html, re.S).group(0)

# caminhos relativos -> root-relative (funcionam em qualquer profundidade de pasta)
def raiz(t):
    t = re.sub(r'(src|href)="(media/|assets/)', r'\1="/\2', t)
    t = re.sub(r'(href)="(index\.html|noticias\.html|sobre\.html|associe-se\.html|privacidade\.html|cookies\.html)', r'\1="/\2', t)
    return t
CHROME = raiz(CHROME); FOOTER = raiz(FOOTER)

def artigo_html(n, en):
    titulo = n.get('titulo_en' if en else 'titulo') or n['titulo']
    categoria = n.get('categoria_en' if en else 'categoria') or n.get('categoria','')
    corpo = n.get('corpo_en' if en else 'corpo') or n.get('corpo',[])
    body = ''.join('<p>'+p+'</p>' for p in corpo)
    hero_cls = 'hero-img inteira' if n.get('imagem_inteira') else 'hero-img'
    out  = f'<a class="back" href="{"/en/news.html" if en else "/noticias.html"}">{"← All news" if en else "← Todas as notícias"}</a>'
    if categoria: out += f'<div><span class="cat">{html.escape(categoria)}</span></div>'
    out += f'<h1 class="title">{html.escape(titulo)}</h1>'
    out += f'<div class="meta">{data_fmt(n["data"], en)}</div>'
    out += f'<img class="{hero_cls}" src="/{n["imagem"]}" alt="{html.escape(titulo)}">'
    if n.get('credito'): out += f'<div class="credito">{"Photo: " if en else "Foto: "}{html.escape(n["credito"])}</div>'
    out += f'<div class="body">{body}</div>'
    g = n.get('galeria') or []
    if g:
        solo = ' solo' if len(g)==1 else ''
        out += f'<div class="gallery{solo}">'+''.join(f'<img loading="lazy" src="/{s}" alt="{html.escape(titulo)}">' for s in g)+'</div>'
    if n.get('apoiadores'):
        tit = (n.get('apoiadores_titulo_en') if en else n.get('apoiadores_titulo')) or ('Organizers and supporters' if en else 'Realização e apoiadores')
        out += f'<div class="apoiadores"><h2>{html.escape(tit)}</h2>'
        for gr in n['apoiadores']:
            nome = (gr.get('grupo_en') if en else gr.get('grupo')) or ''
            out += f'<div class="grp"><b>{html.escape(nome)}</b>'+' · '.join(gr['itens'])+'</div>'
        out += '</div>'
    if n.get('link'):
        lk = n['link']
        if lk == 'associe-se.html': lk = '/en/join.html' if en else '/associe-se.html'
        label = (n.get('link_label_en') if en else n.get('link_label')) or ('Learn more' if en else 'Saiba mais')
        out += f'<a class="more-link" href="{lk}" target="_blank" rel="noopener">{html.escape(label)} →</a>'
    page_url = f"{BASE}/en/n/{n['id']}.html" if en else f"{BASE}/n/{n['id']}.html"
    out += (f'<div class="share"><span>{"Share" if en else "Compartilhar"}</span>'
            f'<a target="_blank" rel="noopener" href="https://wa.me/?text={html.escape(titulo)}%20{page_url}">WhatsApp</a>'
            f'<a target="_blank" rel="noopener" href="https://www.facebook.com/sharer/sharer.php?u={page_url}">Facebook</a></div>')
    return out, titulo, sem_html(n.get('resumo_en' if en else 'resumo') or titulo)

def related_html(atual, todas, en):
    outros = [x for x in todas if x['id'] != atual['id']][:3]
    if not outros: return ''
    cards = ''
    for x in outros:
        t = x.get('titulo_en' if en else 'titulo') or x['titulo']
        href = f"/en/n/{x['id']}.html" if en else f"/n/{x['id']}.html"
        cards += (f'<a class="rc" href="{href}"><img loading="lazy" src="/{x["imagem"]}" alt="{html.escape(t)}">'
                  f'<div class="b"><div class="d">{data_fmt(x["data"], en)}</div><h3>{html.escape(t)}</h3></div></a>')
    return f'<section class="related"><h2>{"More news" if en else "Mais notícias"}</h2><div class="rg">{cards}</div></section>'

def pagina(n, todas, en):
    art, titulo, desc = artigo_html(n, en)
    url    = f"{BASE}/en/n/{n['id']}.html" if en else f"{BASE}/n/{n['id']}.html"
    url_pt = f"{BASE}/n/{n['id']}.html"
    url_en = f"{BASE}/en/n/{n['id']}.html"
    card_rel = f"media/share/{n['id']}.jpg"
    if os.path.exists(card_rel):
        img = f"{BASE}/{card_rel}"; iw, ih = 1200, 630
    else:
        img = f"{BASE}/{n['imagem']}"; iw, ih = dimensoes(n['imagem'])
    lang   = 'en' if en else 'pt-BR'
    tit_tab = html.escape(titulo) + " — ACATMAR"
    dsc = html.escape(desc)
    ld = json.dumps({"@context":"https://schema.org","@type":"NewsArticle","headline":titulo,
        "description":desc,"image":[img],"datePublished":n['data'],"dateModified":n['data'],
        "inLanguage":lang,"mainEntityOfPage":{"@type":"WebPage","@id":url},
        "author":{"@type":"Organization","name":"ACATMAR — Associação Náutica Brasileira","url":BASE+'/'},
        "publisher":{"@type":"Organization","name":"ACATMAR — Associação Náutica Brasileira",
            "logo":{"@type":"ImageObject","url":LOGO}}}, ensure_ascii=False)
    # botao de idioma vira link para a outra versao
    chrome = CHROME.replace('<button id="lb" class="langbtn" type="button">EN</button>',
        f'<a class="langbtn" href="{("/n/"+n["id"]+".html") if en else ("/en/n/"+n["id"]+".html")}" style="text-decoration:none;display:inline-flex;align-items:center">{"PT" if en else "EN"}</a>')
    head = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{tit_tab}</title>
<meta name="description" content="{dsc}">
<meta name="author" content="ACATMAR — Associação Náutica Brasileira">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="ACATMAR — Associação Náutica Brasileira">
<meta property="og:type" content="article">
<meta property="og:locale" content="{'en_US' if en else 'pt_BR'}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{html.escape(titulo)}">
<meta property="og:description" content="{dsc}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="{iw}">
<meta property="og:image:height" content="{ih}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(titulo)}">
<meta name="twitter:description" content="{dsc}">
<meta name="twitter:image" content="{img}">
<link rel="alternate" hreflang="pt-BR" href="{url_pt}">
<link rel="alternate" hreflang="en" href="{url_en}">
<link rel="alternate" hreflang="x-default" href="{url_pt}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Barlow+Condensed:wght@500;600;700&family=PT+Serif:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
{STYLE}
<script type="application/ld+json">{ld}</script>
</head>
<body>
{chrome}
<article class="art">{art}</article>
{related_html(n, todas, en)}
{FOOTER}
<script>
var EN={str(en).lower()};
document.documentElement.lang=EN?'en':'pt-BR';
if(EN){{document.querySelectorAll('.nl,.promobar [data-en],footer [data-en],.mobmenu [data-en]').forEach(function(x){{if(x.getAttribute('data-en'))x.textContent=x.getAttribute('data-en');}});
  var a=document.getElementById('assoc');if(a)a.textContent='Join us';}}
(function(){{var hb=document.getElementById('hambBtn'),mm=document.getElementById('mobmenu');if(!hb||!mm)return;
  hb.addEventListener('click',function(){{var o=mm.classList.toggle('open');hb.textContent=o?'\\u2715':'\\u2630';}});}})();
</script>
<script src="/assets/cookie-consent.js" defer></script>
</body>
</html>'''
    return head

def main():
    todas = json.load(open("noticias.json", encoding="utf-8"))["noticias"]
    os.makedirs("n", exist_ok=True)
    os.makedirs("en/n", exist_ok=True)
    for n in todas:
        open(f"n/{n['id']}.html", "w", encoding="utf-8").write(pagina(n, todas, False))
        open(f"en/n/{n['id']}.html", "w", encoding="utf-8").write(pagina(n, todas, True))
    print(f"{len(todas)} matérias estáticas geradas em /n/ e /en/n/")

if __name__ == "__main__":
    main()
