#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove rodapés de fonte e menções a extração do corpo de numeros.html. As fontes ficam só na seção Fontes.
Idempotente: rodar sempre depois dos geradores (comex-html, rais-html, cnpj-html, uf-html)."""
import re, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'numeros.html')
t = open(P, encoding='utf-8').read()
a = t.index('<main'); b = t.index('id="fontes"')
body = t[a:b]
n = {}
body, n['src'] = re.subn(r'\s*<div class="src"[^>]*>.*?</div>', '', body, flags=re.S)
# parenteses de fonte em titulos h2/h3 e em celulas
FONTE = r'(?:RAIS|Comex Stat|MDIC|DPC|Marinha|Receita Federal|Federal Revenue|SEPLAN|Sebrae|Capitania|Port Authority|Navy|extração|extraction|ACATMAR extraction|compilação|compiled|arquivo de|file of|cadastro CNPJ|CNPJ registry|Observatório|FIESC|SINDIPI|Antaq|Firjan|Semar|IBGE|Epagri|PIA)'
body, n['parenteses'] = re.subn(r' \((?:[^()]*' + FONTE + r'[^()]*)\)', '', body)
body, n['extracao'] = re.subn(r'\s*(?:Extração ACATMAR|ACATMAR extraction)\.?', '', body)
body, n['sep'] = re.subn(r' · (?:extração ACATMAR|ACATMAR extraction)', '', body)
body, n['cell'] = re.subn(r' · (?:RAIS \d{4}|Receita Federal, fev/2025|Receita Federal, \d{2}/\d{2}/\d{4}|Comex Stat/MDIC|Sebrae/SC e ACATMAR, Foresight 2025|Sebrae/SC and ACATMAR, Foresight 2025|Federal Revenue, Feb 2025|Federal Revenue, Jul 31, 2024|Receita Federal, 31/07/2024|Federal Revenue, Dec 2025|Receita Federal, dez/2025)(?:, compilação Sebrae/SC|, compiled by Sebrae/SC|, extração ACATMAR|, ACATMAR extraction)?', '', body)
body, n['lead_rais'] = re.subn(r' Lidos direto dos microdados públicos da RAIS, do Ministério do Trabalho\.| Read directly from the public RAIS microdata of the Ministry of Labor\.', '', body)
body, n['lead_cnpj'] = re.subn(r' Lidos direto dos dados abertos da Receita Federal\.| Read directly from the Federal Revenue open data\.', '', body)
body, n['lead_uf'] = re.subn(r' Lanchas: registro da Marinha \(set/2024\)\. Empregos e construtores: RAIS \d{4}\. Empresas: Receita Federal\. Exportações: Comex Stat \d{4}\. Tudo lido pela ACATMAR direto das fontes primárias\.| Motorboats: Navy registry \(Sept 2024\)\. Jobs and boatbuilders: RAIS \d{4}\. Companies: Federal Revenue\. Exports: Comex Stat \d{4}\. All read by ACATMAR from the primary sources\.', '', body)
body, n['mini'] = re.subn(r'\s*<p class="mini"[^>]*>(?:Unidades são|Units are)[^<]*</p>', '', body)

# links para fora da plataforma (e chamadas "saiba mais") no corpo: some o botao; links externos comuns viram texto
def _link(m):
    href = m.group(1); inner = m.group(2)
    if href.startswith('#'):
        return m.group(0)
    if '&rarr;' in inner or '→' in inner or re.match(r'^\s*(Baixar|Download|PDF|planilha|tabelas|Saiba mais|Ver as notícias|Todas as edições|Guia completo|Informativo técnico|ALESC|SEF/SC|Senado Federal|Antaq|resumo|panrotas|Boletim estatístico|Ler a análise completa)', re.sub(r'<[^>]+>', '', inner), re.I):
        return ''
    return inner
body, n['links'] = re.subn(r'<a\b[^>]*?href="([^"]*)"[^>]*>(.*?)</a>', _link, body, flags=re.S)
t = t[:a] + body + t[b:]
for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, flags=re.S):
    json.loads(x)
open(P, 'w', encoding='utf-8').write(t)
print('limpeza:', n, '| .src restantes no corpo:', len(re.findall(r'class="src"', t[t.index("<main"):t.index('id="fontes"')])), '| links externos no corpo:', len(re.findall(r'href="http', t[t.index("<main"):t.index('id="fontes"')])))
