#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator ACATMAR do Cadastro Nacional da Pessoa Jurídica (dados abertos da Receita Federal).

Baixa os arquivos mensais pelo compartilhamento público (WebDAV/Nextcloud do SERPRO), filtra em fluxo
(sem gravar a base inteira) e guarda só o que interessa:
  - estabelecimentos ativos no Brasil cujo CNAE principal ou secundário está na lista náutica e naval
  - todos os estabelecimentos ativos de Santa Catarina com CNAE principal na lista
  - porte (Empresas) e opção pelo MEI (Simples) das empresas filtradas
Saída em data/cnpj/: estabelecimentos_nautica.csv, resumo.json
Uso: python3 tools/cnpj.py [AAAA-MM]   (padrão: pasta mais recente)
"""
import csv, io, json, os, sys, time, zipfile, urllib.request, base64, collections, re, datetime

TOKEN = "YggdBLfdninEJX9"   # compartilhamento publico oficial da Receita (SERPRO+)
BASE = "https://arquivos.receitafederal.gov.br/public.php/webdav/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "cnpj")
TMP = os.path.join(os.environ.get("TMPDIR", "/tmp"), "acatmar-cnpj")
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
AUTH = "Basic " + base64.b64encode((TOKEN + ":").encode()).decode()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rais import CNAE  # mesma definicao de cadeia nautica e naval
CORE = {c for c, (d, g) in CNAE.items() if g in ("Indústria náutica", "Comércio e serviços náuticos")}
TODOS = set(CNAE)


def req(path, method="GET", headers=None, rng=None):
    h = {"Authorization": AUTH, "User-Agent": "ACATMAR-numeros/1.0"}
    if headers:
        h.update(headers)
    if rng:
        h["Range"] = f"bytes={rng[0]}-{rng[1]}"
    r = urllib.request.Request(BASE + path, method=method, headers=h)
    return urllib.request.urlopen(r, timeout=300)


def listar(pasta=""):
    with req(pasta, "PROPFIND", {"Depth": "1"}) as r:
        x = r.read().decode()
    itens = re.findall(r"<d:href>([^<]*)</d:href>", x)
    return [i.rstrip("/").split("/")[-1] for i in itens[1:]]


def baixar(nome, destino):
    if os.path.exists(destino):
        return destino
    tmp = destino + ".part"
    for tent in range(5):
        try:
            with req(nome) as r, open(tmp, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            os.rename(tmp, destino)
            return destino
        except Exception as e:
            print("   falha", nome, e, "tentando de novo")
            time.sleep(10 * (tent + 1))
    raise RuntimeError("nao baixou " + nome)


def linhas_zip(caminho):
    with zipfile.ZipFile(caminho) as z:
        for n in z.namelist():
            with z.open(n) as f:
                for row in csv.reader((l.replace("\x00", "") for l in io.TextIOWrapper(f, encoding="latin-1", newline="")), delimiter=";"):
                    yield row


pasta = sys.argv[1] if len(sys.argv) > 1 else sorted(p for p in listar() if re.match(r"\d{4}-\d{2}$", p))[-1]
print("Pasta:", pasta)
arquivos = listar(pasta + "/")
print("Arquivos:", arquivos)

# tabelas auxiliares
mun = {}
for row in linhas_zip(baixar(f"{pasta}/Municipios.zip", os.path.join(TMP, f"{pasta}-Municipios.zip"))):
    mun[row[0]] = row[1]
cnae_nome = {}
for row in linhas_zip(baixar(f"{pasta}/Cnaes.zip", os.path.join(TMP, f"{pasta}-Cnaes.zip"))):
    cnae_nome[row[0]] = row[1]

# estabelecimentos
sel = []
n = 0
for a in sorted(x for x in arquivos if x.startswith("Estabelecimentos")):
    print("Lendo", a)
    p = baixar(f"{pasta}/{a}", os.path.join(TMP, f"{pasta}-{a}"))
    for row in linhas_zip(p):
        n += 1
        if row[5] != "02":          # situacao cadastral: 02 = ativa
            continue
        uf = row[19]; cp = row[11]; cs = row[12]
        sec = set(cs.split(",")) if cs else set()
        principal_lista = cp in TODOS
        if not (principal_lista or (sec & CORE)):
            continue
        sel.append({"cnpj_basico": row[0], "cnpj_ordem": row[1], "cnpj_dv": row[2], "matriz_filial": row[3], "nome_fantasia": row[4],
                    "data_inicio": row[10], "cnae_principal": cp, "cnae_secundaria": cs, "uf": uf, "municipio_codigo": row[20],
                    "municipio": mun.get(row[20], row[20]), "bairro": row[17], "cep": row[18], "email": ""})
    os.remove(p)
    print(f"   {n:,} lidos, {len(sel):,} selecionados")

# porte e MEI
basicos = {s["cnpj_basico"] for s in sel}
porte = {}
for a in sorted(x for x in arquivos if x.startswith("Empresas")):
    print("Lendo", a)
    p = baixar(f"{pasta}/{a}", os.path.join(TMP, f"{pasta}-{a}"))
    for row in linhas_zip(p):
        if row[0] in basicos:
            porte[row[0]] = (row[1], row[5], row[4])   # razao social, porte, capital
    os.remove(p)
mei = {}
if "Simples.zip" in arquivos:
    print("Lendo Simples.zip")
    p = baixar(f"{pasta}/Simples.zip", os.path.join(TMP, f"{pasta}-Simples.zip"))
    for row in linhas_zip(p):
        if row[0] in basicos:
            mei[row[0]] = (row[1], row[4])   # opcao simples, opcao mei
    os.remove(p)
PORTE = {"00": "Não informado", "01": "Microempresa", "03": "Empresa de pequeno porte", "05": "Demais"}
with open(os.path.join(OUT, "estabelecimentos_nautica.csv"), "w", newline="", encoding="utf-8") as f:
    cols = ["cnpj", "matriz_filial", "razao_social", "nome_fantasia", "porte", "mei", "simples", "capital_social", "data_inicio", "cnae_principal", "cnae_principal_nome", "cnae_secundaria", "uf", "municipio_codigo", "municipio", "bairro", "cep"]
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for s in sel:
        rz, pt, cap = porte.get(s["cnpj_basico"], ("", "", ""))
        sm, me = mei.get(s["cnpj_basico"], ("", ""))
        w.writerow({"cnpj": s["cnpj_basico"] + s["cnpj_ordem"] + s["cnpj_dv"], "matriz_filial": s["matriz_filial"], "razao_social": rz, "nome_fantasia": s["nome_fantasia"],
                    "porte": PORTE.get(pt, pt), "mei": me, "simples": sm, "capital_social": cap, "data_inicio": s["data_inicio"], "cnae_principal": s["cnae_principal"],
                    "cnae_principal_nome": cnae_nome.get(s["cnae_principal"], ""), "cnae_secundaria": s["cnae_secundaria"], "uf": s["uf"], "municipio_codigo": s["municipio_codigo"],
                    "municipio": s["municipio"], "bairro": s["bairro"], "cep": s["cep"]})

# resumo
def conta(filtro):
    return sum(1 for s in sel if filtro(s))
res = {"pasta": pasta, "gerado_em": datetime.date.today().isoformat(), "fonte": "Receita Federal, dados abertos do CNPJ (estabelecimentos ativos), extração ACATMAR",
       "definicao": {c: {"descricao": d, "grupo": g} for c, (d, g) in CNAE.items()}}
por_uf_core = collections.Counter(s["uf"] for s in sel if s["cnae_principal"] in CORE)
por_uf_3012 = collections.Counter(s["uf"] for s in sel if s["cnae_principal"] == "3012100")
sc = [s for s in sel if s["uf"] == "SC"]
por_cnae_sc = collections.Counter(s["cnae_principal"] for s in sc if s["cnae_principal"] in TODOS)
por_mun_sc_core = collections.Counter(s["municipio"] for s in sc if s["cnae_principal"] in CORE)
por_porte_sc_core = collections.Counter(PORTE.get(porte.get(s["cnpj_basico"], ("", "", ""))[1], "?") for s in sc if s["cnae_principal"] in CORE)
mei_sc_core = sum(1 for s in sc if s["cnae_principal"] in CORE and mei.get(s["cnpj_basico"], ("", ""))[1] == "S")
sec_sc = sum(1 for s in sc if s["cnae_principal"] not in CORE and (set(s["cnae_secundaria"].split(",")) & CORE))
res.update({
    "brasil_setor_nautico_principal_por_uf": dict(por_uf_core.most_common()),
    "brasil_construcao_esporte_lazer_por_uf": dict(por_uf_3012.most_common()),
    "sc_por_cnae": {c: {"nome": CNAE[c][0], "grupo": CNAE[c][1], "estabelecimentos_ativos": v} for c, v in por_cnae_sc.most_common()},
    "sc_setor_nautico_por_municipio": dict(por_mun_sc_core.most_common(30)),
    "sc_setor_nautico_por_porte": dict(por_porte_sc_core), "sc_setor_nautico_mei": mei_sc_core,
    "sc_setor_nautico_total_principal": sum(por_cnae_sc[c] for c in CORE), "sc_com_cnae_nautico_secundario": sec_sc,
})
json.dump(res, open(os.path.join(OUT, "resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ["brasil_construcao_esporte_lazer_por_uf", "sc_setor_nautico_total_principal", "sc_setor_nautico_por_porte", "sc_setor_nautico_mei", "sc_com_cnae_nautico_secundario"]}, ensure_ascii=False))
print("SC por município (setor náutico, CNAE principal):", list(por_mun_sc_core.most_common(12)))
print("Brasil setor náutico por UF:", por_uf_core.most_common(10))
