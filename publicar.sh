#!/bin/bash
# =====================================================================
#  ACATMAR — publicar o site
#  Uso:  ./publicar.sh "mensagem do que mudou"
#
#  O que faz, na ordem:
#   1. Regera a versão em inglês (/en/) a partir das páginas em português
#   2. Atualiza o sitemap.xml com todas as URLs (PT + EN)
#   3. Envia tudo para o ar (GitHub Pages → www.acatmar.org)
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
echo "1/4  Gerando a versão em inglês e o sitemap…"
python3 build-en.py | sed 's/^/     /'

# valida os arquivos de conteúdo antes de subir
python3 - <<'PY'
import json, xml.dom.minidom, sys
try:
    for f in ("noticias.json", "projetos.json", "editions.json"):
        json.load(open(f))
    xml.dom.minidom.parse("sitemap.xml")
    print("     conteúdo validado (JSONs e sitemap OK)")
except Exception as e:
    print("     ERRO no conteúdo:", e); sys.exit(1)
PY

# 3 — publicar --------------------------------------------------------
echo "2/4  Enviando para o ar…"
if [ -z "$(git status --porcelain)" ]; then
  echo "     nada mudou, seguindo para a notificação"
else
  git add -A
  git commit -q -m "$MSG"
  git push -q origin HEAD
  echo "     publicado: $MSG"
fi

# 4 — esperar o site atualizar ---------------------------------------
echo "3/4  Aguardando o site atualizar…"
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 12 "$SITE/sitemap.xml" || true)
  [ "$code" = "200" ] && break
  sleep 10
done
echo "     site respondendo"

# 5 — avisar os buscadores -------------------------------------------
echo "4/4  Avisando os buscadores (IndexNow)…"
KEY=$(cat .indexnow-key 2>/dev/null | tr -d '[:space:]')
if [ -z "$KEY" ]; then
  echo "     AVISO: chave do IndexNow não encontrada (.indexnow-key). Pulando."
else
  curl -s "$SITE/sitemap.xml" | grep -o '<loc>[^<]*' | sed 's/<loc>//' | sed 's/&amp;/\&/g' > /tmp/acatmar-urls.txt
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
