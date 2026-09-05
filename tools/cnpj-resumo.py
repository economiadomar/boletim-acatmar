#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recalcula data/cnpj/resumo.json a partir de estabelecimentos_nautica.csv com o nucleo estrito de CNAEs nauticos."""
import csv, json, os, collections, datetime, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "cnpj")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rais import CNAE
NUCLEO = {"3012100": "Construção de embarcações para esporte e lazer", "3011302": "Construção de embarcações para uso comercial e usos especiais, exceto de grande porte",
          "3317102": "Manutenção e reparação de embarcações para esporte e lazer", "4763605": "Comércio varejista de embarcações e outros veículos recreativos",
          "7719501": "Locação de embarcações sem tripulação, exceto para fins recreativos", "5099801": "Transporte aquaviário para passeios turísticos",
          "4329102": "Instalação de equipamentos para orientação à navegação"}
rows = list(csv.DictReader(open(os.path.join(OUT, "estabelecimentos_nautica.csv"), encoding="utf-8")))
pasta = sys.argv[1] if len(sys.argv) > 1 else "2026-08"
ACENTOS = {"FLORIANOPOLIS": "Florianópolis", "ITAJAI": "Itajaí", "BALNEARIO CAMBORIU": "Balneário Camboriú", "PALHOCA": "Palhoça", "SAO JOSE": "São José", "BIGUACU": "Biguaçu", "CAMBORIU": "Camboriú", "SAO FRANCISCO DO SUL": "São Francisco do Sul", "GOVERNADOR CELSO RAMOS": "Governador Celso Ramos", "CRICIUMA": "Criciúma", "CHAPECO": "Chapecó", "PICARRAS": "Piçarras", "BALNEARIO PICARRAS": "Balneário Piçarras", "ITAPEMA": "Itapema", "BOMBINHAS": "Bombinhas", "TIJUCAS": "Tijucas", "LAGUNA": "Laguna", "GAROPABA": "Garopaba", "IMBITUBA": "Imbituba", "PENHA": "Penha", "PORTO BELO": "Porto Belo", "NAVEGANTES": "Navegantes", "JOINVILLE": "Joinville", "BLUMENAU": "Blumenau", "BARRA VELHA": "Barra Velha", "SAO JOAO BATISTA": "São João Batista", "BRUSQUE": "Brusque", "GUARAMIRIM": "Guaramirim", "JARAGUA DO SUL": "Jaraguá do Sul", "ARARANGUA": "Araranguá", "TUBARAO": "Tubarão", "LAGES": "Lages"}
def title(m):
    return ACENTOS.get(m, " ".join(w.capitalize() if w not in ("DE", "DO", "DA", "DOS", "DAS") else w.lower() for w in m.split()))
core = [r for r in rows if r["cnae_principal"] in NUCLEO]
sc = [r for r in core if r["uf"] == "SC"]
res = {"pasta": pasta, "gerado_em": datetime.date.today().isoformat(), "fonte": "Receita Federal, dados abertos do CNPJ (estabelecimentos ativos), extração ACATMAR",
       "definicao": {c: {"descricao": d, "grupo": "Setor náutico (núcleo)"} for c, d in NUCLEO.items()},
       "brasil_setor_nautico_principal_por_uf": dict(collections.Counter(r["uf"] for r in core).most_common()),
       "brasil_construcao_esporte_lazer_por_uf": dict(collections.Counter(r["uf"] for r in core if r["cnae_principal"] == "3012100").most_common()),
       "sc_por_cnae": {c: {"nome": NUCLEO[c], "grupo": "Setor náutico (núcleo)", "estabelecimentos_ativos": v} for c, v in collections.Counter(r["cnae_principal"] for r in sc).most_common()},
       "sc_setor_nautico_por_municipio": {title(m): v for m, v in collections.Counter(r["municipio"] for r in sc).most_common(30)},
       "sc_setor_nautico_por_porte": dict(collections.Counter(r["porte"] or "Não informado" for r in sc)),
       "sc_setor_nautico_mei": sum(1 for r in sc if r["mei"] == "S"),
       "sc_setor_nautico_total_principal": len(sc),
       "sc_com_cnae_nautico_secundario": sum(1 for r in rows if r["uf"] == "SC" and r["cnae_principal"] not in NUCLEO and set(r["cnae_secundaria"].split(",")) & set(NUCLEO)),
       "sc_matriz_filial": dict(collections.Counter("matriz" if r["matriz_filial"] == "1" else "filial" for r in sc))}
json.dump(res, open(os.path.join(OUT, "resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("SC nucleo:", len(sc), "| por CNAE:", {NUCLEO[c][:30]: v["estabelecimentos_ativos"] for c, v in res["sc_por_cnae"].items()})
print("SC municipios:", list(res["sc_setor_nautico_por_municipio"].items())[:10])
print("SC porte:", res["sc_setor_nautico_por_porte"], "| MEI:", res["sc_setor_nautico_mei"], "| secundario:", res["sc_com_cnae_nautico_secundario"])
print("Brasil por UF:", list(res["brasil_setor_nautico_principal_por_uf"].items())[:8])
print("3012100 por UF:", list(res["brasil_construcao_esporte_lazer_por_uf"].items())[:8])
