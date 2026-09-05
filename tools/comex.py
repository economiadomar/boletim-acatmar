#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator ACATMAR de comércio exterior (Comex Stat / MDIC, API pública).

Produz, em data/comex/:
  - embarcacoes_uf.csv        exportações e importações da posição 8903 por UF e ano (US$ FOB, kg, unidades)
  - embarcacoes_ncm.csv       por NCM (8 dígitos), Brasil e SC, por ano
  - embarcacoes_pais.csv      por país de destino/origem, Brasil e SC, por ano
  - embarcacoes_municipio.csv por município (todo o Brasil), por ano
  - embarcacoes_mensal.csv    por UF e mês, dois últimos anos (para comparação de semestres)
  - pescado_uf.csv            capítulo 03 + posições 1604 e 1605, por UF e ano
  - pescado_municipio_sc.csv  idem, municípios de SC
  - pescado_pais_sc.csv       idem, países, SC
  - resumo.json               indicadores prontos para a página
Uso: python3 tools/comex.py [ano_inicial]  (padrão 2010)
"""
import csv, json, os, sys, time, datetime, urllib.request, urllib.error

BASE = "https://api-comexstat.mdic.gov.br"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "comex")
os.makedirs(OUT, exist_ok=True)
Y0 = int(sys.argv[1]) if len(sys.argv) > 1 else 2010
HOJE = datetime.date.today()
Y1 = HOJE.year
BOATS = [{"filter": "heading", "values": ["8903"]}]
FISH = [{"filter": "chapter", "values": ["03"]}]          # peixes, crustáceos e moluscos
FISH_PREP = [{"filter": "heading", "values": ["1604", "1605"]}]  # preparações e conservas


CACHE = os.path.join(OUT, ".cache")
os.makedirs(CACHE, exist_ok=True)


def post(path, body, tries=6):
    import hashlib
    key = hashlib.md5((path + json.dumps(body, sort_keys=True)).encode()).hexdigest()
    cf = os.path.join(CACHE, key + ".json")
    if os.path.exists(cf) and (HOJE - datetime.date.fromtimestamp(os.path.getmtime(cf))).days < 1:
        return json.load(open(cf, encoding="utf-8"))
    data = json.dumps(body).encode()
    for i in range(tries):
        try:
            req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json", "User-Agent": "ACATMAR-numeros/1.0"})
            with urllib.request.urlopen(req, timeout=180) as r:
                j = json.loads(r.read().decode())
            if j.get("success") is False:
                raise RuntimeError(j.get("message"))
            lst = j["data"]["list"]
            json.dump(lst, open(cf, "w", encoding="utf-8"), ensure_ascii=False)
            time.sleep(1.5)
            return lst
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"   429: aguardando {60 * (i + 1)} s")
                time.sleep(60 * (i + 1))
                continue
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))
    raise RuntimeError("API indisponivel: " + path)


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "ACATMAR-numeros/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())["data"]


UF = {x["uf"]: x["id"] for x in get("/tables/uf")}
UF_NOME = {x["text"]: x["uf"] for x in get("/tables/uf")}
NAO_UF = {"MN", "ND", "EX", "RE", "ZN", "CB", "ED"}  # codigos que nao sao estados
SC = UF["SC"]


def q(flow, filters, details, years=(Y0, Y1), monthly=False, metrics=None, path="/general"):
    # metricStatistic (quantidade) so e aceita com detalhamento por NCM
    if metrics is None:
        metrics = ("metricFOB", "metricKG", "metricStatistic") if "ncm" in details else ("metricFOB", "metricKG")
    # um unico pedido para a serie inteira (a API devolve uma linha por ano); mensal em blocos de um ano
    blocos = [(y, y) for y in range(years[0], years[1] + 1)] if monthly else [years]
    rows = []
    for a, b in blocos:
        body = {"flow": flow, "monthDetail": monthly, "period": {"from": f"{a}-01", "to": f"{b}-12"},
                "filters": filters, "details": list(details), "metrics": list(metrics)}
        for r in post(path, body):
            r["flow"] = flow
            rows.append(r)
    return rows


def num(v):
    try:
        return int(float(v))
    except Exception:
        return 0


def save(name, rows, cols):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"  {name}: {len(rows)} linhas")


def by_year(rows, key=None, val="metricFOB"):
    d = {}
    for r in rows:
        k = (int(r["year"]),) + ((r.get(key),) if key else ())
        d[k] = d.get(k, 0) + num(r.get(val))
    return d


print("1/8 embarcações (8903) por UF e ano")
uf_rows = q("export", BOATS, ["state"]) + q("import", BOATS, ["state"])
for r in uf_rows:
    r["uf"] = UF_NOME.get(r["state"], "")
save("embarcacoes_uf.csv", uf_rows, ["flow", "year", "state", "uf", "metricFOB", "metricKG", "metricStatistic"])

print("2/8 embarcações por NCM, Brasil e SC")
ncm_rows = []
for f, tag in ((BOATS, "BR"), (BOATS + [{"filter": "state", "values": [SC]}], "SC")):
    for r in q("export", f, ["ncm"]) + q("import", f, ["ncm"]):
        r["recorte"] = tag
        ncm_rows.append(r)
save("embarcacoes_ncm.csv", ncm_rows, ["recorte", "flow", "year", "coNcm", "ncm", "metricFOB", "metricKG", "metricStatistic"])

print("3/8 embarcações por país, Brasil e SC")
pais_rows = []
for f, tag in ((BOATS, "BR"), (BOATS + [{"filter": "state", "values": [SC]}], "SC")):
    for r in q("export", f, ["country", "ncm"]) + q("import", f, ["country", "ncm"]):
        r["recorte"] = tag
        pais_rows.append(r)
save("embarcacoes_pais.csv", pais_rows, ["recorte", "flow", "year", "country", "metricFOB", "metricKG", "metricStatistic"])

print("4/8 embarcações por município (Brasil)")
mun_rows = q("export", BOATS, ["city"], metrics=("metricFOB", "metricKG"), path="/cities") + q("import", BOATS, ["city"], metrics=("metricFOB", "metricKG"), path="/cities")
for r in mun_rows:
    nome = r.get("noMunMinsgUf", "")
    r["municipio"], r["uf"] = (nome.rsplit(" - ", 1) + [""])[:2]
save("embarcacoes_municipio.csv", mun_rows, ["flow", "year", "municipio", "uf", "metricFOB", "metricKG"])

print("5/8 embarcações mensal por UF (dois últimos anos)")
mes_rows = q("export", BOATS, ["state"], years=(Y1 - 1, Y1), monthly=True) + q("import", BOATS, ["state"], years=(Y1 - 1, Y1), monthly=True)
for r in mes_rows:
    r["uf"] = UF_NOME.get(r["state"], "")
save("embarcacoes_mensal.csv", mes_rows, ["flow", "year", "monthNumber", "state", "uf", "metricFOB", "metricKG", "metricStatistic"])
mes_mun = q("export", BOATS, ["city"], years=(Y1 - 1, Y1), monthly=True, metrics=("metricFOB", "metricKG"), path="/cities")
for r in mes_mun:
    nome = r.get("noMunMinsgUf", "")
    r["municipio"], r["uf"] = (nome.rsplit(" - ", 1) + [""])[:2]
save("embarcacoes_mensal_municipio.csv", mes_mun, ["flow", "year", "monthNumber", "municipio", "uf", "metricFOB", "metricKG"])

print("6/8 pescado por UF e ano")
fish_rows = []
for f, tag in ((FISH, "cap03"), (FISH_PREP, "1604-1605")):
    for r in q("export", f, ["state"], metrics=("metricFOB", "metricKG")) + q("import", f, ["state"], metrics=("metricFOB", "metricKG")):
        r["grupo"] = tag
        r["uf"] = UF_NOME.get(r["state"], "")
        fish_rows.append(r)
save("pescado_uf.csv", fish_rows, ["grupo", "flow", "year", "state", "uf", "metricFOB", "metricKG"])

print("7/8 pescado por município e país, SC")
fsc = []
for f, tag in ((FISH + [{"filter": "state", "values": [SC]}], "cap03"), (FISH_PREP + [{"filter": "state", "values": [SC]}], "1604-1605")):
    for r in q("export", f, ["city"], metrics=("metricFOB", "metricKG"), path="/cities") + q("import", f, ["city"], metrics=("metricFOB", "metricKG"), path="/cities"):
        nome = r.get("noMunMinsgUf", "")
        r["municipio"], r["uf"] = (nome.rsplit(" - ", 1) + [""])[:2]
        r["grupo"] = tag
        fsc.append(r)
save("pescado_municipio_sc.csv", fsc, ["grupo", "flow", "year", "municipio", "uf", "metricFOB", "metricKG"])
fpais = []
for f, tag in ((FISH + [{"filter": "state", "values": [SC]}], "cap03"), (FISH_PREP + [{"filter": "state", "values": [SC]}], "1604-1605")):
    for r in q("export", f, ["country"], metrics=("metricFOB", "metricKG")) + q("import", f, ["country"], metrics=("metricFOB", "metricKG")):
        r["grupo"] = tag
        fpais.append(r)
save("pescado_pais_sc.csv", fpais, ["grupo", "flow", "year", "country", "metricFOB", "metricKG"])

print("8/8 resumo")
exp_uf = by_year([r for r in uf_rows if r["flow"] == "export"], "uf")
imp_uf = by_year([r for r in uf_rows if r["flow"] == "import"], "uf")
serie = []
for y in range(Y0, Y1 + 1):
    br = sum(v for (yy, u), v in exp_uf.items() if yy == y)
    sc = exp_uf.get((y, "SC"), 0)
    ibr = sum(v for (yy, u), v in imp_uf.items() if yy == y)
    isc = imp_uf.get((y, "SC"), 0)
    rank = sorted([(v, u) for (yy, u), v in exp_uf.items() if yy == y and u and u not in NAO_UF], reverse=True)[:6]
    serie.append({"ano": y, "exp_sc": sc, "exp_br": br, "part_sc": round(100 * sc / br, 1) if br else None,
                  "imp_sc": isc, "imp_br": ibr, "part_imp_sc": round(100 * isc / ibr, 1) if ibr else None,
                  "ranking_exp": [{"uf": u, "fob": v} for v, u in rank]})
mun_exp = by_year([r for r in mun_rows if r["flow"] == "export"], "noMunMinsgUf")
mun_por_ano = {}
for (y, m), v in mun_exp.items():
    mun_por_ano.setdefault(y, []).append((v, m))
mun_top = {y: [{"municipio": m, "fob": v} for v, m in sorted(l, reverse=True)[:10]] for y, l in mun_por_ano.items()}
mun_sc = {y: [{"municipio": m, "fob": v} for v, m in sorted(l, reverse=True) if m.endswith("- SC")][:10] for y, l in mun_por_ano.items()}
ncm_sc = {}
for r in ncm_rows:
    if r["recorte"] == "SC" and r["flow"] == "export":
        ncm_sc.setdefault(int(r["year"]), []).append({"ncm": r["coNcm"], "desc": r["ncm"], "fob": num(r["metricFOB"]), "kg": num(r["metricKG"]), "unidades": num(r["metricStatistic"])})
pais_sc = {}
agg = {}
for r in pais_rows:
    if r["recorte"] == "SC" and r["flow"] == "export":
        k = (int(r["year"]), r["country"])
        a = agg.setdefault(k, {"fob": 0, "unidades": 0})
        a["fob"] += num(r["metricFOB"]); a["unidades"] += num(r.get("metricStatistic"))
for (y, c), a in agg.items():
    pais_sc.setdefault(y, []).append({"pais": c, "fob": a["fob"], "unidades": a["unidades"]})
for y in pais_sc:
    pais_sc[y] = sorted(pais_sc[y], key=lambda x: -x["fob"])[:10]
# semestres
def semestre(rows, y, uf=None, mun=None, meses=range(1, 7)):
    s = 0
    for r in rows:
        if r["flow"] != "export" or int(r["year"]) != y or int(r["monthNumber"]) not in meses:
            continue
        if uf is not None and r.get("uf") != uf:
            continue
        if mun is not None and r.get("noMunMinsgUf") != mun:
            continue
        s += num(r["metricFOB"])
    return s
ult_mes = max((int(r["monthNumber"]) for r in mes_rows if int(r["year"]) == Y1), default=0)
sem = {"ano": Y1, "ate_mes": ult_mes,
       "h1": {"br": [semestre(mes_rows, Y1 - 1), semestre(mes_rows, Y1)], "sc": [semestre(mes_rows, Y1 - 1, "SC"), semestre(mes_rows, Y1, "SC")],
              "itajai": [semestre(mes_mun, Y1 - 1, mun="Itajaí - SC"), semestre(mes_mun, Y1, mun="Itajaí - SC")],
              "palhoca": [semestre(mes_mun, Y1 - 1, mun="Palhoça - SC"), semestre(mes_mun, Y1, mun="Palhoça - SC")]},
       "acumulado_ate_mes": {"br": [semestre(mes_rows, Y1 - 1, meses=range(1, ult_mes + 1)), semestre(mes_rows, Y1, meses=range(1, ult_mes + 1))],
                             "sc": [semestre(mes_rows, Y1 - 1, "SC", meses=range(1, ult_mes + 1)), semestre(mes_rows, Y1, "SC", meses=range(1, ult_mes + 1))]}}
fish_exp = by_year([r for r in fish_rows if r["flow"] == "export"], "uf")
fish_imp = by_year([r for r in fish_rows if r["flow"] == "import"], "uf")
pesca = []
for y in range(Y0, Y1 + 1):
    br = sum(v for (yy, u), v in fish_exp.items() if yy == y)
    sc = fish_exp.get((y, "SC"), 0)
    rank = sorted([(v, u) for (yy, u), v in fish_exp.items() if yy == y and u and u not in NAO_UF], reverse=True)[:5]
    pesca.append({"ano": y, "exp_sc": sc, "exp_br": br, "part_sc": round(100 * sc / br, 1) if br else None,
                  "imp_sc": fish_imp.get((y, "SC"), 0), "imp_br": sum(v for (yy, u), v in fish_imp.items() if yy == y),
                  "ranking_exp": [{"uf": u, "fob": v} for v, u in rank]})
fmun = by_year([r for r in fsc if r["flow"] == "export"], "noMunMinsgUf")
pesca_mun = {}
for (y, m), v in fmun.items():
    pesca_mun.setdefault(y, []).append({"municipio": m, "fob": v})
for y in pesca_mun:
    pesca_mun[y] = sorted(pesca_mun[y], key=lambda x: -x["fob"])[:8]
resumo = {"gerado_em": HOJE.isoformat(), "fonte": "Comex Stat / MDIC, API pública (api-comexstat.mdic.gov.br), extração ACATMAR",
          "embarcacoes_8903": {"serie_anual": serie, "municipios_top_brasil": mun_top, "municipios_sc": mun_sc, "ncm_sc": ncm_sc, "paises_sc": pais_sc, "semestre": sem},
          "pescado_cap03_1604_1605": {"serie_anual": pesca, "municipios_sc": pesca_mun}}
with open(os.path.join(OUT, "resumo.json"), "w", encoding="utf-8") as f:
    json.dump(resumo, f, ensure_ascii=False, indent=1)
print("\n== Embarcações (8903): exportações, US$ FOB ==")
for s in serie:
    print(f"  {s['ano']}: SC {s['exp_sc']:>12,} | BR {s['exp_br']:>12,} | SC {s['part_sc']}% | ranking {[(r['uf'], r['fob']) for r in s['ranking_exp'][:3]]}")
print("\n== SC por NCM, último ano completo ==")
for x in sorted(ncm_sc.get(Y1 - 1, []), key=lambda x: -x["fob"]):
    print(f"  {x['ncm']} {x['fob']:>12,} US$ | {x['unidades']:>4} un | {x['desc'][:70]}")
print("\n== Semestres ==", json.dumps(sem, ensure_ascii=False))
print("\n== Pescado, últimos anos ==")
for s in pesca[-4:]:
    print(f"  {s['ano']}: SC {s['exp_sc']:>12,} | BR {s['exp_br']:>12,} | {s['part_sc']}% | imp SC {s['imp_sc']:,}")
