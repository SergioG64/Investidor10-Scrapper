# gerar_relatorio.py

import os
import json
from datetime import datetime
from glob import glob

def carregar_dados():
    arquivos = sorted(glob("dados/*.json"))
    if len(arquivos) < 2:
        raise Exception("São necessários pelo menos dois arquivos JSON para comparar.")
    with open(arquivos[-2], encoding='utf-8') as f:
        dados_inicio = json.load(f)
    with open(arquivos[-1], encoding='utf-8') as f:
        dados_fim = json.load(f)
    return dados_inicio, dados_fim

def normalizar_valor(valor):
    if isinstance(valor, str):
        return float(valor.replace('%', '').replace('+', '').replace('−', '-').replace(',', '.'))
    return float(valor)

def gerar_relatorio(dados_inicio, dados_fim):
    ativos = {}
    for ativo in dados_fim:
        nome = ativo.get("Ativo") or ativo.get("Nome") or ativo.get("Título")
        if not nome:
            continue
        ativos[nome] = {
            "final": ativo,
            "inicio": next((a for a in dados_inicio if a.get("Ativo") == nome or a.get("Nome") == nome or a.get("Título") == nome), {})
        }

    # RESUMO GERAL
    total_aplicado = 0.0
    total_saldo = 0.0
    for ativo in ativos.values():
        aplicado = ativo["final"].get("Aplicado")
        saldo = ativo["final"].get("Saldo")
        if aplicado: total_aplicado += normalizar_valor(aplicado)
        if saldo: total_saldo += normalizar_valor(saldo)
    variacao_dia = ((total_saldo / total_aplicado) - 1) * 100 if total_aplicado else 0

    linhas = []
    linhas.append("📊 RESUMO GERAL")
    linhas.append(f"- Valor aplicado: R$ {total_aplicado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    linhas.append(f"- Saldo bruto: R$ {total_saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    linhas.append(f"- Variação do dia: {variacao_dia:+.2f}%")
    linhas.append("\n")

    # VARIAÇÃO DO DIA POR ATIVO
    variacoes = []
    for nome, dados in ativos.items():
        try:
            preco_ini = normalizar_valor(dados["inicio"].get("Preço Atual") or dados["inicio"].get("PU D-1"))
            preco_fim = normalizar_valor(dados["final"].get("Preço Atual") or dados["final"].get("PU Hoje"))
            variacao = ((preco_fim / preco_ini) - 1) * 100
            variacoes.append((nome, variacao))
        except:
            continue

    variacoes_ordenadas = sorted(variacoes, key=lambda x: x[1], reverse=True)
    linhas.append("📈 Top 3 Altas do Dia")
    for i, (nome, var) in enumerate(variacoes_ordenadas[:3], 1):
        linhas.append(f"{i}. {nome} — [+{var:.2f}%]")

    linhas.append("\n📉 Top 3 Baixas do Dia")
    for i, (nome, var) in enumerate(variacoes_ordenadas[-3:], 1):
        linhas.append(f"{i}. {nome} — [{var:.2f}%]")

    # DETALHAMENTO
    linhas.append("\n📁 Detalhamento por categoria:")
    for nome, dados in ativos.items():
        try:
            preco_ini = dados["inicio"].get("Preço Atual") or dados["inicio"].get("PU D-1")
            preco_fim = dados["final"].get("Preço Atual") or dados["final"].get("PU Hoje")
            variacao = ((normalizar_valor(preco_fim) / normalizar_valor(preco_ini)) - 1) * 100
        except:
            preco_ini, preco_fim, variacao = "-", "-", 0

        var_inicio = dados["inicio"].get("Variação") or "-"
        var_fim = dados["final"].get("Variação") or "-"

        linhas.append(f"{nome} | {preco_ini} → {preco_fim} | ΔDia: {variacao:+.2f}% | Inv10 Início: {var_inicio} | Inv10 Fim: {var_fim}")

    with open("relatorio_diario.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    print("\n".join(linhas))

if __name__ == "__main__":
    dados_inicio, dados_fim = carregar_dados()
    gerar_relatorio(dados_inicio, dados_fim)
