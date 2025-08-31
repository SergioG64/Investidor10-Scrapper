import json
import os
import datetime
import difflib
from glob import glob


# ❌ ERRO se não houver arquivos
arquivos = sorted(glob("dados/*.json"))
if len(arquivos) < 2:
    print("[ERRO] É preciso ter ao menos dois arquivos JSON para comparar.")
    exit(1)

# ✅ Identifica o arquivo mais recente (final do dia) e anterior (início do dia)
json_final_path = arquivos[-1]
json_inicio_path = arquivos[-2]

with open(json_inicio_path, encoding="utf-8") as f:
    inicio_data = json.load(f)

with open(json_final_path, encoding="utf-8") as f:
    final_data = json.load(f)


# Extrai dados gerais (valor aplicado, saldo bruto, variação)
def extrair_resumo(d):
    return {
        "valor_aplicado": d.get("valor_aplicado", 0),
        "saldo_bruto": d.get("saldo_bruto", 0),
        "variacao": d.get("variacao", "0%")
    }


# Gera dicionário de ativos por nome
inicio_ativos = {a["ativo"]: a for a in inicio_data["ativos"]}
final_ativos = {a["ativo"]: a for a in final_data["ativos"]}


# Gera o relatório
hoje = datetime.datetime.today().strftime("%d/%m/%Y")
resumo_inicio = extrair_resumo(inicio_data)
resumo_final = extrair_resumo(final_data)

relatorio = f"""
📅 **Relatório da Carteira - {hoje}**

---
**📊 RESUMO GERAL**
- Valor aplicado: R$ {resumo_final['valor_aplicado']}
- Saldo bruto: R$ {resumo_final['saldo_bruto']}
- Variação do dia: {resumo_final['variacao']}

---
"""

# Cálculo da variação no dia
def calc_variacao_dia(inicio, fim):
    try:
        p1 = float(inicio.replace("R$", "").replace(",", "."))
        p2 = float(fim.replace("R$", "").replace(",", "."))
        return ((p2 - p1) / p1) * 100
    except:
        return 0

# Cria lista com ativos e variação no dia
ativos_resultado = []
for ativo, final_info in final_ativos.items():
    inicio_info = inicio_ativos.get(ativo)
    if not inicio_info:
        continue

    preco_inicio = inicio_info.get("preco_atual") or inicio_info.get("preco")
    preco_fim = final_info.get("preco_atual") or final_info.get("preco")

    variacao_dia = calc_variacao_dia(preco_inicio, preco_fim)

    ativos_resultado.append({
        "ativo": ativo,
        "categoria": final_info.get("categoria", "N/D"),
        "abertura": preco_inicio,
        "fechamento": preco_fim,
        "variacao_dia": variacao_dia,
        "var_ini": final_info.get("variacao_inicio"),
        "var_fim": final_info.get("variacao_fim")
    })

# Ordena por variação
altas = sorted(ativos_resultado, key=lambda x: -x["variacao_dia"])[:3]
baixas = sorted(ativos_resultado, key=lambda x: x["variacao_dia"])[:3]

relatorio += "**📈 Top 3 Altas do Dia**\n"
for a in altas:
    relatorio += f"1. {a['ativo']} — [+{a['variacao_dia']:.2f}%]\n"

relatorio += "\n**📉 Top 3 Baixas do Dia**\n"
for a in baixas:
    relatorio += f"1. {a['ativo']} — [{a['variacao_dia']:.2f}%]\n"

# Agrupamento por categoria
relatorio += "\n---\n**📁 Detalhamento por categoria:**\n"

categorias = {}
for a in ativos_resultado:
    cat = a["categoria"]
    categorias.setdefault(cat, []).append(a)

for cat, lista in categorias.items():
    relatorio += f"\n{cat} | Ativo | Abertura | Fechamento | Variação | Var.Início | Var.Fim\n"
    for a in lista:
        relatorio += f"- {a['ativo']} | {a['abertura']} | {a['fechamento']} | {a['variacao_dia']:.2f}% | {a['var_ini']} | {a['var_fim']}\n"

print(relatorio)

# Opcional: salvar em txt
with open("relatorio_diario.txt", "w", encoding="utf-8") as f:
    f.write(relatorio)

print("\n✅ Relatório gerado com sucesso.")
