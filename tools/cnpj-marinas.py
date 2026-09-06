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



pasta = sys.argv[1] if len(sys.argv) > 1 else "2026-08"
OUTC = os.path.join(ROOT, "data", "censo"); os.makedirs(OUTC, exist_ok=True)
arquivos = listar(pasta + "/")
mun = {}
for row in linhas_zip(baixar(f"{pasta}/Municipios.zip", os.path.join(TMP, f"{pasta}-Municipios.zip"))):
    mun[row[0]] = row[1]
cnae_nome = {}
for row in linhas_zip(baixar(f"{pasta}/Cnaes.zip", os.path.join(TMP, f"{pasta}-Cnaes.zip"))):
    cnae_nome[row[0]] = row[1]
PAT = re.compile(r"\bMARINA\b|GARAGEM NAUTICA|GARAGENS NAUTICAS|IATE CLUBE|YACHT CLUB|CLUBE NAUTICO|CLUBE DE VELA|VELA CLUBE|PORTO ESPORTIVO|ESTACIONAMENTO NAUTICO|GUARDA DE EMBARCAC|GUARDERIA|PIER|TRAPICHE", re.I)
sel = []; n = 0
for a in sorted(x for x in arquivos if x.startswith("Estabelecimentos")):
    print("Lendo", a, flush=True)
    p = baixar(f"{pasta}/{a}", os.path.join(TMP, f"{pasta}-{a}"))
    for row in linhas_zip(p):
        n += 1
        if row[19] != "SC" or row[5] != "02":
            continue
        nome = row[4]
        if not PAT.search(nome):
            continue
        sel.append({"cnpj": row[0] + row[1] + row[2], "cnpj_basico": row[0], "nome_fantasia": nome, "cnae_principal": row[11], "cnae_nome": cnae_nome.get(row[11], ""), "cnae_secundaria": row[12], "municipio": mun.get(row[20], row[20]), "bairro": row[17], "data_inicio": row[10], "matriz_filial": "matriz" if row[3] == "1" else "filial"})
    os.remove(p)
    print(f"   {n:,} lidos, {len(sel):,} candidatos em SC", flush=True)
basicos = {s["cnpj_basico"] for s in sel}
rz = {}
for a in sorted(x for x in arquivos if x.startswith("Empresas")):
    print("Lendo", a, flush=True)
    p = baixar(f"{pasta}/{a}", os.path.join(TMP, f"{pasta}-{a}"))
    for row in linhas_zip(p):
        if row[0] in basicos:
            rz[row[0]] = (row[1], row[5])
        # razao social tambem pode conter o termo, mas so temos os selecionados pelo nome fantasia
    os.remove(p)
PORTE = {"00": "Nao informado", "01": "Microempresa", "03": "Empresa de pequeno porte", "05": "Demais"}
with open(os.path.join(OUTC, "marinas-sc-candidatos.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["validar (S/N)", "tipo provavel", "nome_fantasia", "razao_social", "municipio", "bairro", "porte", "desde", "cnae_principal", "cnae_nome", "matriz_filial", "cnpj", "observacao"])
    for s in sorted(sel, key=lambda s: (s["municipio"], s["nome_fantasia"])):
        r, pt = rz.get(s["cnpj_basico"], ("", ""))
        nm = s["nome_fantasia"].upper()
        tipo = "iate clube / clube" if re.search(r"CLUBE|YACHT CLUB|VELA", nm) else "garagem nautica" if "GARAGE" in nm or "GUARD" in nm or "ESTACIONAMENTO" in nm else "marina" if "MARINA" in nm else "pier / trapiche / porto"
        w.writerow(["", tipo, s["nome_fantasia"], r, s["municipio"].title(), s["bairro"].title(), PORTE.get(pt, pt), s["data_inicio"][:4], s["cnae_principal"], s["cnae_nome"], s["matriz_filial"], s["cnpj"], ""])
print("pronto:", len(sel), "candidatos ->", os.path.join(OUTC, "marinas-sc-candidatos.csv"))
