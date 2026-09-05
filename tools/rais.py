#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator ACATMAR da RAIS (microdados públicos por estabelecimento, PDET/MTE).

Entrada: arquivos RAIS_ESTAB_PUB.COMT (um por ano), csv com aspas, latin-1.
Saída, em data/rais/:
  - nautica_uf_ANO.csv          estabelecimentos e vínculos ativos por UF e CNAE (cadeia náutica e naval)
  - nautica_municipio_sc_ANO.csv idem por município de SC
  - resumo.json                  indicadores prontos
Uso: python3 tools/rais.py ANO=CAMINHO [ANO=CAMINHO ...]
"""
import csv, json, os, sys, urllib.request, collections, gzip

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "rais")
os.makedirs(OUT, exist_ok=True)

# CNAE 2.3 subclasses: cadeia nautica e naval + pesca + portos (definicao ACATMAR, explicitada na pagina)
CNAE = {
    # construcao de embarcacoes (os tres CNAEs de construcao juntos: os estaleiros se registram em qualquer um deles)
    "3012100": ("Construção de embarcações para esporte e lazer", "Construção de embarcações"),
    "3011302": ("Construção de embarcações para uso comercial e usos especiais, exceto de grande porte", "Construção de embarcações"),
    "3011301": ("Construção de embarcações de grande porte", "Construção de embarcações"),
    # manutencao e reparo
    "3317102": ("Manutenção e reparação de embarcações para esporte e lazer", "Manutenção e reparo de embarcações"),
    "3317101": ("Manutenção e reparação de embarcações e estruturas flutuantes", "Manutenção e reparo de embarcações"),
    # comercio e servicos nauticos
    "4763605": ("Comércio varejista de embarcações e outros veículos recreativos", "Comércio e serviços náuticos"),
    "7719501": ("Locação de embarcações sem tripulação, exceto para fins recreativos", "Comércio e serviços náuticos"),
    "5099801": ("Transporte aquaviário para passeios turísticos", "Comércio e serviços náuticos"),
    "4329102": ("Instalação de equipamentos para orientação à navegação", "Comércio e serviços náuticos"),
    # portos e navegacao
    "5231101": ("Administração da infraestrutura portuária", "Portos e navegação"),
    "5231102": ("Atividades do operador portuário", "Portos e navegação"),
    "5232000": ("Atividades de agenciamento marítimo", "Portos e navegação"),
    "5239701": ("Serviços de praticagem", "Portos e navegação"),
    "5239799": ("Atividades auxiliares dos transportes aquaviários", "Portos e navegação"),
    "5011401": ("Transporte marítimo de cabotagem, carga", "Portos e navegação"),
    "5030101": ("Navegação de apoio marítimo", "Portos e navegação"),
    "5030102": ("Navegação de apoio portuário", "Portos e navegação"),
    # pesca e aquicultura
    "0311601": ("Pesca de peixes em água salgada", "Pesca e aquicultura"),
    "0311602": ("Pesca de crustáceos e moluscos em água salgada", "Pesca e aquicultura"),
    "0311604": ("Atividades de apoio à pesca em água salgada", "Pesca e aquicultura"),
    "0321301": ("Criação de peixes em água salgada e salobra", "Pesca e aquicultura"),
    "0321302": ("Criação de camarões em água salgada e salobra", "Pesca e aquicultura"),
    "0321303": ("Criação de ostras e mexilhões em água salgada e salobra", "Pesca e aquicultura"),
    "0321305": ("Atividades de apoio à aquicultura em água salgada e salobra", "Pesca e aquicultura"),
    "0321399": ("Cultivos e semicultivos da aquicultura em água salgada e salobra", "Pesca e aquicultura"),
    "1020101": ("Preservação de peixes, crustáceos e moluscos", "Pesca e aquicultura"),
    "1020102": ("Fabricação de conservas de peixes, crustáceos e moluscos", "Pesca e aquicultura"),
}
UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}


def municipios():
    cf = os.path.join(OUT, ".municipios_ibge.json")
    if os.path.exists(cf):
        return json.load(open(cf, encoding="utf-8"))
    req = urllib.request.Request("https://servicodados.ibge.gov.br/api/v1/localidades/municipios", headers={"User-Agent": "ACATMAR-numeros/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    lst = json.loads(raw.decode("utf-8"))
    m = {str(x["id"])[:6]: x["nome"] for x in lst}
    json.dump(m, open(cf, "w", encoding="utf-8"), ensure_ascii=False)
    return m


MUN = municipios()


def processa(ano, caminho):
    print(f"RAIS {ano}: {caminho}")
    uf_cnae = collections.defaultdict(lambda: [0, 0, 0])   # (uf, cnae) -> [estab c/ vinculo, vinculos ativos, estab declarantes]
    mun_cnae = collections.defaultdict(lambda: [0, 0, 0])  # (mun, cnae) -> idem, so SC
    econ_mar_sc_mun = collections.defaultdict(lambda: [0, 0])  # municipio SC -> [estab, vinculos] de todos os CNAEs da lista
    total_sc = [0, 0]
    n = 0
    with open(caminho, encoding="latin-1", newline="") as f:
        rd = csv.reader(f)
        head = next(rd)
        ix = {h: i for i, h in enumerate(head)}
        iC = ix["CNAE 2.0 Subclasse - Codigo"]; iV = ix["Qtd Vínculos Ativos"]; iU = ix["UF - Código"]; iM = ix["Município - Código"]; iN = ix["Ind RAIS Negativa - Código"]
        for row in rd:
            n += 1
            uf = UF.get(row[iU].strip(), "")
            v = int(row[iV] or 0)
            if uf == "SC":
                total_sc[0] += 1 if v > 0 else 0
                total_sc[1] += v
            c = row[iC].strip()
            if c not in CNAE:
                continue
            a = uf_cnae[(uf, c)]
            a[0] += 1 if v > 0 else 0; a[1] += v; a[2] += 1
            if uf == "SC":
                mun = row[iM].strip()
                b = mun_cnae[(mun, c)]
                b[0] += 1 if v > 0 else 0; b[1] += v; b[2] += 1
                e = econ_mar_sc_mun[mun]
                e[0] += 1 if v > 0 else 0; e[1] += v
    print(f"  {n:,} estabelecimentos lidos; SC: {total_sc[0]:,} estabelecimentos com vínculo, {total_sc[1]:,} vínculos ativos")
    with open(os.path.join(OUT, f"nautica_uf_{ano}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["ano", "uf", "cnae", "descricao", "grupo", "estab_com_vinculo", "vinculos_ativos", "estab_declarantes"])
        for (uf, c), a in sorted(uf_cnae.items()):
            w.writerow([ano, uf, c, CNAE[c][0], CNAE[c][1], a[0], a[1], a[2]])
    with open(os.path.join(OUT, f"nautica_municipio_sc_{ano}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["ano", "municipio_codigo", "municipio", "cnae", "descricao", "grupo", "estab_com_vinculo", "vinculos_ativos", "estab_declarantes"])
        for (mun, c), a in sorted(mun_cnae.items()):
            w.writerow([ano, mun, MUN.get(mun, mun), c, CNAE[c][0], CNAE[c][1], a[0], a[1], a[2]])
    # resumos
    def grupo(uf_filter=None):
        g = collections.defaultdict(lambda: [0, 0])
        for (uf, c), a in uf_cnae.items():
            if uf_filter and uf != uf_filter:
                continue
            g[CNAE[c][1]][0] += a[0]; g[CNAE[c][1]][1] += a[1]
        return {k: {"estab": v[0], "vinculos": v[1]} for k, v in g.items()}
    ind_uf = collections.defaultdict(lambda: [0, 0])
    for (uf, c), a in uf_cnae.items():
        if CNAE[c][1] == "Construção de embarcações" and uf:
            ind_uf[uf][0] += a[0]; ind_uf[uf][1] += a[1]
    grupos_uf = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for (uf, c), a in uf_cnae.items():
        if uf:
            grupos_uf[uf][CNAE[c][1]][0] += a[0]; grupos_uf[uf][CNAE[c][1]][1] += a[1]
    constr_uf = collections.defaultdict(lambda: [0, 0])
    for (uf, c), a in uf_cnae.items():
        if c in ("3012100",) and uf:
            constr_uf[uf][0] += a[0]; constr_uf[uf][1] += a[1]
    mun_ind = collections.defaultdict(lambda: [0, 0])
    for (mun, c), a in mun_cnae.items():
        if CNAE[c][1] == "Construção de embarcações":
            mun_ind[mun][0] += a[0]; mun_ind[mun][1] += a[1]
    mun_all = {MUN.get(m, m): {"estab": v[0], "vinculos": v[1]} for m, v in sorted(econ_mar_sc_mun.items(), key=lambda x: -x[1][1])[:25]}
    sc_cnae = {c: {"desc": CNAE[c][0], "grupo": CNAE[c][1], "estab": a[0], "vinculos": a[1]} for (uf, c), a in uf_cnae.items() if uf == "SC"}
    return {
        "ano": ano, "total_sc": {"estab_com_vinculo": total_sc[0], "vinculos_ativos": total_sc[1]},
        "grupos_br": grupo(), "grupos_sc": grupo("SC"),
        "construcao_por_uf": {u: {"estab": v[0], "vinculos": v[1]} for u, v in sorted(ind_uf.items(), key=lambda x: -x[1][1])},
        "grupos_por_uf": {u: {g: {"estab": v[0], "vinculos": v[1]} for g, v in gg.items()} for u, gg in grupos_uf.items()},
        "construcao_esporte_lazer_por_uf": {u: {"estab": v[0], "vinculos": v[1]} for u, v in sorted(constr_uf.items(), key=lambda x: -x[1][1])},
        "construcao_sc_por_municipio": {MUN.get(m, m): {"estab": v[0], "vinculos": v[1]} for m, v in sorted(mun_ind.items(), key=lambda x: -x[1][1])[:20]},
        "cadeia_sc_por_municipio": mun_all,
        "sc_por_cnae": sc_cnae,
    }


if __name__ == "__main__":
    res = {"fonte": "RAIS, microdados públicos por estabelecimento (PDET/MTE), extração ACATMAR", "definicao": {c: {"descricao": d, "grupo": g} for c, (d, g) in CNAE.items()}, "anos": {}}
    for arg in sys.argv[1:]:
        ano, caminho = arg.split("=", 1)
        res["anos"][ano] = processa(ano, caminho)
    json.dump(res, open(os.path.join(OUT, "resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for ano, r in res["anos"].items():
        print(f"\n== {ano} ==")
        print("  SC por grupo:", json.dumps(r["grupos_sc"], ensure_ascii=False))
        print("  Construção de embarcações por UF (vínculos):", [(u, v["vinculos"], v["estab"]) for u, v in list(r["construcao_por_uf"].items())[:8]])
        print("  Construção esporte e lazer (3012100) por UF:", [(u, v["vinculos"], v["estab"]) for u, v in list(r["construcao_esporte_lazer_por_uf"].items())[:8]])
        print("  Indústria náutica SC por município:", [(m, v["vinculos"], v["estab"]) for m, v in list(r["construcao_sc_por_municipio"].items())[:8]])
