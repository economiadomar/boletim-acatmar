#!/bin/bash
# =====================================================================
#  ACATMAR — publicar o site
#  Uso:  ./publicar.sh "mensagem do que mudou"
#
#  O que faz, na ordem:
#   1. Regera notícias, versão em inglês (/en/) e o sitemap.xml
#   2. Publica na Cloudflare Pages (INSTANTÂNEO, em segundos)
#   3. Faz backup do código no GitHub (não bloqueia)
#   4. Avisa os buscadores (Bing, Yandex, Copilot/ChatGPT) via IndexNow
# =====================================================================
set -e
cd "$(dirname "$0")"

MSG="${1:-Atualiza o site}"
SITE="https://www.acatmar.org"

echo ""
echo "🚢  PUBLICANDO O SITE DA ACATMAR"
echo "───────────────────────────────────────────────"

# 1 e 2 — versão em inglês + sitemap ---------------------------------
echo "1/4  Gerando páginas de notícias, versão em inglês e sitemap…"
python3 build-cards.py | sed 's/^/     /'
python3 build-noticias.py | sed 's/^/     /'
python3 tools/forum-agenda.py | sed 's/^/     /'
python3 tools/logo-optica.py >/dev/null && python3 tools/forum-patrocinadores.py | sed 's/^/     /'
python3 tools/bloco-palestrantes.py | sed 's/^/     /'
python3 build-en.py | sed 's/^/     /'

# valida os arquivos de conteúdo antes de subir
python3 - <<'PY'
import json, xml.dom.minidom, sys
try:
    for f in ("noticias.json", "projetos.json", "editions.json", "app/data/forum.json"):
        json.load(open(f))
    d = json.load(open("app/data/forum.json"))
    for k in ("evento", "programacao", "avisos", "patrocinadores", "versao"):
        assert k in d, "forum.json sem campo " + k
    import re, subprocess
    appv = int(re.search(r"var APP_V=(\d+);", open("app/app.js").read()).group(1))
    assert d.get("app_min", 0) <= appv, f"app_min ({d.get('app_min')}) maior que APP_V do app.js ({appv}): causaria recarga em loop"
    for js in ("app/app.js", "app/sw.js"):
        r = subprocess.run(["node", "-e", "new Function(require('fs').readFileSync(process.argv[1],'utf8'))", js], capture_output=True, text=True)
        assert r.returncode == 0, js + " com erro de sintaxe: " + r.stderr[:300]
    print("     app do Fórum validado (forum.json, app.js, sw.js)")
    xml.dom.minidom.parse("sitemap.xml")
    print("     conteúdo validado (JSONs e sitemap OK)")
except Exception as e:
    print("     ERRO no conteúdo:", e); sys.exit(1)
PY

# 3 — publicar na Cloudflare Pages (INSTANTÂNEO, independe do GitHub) --
echo "2/4  Publicando na Cloudflare Pages…"
DIST=/tmp/acatmar-dist
rm -rf "$DIST"; mkdir -p "$DIST"
rsync -a --exclude='.git' --exclude='*.py' --exclude='*.sh' --exclude='build-*' \
  --exclude='.indexnow-key' --exclude='.cache' --exclude='.DS_Store' --exclude='CNAME' \
  --exclude='GUIA.html' --exclude='assets/fonts' --exclude='data/cnpj/estabelecimentos_nautica.csv' \
  ./ "$DIST"/ 2>/dev/null
WOUT=$(npx wrangler pages deploy "$DIST" --project-name=acatmar --branch=main --commit-dirty=true 2>&1)
echo "$WOUT" | grep -iE 'success|deployment|http' | sed 's/^/     /'
if echo "$WOUT" | grep -qiE 'ERROR|failed'; then echo "$WOUT" | grep -iE 'ERROR|MiB|failed' | sed 's/^/     /'; echo "❌  DEPLOY FALHOU — site NÃO foi atualizado"; exit 1; fi

# backup/histórico no GitHub (não bloqueia; pode estar lento/fora)
echo "3/4  Backup no GitHub…"
if [ -n "$(git status --porcelain)" ]; then
  git add -A && git commit -q -m "$MSG"
  ( git push -q origin HEAD 2>/dev/null && echo "     backup enviado ao GitHub" \
    || echo "     (GitHub indisponível agora — backup será enviado depois; site já está no ar)" ) &
fi

# 5 — avisar os buscadores -------------------------------------------
echo "4/4  Avisando os buscadores (IndexNow)…"
KEY=$(cat .indexnow-key 2>/dev/null | tr -d '[:space:]')
if [ -z "$KEY" ]; then
  echo "     AVISO: chave do IndexNow não encontrada (.indexnow-key). Pulando."
else
  grep -o '<loc>[^<]*' sitemap.xml | sed 's/<loc>//' | sed 's/&amp;/\&/g' > /tmp/acatmar-urls.txt
  python3 - "$KEY" <<'PY' | sed 's/^/     /'
import sys, json, urllib.request
key = sys.argv[1]
urls = [l.strip() for l in open('/tmp/acatmar-urls.txt') if l.strip()]
payload = {"host": "www.acatmar.org", "key": key,
           "keyLocation": f"https://www.acatmar.org/{key}.txt", "urlList": urls}
req = urllib.request.Request("https://api.indexnow.org/IndexNow",
      data=json.dumps(payload).encode(),
      headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"{len(urls)} URLs enviadas — resposta: {r.status} {r.reason}")
except Exception as e:
    print("não foi possível avisar os buscadores:", e)
PY
fi

echo "───────────────────────────────────────────────"
echo "✅  Pronto!  $SITE"
echo ""
echo "    Lembrete: para uma matéria nova entrar rápido no Google,"
echo "    peça a indexação no Search Console (Inspeção de URL)."
echo ""
