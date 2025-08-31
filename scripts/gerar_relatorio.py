import os
import json
import pandas as pd
from datetime import datetime

def parse_reais(valor):
    if isinstance(valor, str):
        valor = valor.replace("R$", "").replace(".", "").replace(",", ".").strip()
    return float(valor)

def parse_valor(valor):
    if isinstance(valor, str):
        valor = valor.replace(",", ".").strip()
    return float(valor)

def parse_percentual(pct):
    return float(pct.replace("%", "").replace(",", ".").strip())

def encontrar_arquivos_json():
    hoje = datetime.today().strftime("%Y-%m-%d")
    pasta = "dados"
    arquivos_hoje = sorted([
        f for f in os.listdir(pasta)
        if f.startswith(hoje) and f.endswith(".json")
    ])
    if len(arquivos_hoje) < 2:
        raise Exception(f"Esperado 2 arquivos para {hoje}, mas encontrado: {arquivos_hoje}")
    return arquivos_hoje[0], arquivos_hoje[1]

def gerar_relatorio(arquivo_inicio, arquivo_fim):
    with open(arquivo_inicio, encoding="utf-8") as f:
        dados_inicio = json.load(f)

    with open(arquivo_fim, encoding="utf-8") as f:
        dados_fim = json.load(f)

    df_inicio = pd.DataFrame(dados_inicio)
    df_fim = pd.DataFrame(dados_fim)

    # Corrige coluna "Ativo" duplicada tipo "VALE3VALE3"
    df_inicio["Ativo"] = df_inicio["Ativo"].str.extract(r"(\D+\d{1,2})")
    df_fim["Ativo"] = df_fim["Ativo"].str.extract(r"(\D+\d{1,2})")

    df = df_fim.merge(df_inicio, on="Ativo", suffixes=("_fim", "_inicio"))

    df["Preço Médio_fim"] = df["Preço Médio_fim"].apply(parse_reais)
    df["Quantidade_fim"] = df["Quantidade_fim"].apply(parse_valor)
    saldo_aplicado = df["Preço Médio_fim"] * df["Quantidade_fim"]
    saldo_atual = df["Saldo_fim"].apply(parse_reais)

    df["Variação_Dia"] = ((saldo_atual - saldo_aplicado) / saldo_aplicado) * 100
    df["Variação_Dia_fmt"] = df["Variação_Dia"].map(lambda x: f"{x:.2f}%")

    # Top 3
    top_altas = df.nlargest(3, "Variação_Dia")[["Ativo", "Variação_Dia_fmt"]]
    top_baixas = df.nsmallest(3, "Variação_Dia")[["Ativo", "Variação_Dia_fmt"]]

    # Totais
    total_aplicado = saldo_aplicado.sum()
    total_atual = saldo_atual.sum()
    variacao_total = ((total_atual - total_aplicado) / total_aplicado) * 100

    # 📝 Relatório
    print("\n🎯 **Relatório Diário - Investidor10**")
    print("\n---\n**📊 RESUMO GERAL**")
    print(f"- Valor aplicado: R$ {total_aplicado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    print(f"- Saldo bruto: R$ {total_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    print(f"- Variação do dia: {variacao_total:.2f}%")

    print("\n---\n**📈 Top 3 Altas do Dia**")
    for i, row in top_altas.iterrows():
        print(f"{i+1}. {row['Ativo']} — +{row['Variação_Dia_fmt']}")

    print("\n**📉 Top 3 Baixas do Dia**")
    for i, row in top_baixas.iterrows():
        print(f"{i+1}. {row['Ativo']} — {row['Variação_Dia_fmt']}")

    print("\n---\n**📁 Detalhamento por categoria:**")
    for _, row in df.iterrows():
        print(f"{row['Ativo']}: Abertura={row['Preço Atual_inicio']}, Fechamento={row['Preço Atual_fim']}, Variação={row['Variação_Dia_fmt']}, Inv10 Início={row['Variação_inicio']}, Inv10 Fim={row['Variação_fim']}")

if __name__ == "__main__":
    arq_inicio, arq_fim = encontrar_arquivos_json()
    gerar_relatorio(os.path.join("dados", arq_inicio), os.path.join("dados", arq_fim))
