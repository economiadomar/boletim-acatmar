#!/bin/bash
# Atualiza os dados de comércio exterior da página Economia do Mar em Números e publica.
# Rodar uma vez por mês, depois que o MDIC divulga o mês anterior (em geral na primeira semana).
#   ./tools/atualizar-comex.sh            -> extrai (2010 em diante), injeta e publica
#   ./tools/atualizar-comex.sh --sem-publicar
set -e
cd "$(dirname "$0")/.."
echo "1) Extraindo do Comex Stat (API pública do MDIC)..."
python3 tools/comex.py 2010
echo "2) Injetando na página..."
python3 tools/comex-html.py
python3 tools/uf-html.py
python3 tools/limpar-fontes.py
if [ "$1" != "--sem-publicar" ]; then
  echo "3) Publicando..."
  ./publicar.sh "Numeros: atualizacao mensal do Comex Stat (extracao ACATMAR)"
fi
echo "Pronto."
