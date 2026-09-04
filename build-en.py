#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera a versão em inglês do site em /en/ com URLs próprias (indexáveis pelo Google).
Rode este script sempre que alterar as páginas em português:  python3 build-en.py
"""
import re, os, json, datetime, shutil

BASE = "https://www.acatmar.org"
PAGES = {                       # arquivo PT -> arquivo EN (dentro de /en/)
    "index.html":      "index.html",
    "sobre.html":      "about.html",
    "noticias.html":   "news.html",
    "noticia.html":    "article.html",
    "projeto.html":    "project.html",
    "associe-se.html": "join.html",
    "projetos.html":  "projects.html",
    "viewer.html":     "bulletin.html",
    "obrigado.html":   "thank-you.html",
    "lei.html":        "public-utility-law.html",
    "privacidade.html":"privacy-policy.html",
    "cookies.html":    "cookie-policy.html",
    "numeros.html":    "numbers.html",
}

# meta tags em inglês (title / description / keywords)
META_EN = {
 "index.html": ("Brazilian Nautical Association | ACATMAR — Sea Economy & Marine Industry in Brazil",
   "ACATMAR is the Brazilian Nautical Association, representing Brazil's Sea Economy since 2008: marine industry, marinas, boatbuilding, services, nautical tourism, fishing and mariculture.",
   "brazilian nautical association, nautical sector brazil, sea economy, blue economy brazil, marine industry brazil, marinas brazil, boat industry, nautical tourism"),
 "about.html": ("About Us | ACATMAR — Brazilian Nautical Association",
   "Learn about ACATMAR, the non-profit association representing Brazil's Sea Economy since 2008: industry, trade, services and nautical tourism.",
   "about acatmar, brazilian nautical association, sea economy brazil, blue economy, nautical industry"),
 "news.html": ("Nautical Sector & Sea Economy News | ACATMAR Brazil",
   "News from Brazil's nautical sector: events, international cooperation, public policy, marinas, boatbuilding industry and the Sea Economy.",
   "nautical news brazil, sea economy news, blue economy, brazilian marine industry, boat show brazil"),
 "article.html": ("News | ACATMAR — Brazilian Nautical Association",
   "News from ACATMAR about Brazil's nautical sector and the Sea Economy.",
   "nautical news brazil, sea economy, acatmar"),
 "project.html": ("Projects | ACATMAR — Brazilian Nautical Association",
   "ACATMAR projects driving Brazil's Sea Economy: technical training, marinas, school of the sea, international missions and sector development.",
   "nautical projects brazil, sea economy projects, marina legal, school of the sea, technical missions"),
 "projects.html": ("Projects | ACATMAR — Brazilian Nautical Association",
   "The initiatives through which ACATMAR moves Brazil's Sea Economy: training, infrastructure, technical missions and sector development.",
   "nautical projects brazil, sea economy, acatmar forum, marina legal, school of the sea"),
 "join.html": ("Become a Member | ACATMAR — Brazilian Nautical Association",
   "Join ACATMAR and strengthen Brazil's nautical sector. Representation, networking, technical visits, international events and legal support for your company.",
   "join nautical association brazil, membership, brazilian marine industry, nautical business network"),
 "bulletin.html": ("Digital Bulletin | ACATMAR — Brazilian Nautical Association",
   "Browse ACATMAR's digital bulletins with the main actions and achievements of Brazil's nautical sector.",
   "nautical bulletin, brazil marine industry report, sea economy"),
 "thank-you.html": ("Registration sent | ACATMAR", "Your membership form has been sent to the ACATMAR team.", "acatmar membership"),
 "public-utility-law.html": ("Municipal Public Utility Law | ACATMAR",
   "Municipal Law No. 10,711/2020 of Florianópolis, declaring ACATMAR an entity of public utility.",
   "public utility, acatmar law, florianopolis"),
 "privacy-policy.html": ("Privacy Policy | ACATMAR",
   "ACATMAR's Privacy Policy in accordance with the Brazilian General Data Protection Law (LGPD).",
   "privacy policy, lgpd, data protection"),
 "cookie-policy.html": ("Cookie Policy | ACATMAR",
   "How the ACATMAR website uses cookies and local storage.",
   "cookie policy, privacy, lgpd"),
 "numbers.html": ("Sea Economy in Numbers | Brazilian Nautical Sector Data | ACATMAR",
   "ACATMAR reference page with the key figures of Brazil's Sea Economy and nautical sector: jobs, companies, boat production, Itajaí and Santa Catarina exports, foreign trade, legal framework (ZENAs) and US tariffs. Data with source, date and methodology.",
   "sea economy data, blue economy brazil statistics, brazilian nautical industry numbers, boat production santa catarina, boat exports itajai, marine industry jobs brazil, acatmar data"),
}

os.makedirs("en", exist_ok=True)

def para_en(t, pt_file, en_file):
    # 1) força o inglês (sem depender da escolha guardada no navegador)
    t = t.replace("localStorage.getItem('acatmar_lang')||'pt'", "'en'")
    t = t.replace("localStorage.getItem('acatmar_lang')==='en'", "true")

    # 2) caminhos relativos passam a subir um nível
    t = re.sub(r'(src|href)="((?:media|assets)/)', r'\1="../\2', t)
    t = re.sub(r"fetch\('([a-z-]+\.json)", r"fetch('../\1", t)
    t = t.replace("'editions/'", "'../editions/'")
    t = t.replace('"editions/', '"../editions/')
    t = t.replace('src="assets/', 'src="../assets/')

    # 3) links internos apontam para os equivalentes em inglês
    for pt, en in PAGES.items():
        t = re.sub(r'(href=")' + re.escape(pt), r'\1' + en, t)
        t = re.sub(r"('|\")" + re.escape(pt) + r"(\?|'|\")", r"\1" + en + r"\2", t)
    t = t.replace("index.html#", "index.html#")   # âncoras seguem válidas

    # 4) o botão de idioma passa a levar para a versão em português
    volta = pt_file if pt_file != "index.html" else ""
    t = re.sub(r"<button id=\"lb\" class=\"langbtn\" type=\"button\">EN</button>",
               f'<a class="langbtn" href="../{volta}" hreflang="pt-BR" aria-label="Ver em português" style="text-decoration:none;display:inline-flex;align-items:center">PT</a>', t)
    t = re.sub(r"<button id=\"langBtn\"[^>]*>EN</button>",
               f'<a class="langbtn" id="langBtn" href="../{volta}" hreflang="pt-BR" aria-label="Ver em português" style="text-decoration:none;display:inline-flex;align-items:center">PT</a>', t)

    # 5) meta tags em inglês + hreflang
    titulo, desc, kw = META_EN[en_file]
    canon_en = f"{BASE}/en/" if en_file == "index.html" else f"{BASE}/en/{en_file}"
    canon_pt = f"{BASE}/" if pt_file == "index.html" else f"{BASE}/{pt_file}"
    if pt_file == "numeros.html":  # pagina de referencia: URL limpa (Cloudflare redireciona .html)
        canon_pt, canon_en = canon_pt[:-5], canon_en[:-5]
    t = re.sub(r'<title>.*?</title>', f"<title>{titulo}</title>", t, count=1, flags=re.S)
    t = re.sub(r'\n\s*<meta name="description"[^>]*>', f'\n<meta name="description" content="{desc}">', t, count=1)
    t = re.sub(r'\n\s*<meta name="keywords"[^>]*>', f'\n<meta name="keywords" content="{kw}">', t, count=1)
    t = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{canon_en}">', t, count=1)
    t = re.sub(r'<meta property="og:url"[^>]*>', f'<meta property="og:url" content="{canon_en}">', t, count=1)
    t = re.sub(r'<meta property="og:title"[^>]*>', f'<meta property="og:title" content="{titulo}">', t, count=1)
    t = re.sub(r'<meta property="og:description"[^>]*>', f'<meta property="og:description" content="{desc}">', t, count=1)
    t = re.sub(r'<meta property="og:locale"[^>]*>', '<meta property="og:locale" content="en_US">', t, count=1)
    t = re.sub(r'<meta property="og:locale:alternate"[^>]*>', '<meta property="og:locale:alternate" content="pt_BR">', t, count=1)
    t = re.sub(r'<meta name="twitter:title"[^>]*>', f'<meta name="twitter:title" content="{titulo}">', t, count=1)
    t = re.sub(r'<meta name="twitter:description"[^>]*>', f'<meta name="twitter:description" content="{desc}">', t, count=1)
    hre = (f'\n<link rel="alternate" hreflang="pt-BR" href="{canon_pt}">'
           f'\n<link rel="alternate" hreflang="en" href="{canon_en}">'
           f'\n<link rel="alternate" hreflang="x-default" href="{canon_pt}">')
    t = t.replace('</head>', hre + '\n</head>', 1)
    t = t.replace("'/n/'+id+'.html'", "'/en/n/'+id+'.html'")
    t = t.replace('<html lang="pt-BR">', '<html lang="en">', 1)

    # 6) conteudo carregado por JavaScript: corrige caminhos de media e links
    corretor = """
<script>
/* /en/ fica um nivel abaixo: ajusta caminhos de midia e links vindos do JSON */
(function(){
  function ajustar(raiz){
    (raiz.querySelectorAll?raiz.querySelectorAll('img'):[]).forEach(function(i){
      var s=i.getAttribute('src')||'';
      if(/^(media|editions)\//.test(s)) i.setAttribute('src','../'+s);
    });
    (raiz.querySelectorAll?raiz.querySelectorAll('a[href^="noticia.html"],a[href^="projeto.html"],a[href^="viewer.html"],a[href^="associe-se.html"],a[href^="noticias.html"],a[href^="sobre.html"]'):[]).forEach(function(a){
      var h=a.getAttribute('href');
      a.setAttribute('href', h.replace(/^noticia\.html/,'article.html')
                              .replace(/^noticias\.html/,'news.html')
                              .replace(/^projeto\.html/,'project.html')
                              .replace(/^viewer\.html/,'bulletin.html')
                              .replace(/^associe-se\.html/,'join.html')
                              .replace(/^sobre\.html/,'about.html'));
    });
  }
  ajustar(document);
  new MutationObserver(function(muts){
    muts.forEach(function(m){ m.addedNodes.forEach(function(n){ if(n.nodeType===1){ ajustar(n);
      if(n.tagName==='IMG'&&/^media\//.test(n.getAttribute('src')||'')) n.setAttribute('src','../'+n.getAttribute('src'));
    }});});
  }).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>
"""
    t = t.replace('</body>', corretor + '</body>', 1)

    return t

gerados = []
for pt, en in PAGES.items():
    if not os.path.exists(pt):
        continue
    t = open(pt, encoding="utf-8").read()
    open(os.path.join("en", en), "w", encoding="utf-8").write(para_en(t, pt, en))
    gerados.append(en)

# ---- hreflang também nas páginas em português ----
for pt, en in PAGES.items():
    if not os.path.exists(pt):
        continue
    t = open(pt, encoding="utf-8").read()
    t = re.sub(r'\n<link rel="alternate" hreflang="[^"]*"[^>]*>', '', t)
    canon_pt = f"{BASE}/" if pt == "index.html" else f"{BASE}/{pt}"
    canon_en = f"{BASE}/en/" if en == "index.html" else f"{BASE}/en/{en}"
    hre = (f'\n<link rel="alternate" hreflang="pt-BR" href="{canon_pt}">'
           f'\n<link rel="alternate" hreflang="en" href="{canon_en}">'
           f'\n<link rel="alternate" hreflang="x-default" href="{canon_pt}">')
    t = t.replace('</head>', hre + '\n</head>', 1)
    open(pt, "w", encoding="utf-8").write(t)

# ---- sitemap com as duas versões ----
hoje = datetime.date.today().isoformat()
urls = []
def add(loc, prio, freq, last=None, alts=None):
    urls.append((loc, prio, freq, last or hoje, alts or []))

pares = [("", "en/", "1.0", "weekly"), ("sobre.html", "en/about.html", "0.9", "monthly"),
         ("noticias.html", "en/news.html", "0.9", "weekly"),
         ("projetos.html", "en/projects.html", "0.9", "weekly"), ("associe-se.html", "en/join.html", "0.9", "monthly"),
         ("numeros.html", "en/numbers.html", "0.9", "weekly"),
         ("lei.html", "en/public-utility-law.html", "0.4", "yearly"),
         ("privacidade.html", "en/privacy-policy.html", "0.3", "yearly"),
         ("cookies.html", "en/cookie-policy.html", "0.3", "yearly")]
for p, e, prio, freq in pares:
    add(f"{BASE}/{p}", prio, freq, alts=[("pt-BR", f"{BASE}/{p}"), ("en", f"{BASE}/{e}")])
    add(f"{BASE}/{e}", prio, freq, alts=[("pt-BR", f"{BASE}/{p}"), ("en", f"{BASE}/{e}")])

# URL limpa do Forum — usada nos e-mails e materiais (o Gmail bloqueia links com "?")
add(f"{BASE}/forum-acatmar.html", "0.9", "monthly",
    alts=[("pt-BR", f"{BASE}/forum-acatmar.html"),
          ("en", f"{BASE}/en/project.html?id=forum-acatmar")])

for n in sorted(json.load(open("noticias.json"))["noticias"], key=lambda a: a["data"], reverse=True):
    pt_u = f"{BASE}/n/{n['id']}.html"; en_u = f"{BASE}/en/n/{n['id']}.html"
    add(pt_u, "0.8", "monthly", n["data"], [("pt-BR", pt_u), ("en", en_u)])
    add(en_u, "0.8", "monthly", n["data"], [("pt-BR", pt_u), ("en", en_u)])
for p in json.load(open("projetos.json"))["projetos"]:
    pt_u = f"{BASE}/projeto.html?id={p['id']}"; en_u = f"{BASE}/en/project.html?id={p['id']}"
    add(pt_u, "0.8", "monthly", None, [("pt-BR", pt_u), ("en", en_u)])
    add(en_u, "0.8", "monthly", None, [("pt-BR", pt_u), ("en", en_u)])
for e in json.load(open("editions.json"))["editions"]:
    add(f"{BASE}/viewer.html?ed={e['id']}", "0.6", "yearly")

out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for loc, prio, freq, last, alts in urls:
    esc = lambda s: s.replace("&", "&amp;")
    out.append("  <url>")
    out.append(f"    <loc>{esc(loc)}</loc>")
    for lang, href in alts:
        out.append(f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{esc(href)}"/>')
    out.append(f"    <lastmod>{last}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>")
    out.append("  </url>")
out.append("</urlset>")
open("sitemap.xml", "w", encoding="utf-8").write("\n".join(out))

print(f"{len(gerados)} páginas em inglês geradas em /en/")
print(f"sitemap.xml com {len(urls)} URLs (PT + EN com hreflang)")
