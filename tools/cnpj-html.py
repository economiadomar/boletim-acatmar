#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injeta data/cnpj/resumo.json em numeros.html entre marcadores <!-- cnpj:X --> (sc, br, nota)."""
import json, re, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'numeros.html')
R = json.load(open(os.path.join(ROOT, 'data', 'cnpj', 'resumo.json'), encoding='utf-8'))
t = open(P, encoding='utf-8').read()
MESES = {'01': 'janeiro', '02': 'fevereiro', '03': 'março', '04': 'abril', '05': 'maio', '06': 'junho', '07': 'julho', '08': 'agosto', '09': 'setembro', '10': 'outubro', '11': 'novembro', '12': 'dezembro'}
MESES_EN = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
ano, mes = R['pasta'].split('-')
REF = f"{MESES[mes]} de {ano}"; REF_EN = f"{MESES_EN[mes]} {ano}"


def n(v):
    return f"{v:,}".replace(',', '.')


def put(key, html):
    global t
    t, k = re.subn(r'<!-- cnpj:%s -->.*?<!-- /cnpj:%s -->' % (key, key), '<!-- cnpj:%s -->%s<!-- /cnpj:%s -->' % (key, html, key), t, count=1, flags=re.S)
    print(f"  {key}: {k}")


core_total = R['sc_setor_nautico_total_principal']
porte = R['sc_setor_nautico_por_porte']
rows_cnae = ''
for c, d in R['sc_por_cnae'].items():
    if d['grupo'] in ('Indústria náutica', 'Comércio e serviços náuticos'):
        rows_cnae += f'      <tr><td>{c[:4]}-{c[4]}/{c[5:]}</td><td>{d["nome"]}</td><td class="v">{n(d["estabelecimentos_ativos"])}</td></tr>\n'
rows_mun = ''.join(f'      <tr><td>{m}</td><td class="v">{n(v)}</td></tr>\n' for m, v in list(R['sc_setor_nautico_por_municipio'].items())[:12])
rows_porte = ' · '.join(f'{k} {n(v)}' for k, v in sorted(porte.items(), key=lambda x: -x[1]))
html = (f'\n    <h3 data-en="Active nautical companies in Santa Catarina (Federal Revenue CNPJ registry, {REF_EN}, ACATMAR extraction)" style="margin-top:1.4rem">Empresas náuticas ativas em Santa Catarina (cadastro CNPJ da Receita Federal, {REF}, extração ACATMAR)</h3>\n'
        f'    <p class="lead" data-en="Establishments with active registration status whose main CNAE is one of the ten nautical industry, trade and services subclasses defined by ACATMAR. Read directly from the Federal Revenue open data. Includes companies without employees (MEI), which do not appear in RAIS.">Estabelecimentos com situação cadastral ativa cujo CNAE principal é uma das dez subclasses de indústria, comércio e serviços náuticos definidas pela ACATMAR. Lidos direto dos dados abertos da Receita Federal. Inclui empresas sem empregados (MEI), que não aparecem na RAIS.</p>\n'
        f'    <div class="tw"><table>\n      <tr><th>CNAE</th><th data-en="Activity">Atividade</th><th data-en="Active establishments">Estabelecimentos ativos</th></tr>\n{rows_cnae}'
        f'      <tr><td></td><td><b data-en="Total, nautical sector (main CNAE)">Total do setor náutico (CNAE principal)</b></td><td class="v"><b>{n(core_total)}</b></td></tr>\n'
        f'      <tr><td></td><td data-en="Plus: companies with a nautical CNAE as secondary activity">Além desses: empresas com CNAE náutico como atividade secundária</td><td class="v">{n(R["sc_com_cnae_nautico_secundario"])}</td></tr>\n    </table></div>\n'
        f'    <div class="src" data-en="Size: {rows_porte} · MEI: {n(R["sc_setor_nautico_mei"])}. Source: Federal Revenue, CNPJ open data, {REF_EN} release, ACATMAR extraction.">Porte: {rows_porte} · MEI: {n(R["sc_setor_nautico_mei"])}. Fonte: Receita Federal, dados abertos do CNPJ, divulgação de {REF}, extração ACATMAR.</div>\n'
        f'    <div class="tw" style="margin-top:1rem"><table>\n      <tr><th data-en="Municipality (SC)">Município (SC)</th><th data-en="Active nautical establishments">Estabelecimentos náuticos ativos</th></tr>\n{rows_mun}    </table></div>\n')
put('sc', html)
br = R['brasil_setor_nautico_principal_por_uf']
b3 = R['brasil_construcao_esporte_lazer_por_uf']
put('br', f'      <tr><td data-en="Active nautical companies by state (main CNAE, 10 subclasses)">Empresas náuticas ativas por estado (CNAE principal, 10 subclasses)</td><td class="v">' + ' · '.join(f'{u} {n(v)}' for u, v in list(br.items())[:4]) + f'</td><td data-en="' + ' · '.join(f'{u} {n(v)}' for u, v in list(br.items())[4:9]) + f' · Federal Revenue CNPJ registry, {REF_EN}, ACATMAR extraction">' + ' · '.join(f'{u} {n(v)}' for u, v in list(br.items())[4:9]) + f' · cadastro CNPJ da Receita Federal, {REF}, extração ACATMAR</td></tr>\n'
    f'      <tr><td data-en="Active sport and leisure boatbuilders (CNAE 3012-1/00), by state">Construtores ativos de embarcações de esporte e lazer (CNAE 3012-1/00), por estado</td><td class="v">' + ' · '.join(f'{u} {n(v)}' for u, v in list(b3.items())[:4]) + f'</td><td data-en="' + ' · '.join(f'{u} {n(v)}' for u, v in list(b3.items())[4:9]) + f' · Federal Revenue, {REF_EN}">' + ' · '.join(f'{u} {n(v)}' for u, v in list(b3.items())[4:9]) + f' · Receita Federal, {REF}</td></tr>\n')
put('nota', f'<b>Empresas na Receita Federal.</b> A contagem de empresas náuticas usa os dados abertos do CNPJ (divulgação de {REF}), estabelecimentos com situação cadastral ativa e CNAE principal em uma das dez subclasses náuticas da definição ACATMAR. Inclui MEI e empresas sem empregados, por isso é maior que a RAIS; difere das contagens do Sebrae (1.028 e 1.292) por usar outra data e outro conjunto de CNAEs, explicitado na página. Marinas e garagens náuticas não têm CNAE próprio (muitas se registram como administração imobiliária ou recreação) e só podem ser contadas pela Capitania dos Portos e pelas prefeituras. ')
for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
    json.loads(x)
open(P, 'w', encoding='utf-8').write(t)
print('ok', REF, 'SC setor nautico', core_total)
