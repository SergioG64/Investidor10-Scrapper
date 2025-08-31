import json
import os
import pandas as pd
from datetime import datetime


def parse_reais(valor):
    if isinstance(valor, str):
        valor = valor.replace("R$", "").replace("US$", "").replace(" ", "").replace(".", "").replace(",", ".")
        try:
            return float(valor)
        except ValueError:
            return 0.0
    return valor


def parse_quantidade(valor):
    if isinstance(valor, str):
        valor = valor.replace(",", ".")
        try:
            return float(valor)
        except ValueError:
            return 0.0
    return valor


def corrigir_nome_ativo(valor):
    if isinstance(valor, str) and len(valor) % 2 == 0:
        meio = len(valor) // 2
        if valor[:meio] == valor[meio:]:
            return valor[:meio]
    return valor


def gerar_relatorio(path_inicio, path_fim):
    with open(path_inicio, "r", encoding="utf-8") as f:
        dados_inicio = json.load(f)

    with open(path_fim, "r", encoding="utf-8") as f:
        dados_fim = json.load(f)

    df_inicio = pd.DataFrame(dados_inicio)
    df_fim = pd.DataFrame(dados_fim)

    df_inicio["ticker"] = df_inicio["Ativo"].apply(corrigir_nome_ativo)
    df_fim["ticker"] = df_fim["Ativo"].apply(corrigir_nome_ativo)

    df = df_fim.merge(df_inicio, on="ticker", suffixes=("_fim", "_inicio"))

    df["Preço Atual_inicio"] = df["Preço Atual_inicio"].apply(parse_reais)
    df["Preço Atual_fim"] = df["Preço Atual_fim"].apply(parse_reais)

    df["Variação Dia"] = (df["Preço Atual_fim"] - df["Preço Atual_inicio"]) / df["Preço Atual_inicio"] * 100

    df["Preço Médio_fim"] = df["Preço Médio_fim"].apply(parse_reais)
    df["Quantidade_fim"] = df["Quantidade_fim"].apply(parse_quantidade)
    df["Saldo_fim"] = df["Saldo_fim"].apply(parse_reais)

    valor_aplicado = 58796.95
    saldo_bruto = 61545.01
    variacao_total = 4.67

    print("\n📊 RESUMO GERAL")
    print(f"- Valor aplicado: R$ {valor_aplicado:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","))
    print(f"- Saldo bruto: R$ {saldo_bruto:,.2f}".replace(".", "v").replace(",", ".").replace("v", ","))
    print(f"- Variação do dia: +{variacao_total:.2f}%")
    print("---")

    ranking = df.dropna(subset=["Variação Dia"]).sort_values("Variação Dia", ascending=False)
    print("📈 Top 3 Altas do Dia")
    for i, row in ranking.head(3).iterrows():
        print(f"{i+1}. {row['ticker']} — {row['Variação Dia']:+.2f}%")

    print("📉 Top 3 Baixas do Dia")
    for i, row in ranking.tail(3).iterrows():
        print(f"{len(df)-2+i}. {row['ticker']} — {row['Variação Dia']:+.2f}%")

    print("---\n📁 Detalhamento dos ativos:\n")
    print("Ativo | Abertura | Fechamento | Variação Dia | Var. Investidor10 Início | Var. Investidor10 Fim")
    for _, row in df.iterrows():
        print(f"{row['ticker']} | R$ {row['Preço Atual_inicio']:.2f} | R$ {row['Preço Atual_fim']:.2f} | {row['Variação Dia']:+.2f}% | {row['Variação_inicio']} | {row['Variação_fim']}")


if __name__ == "__main__":
    arquivos = sorted([f for f in os.listdir("dados") if f.endswith(".json")])
    if len(arquivos) < 1:
        print("Nenhum arquivo JSON encontrado na pasta 'dados'.")
        exit(1)

    arq_fim = arquivos[-1]
    if len(arquivos) >= 2:
        arq_inicio = arquivos[-2]
    else:
        arq_inicio = arq_fim

    gerar_relatorio(os.path.join("dados", arq_inicio), os.path.join("dados", arq_fim))
