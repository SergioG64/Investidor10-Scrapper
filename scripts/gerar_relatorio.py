import os
import json
import pandas as pd
from datetime import datetime

def parse_moeda(valor):
    if not isinstance(valor, str):
        return 0.0

    valor = valor.strip()

    if valor.startswith("R$"):
        valor = valor.replace("R$", "").replace(".", "").replace(",", ".").strip()
    elif valor.startswith("US$"):
        valor = valor.replace("US$", "").replace(",", "").strip()
    elif valor in ("", "-", None):
        return 0.0

    try:
        return float(valor)
    except ValueError:
        return 0.0

def encontrar_arquivos_json():
    hoje = datetime.today().strftime("%Y-%m-%d")
    arquivos = os.listdir("dados")
    arquivos_hoje = [arq for arq in arquivos if arq.startswith(hoje) and arq.endswith(".json")]
    arquivos_hoje.sort()
    if len(arquivos_hoje) < 2:
        raise Exception(f"Esperado 2 arquivos para {hoje}, mas encontrado: {arquivos_hoje}")
    return arquivos_hoje[0], arquivos_hoje[-1]

def gerar_relatorio(path_inicio, path_fim):
    with open(path_inicio, "r", encoding="utf-8") as f:
        dados_inicio = json.load(f)
    with open(path_fim, "r", encoding="utf-8") as f:
        dados_fim = json.load(f)

    df_inicio = pd.DataFrame(dados_inicio)
    df_fim = pd.DataFrame(dados_fim)

    df = df_fim.merge(df_inicio, on="Ativo", suffixes=("_fim", "_inicio"))

    # Limpar campos numéricos
    for campo in ["Preço Médio_fim", "Preço Atual_fim", "Preço Médio_inicio", "Preço Atual_inicio"]:
        df[campo] = df[campo].apply(parse_moeda)

    df["Quantidade_fim"] = df["Quantidade_fim"].astype(float)
    df["Quantidade_inicio"] = df["Quantidade_inicio"].astype(float)

    # Calcula variação do dia com base na diferença de preço
    df["Variação_dia"] = ((df["Preço Atual_fim"] - df["Preço Atual_inicio"]) / df["Preço Atual_inicio"]) * 100

    # Saldo aplicado (Preço Médio x Quantidade)
    saldo_aplicado = df["Preço Médio_fim"] * df["Quantidade_fim"]
    saldo_total = df["Preço Atual_fim"] * df["Quantidade_fim"]
    variacao_total = ((saldo_total.sum() - saldo_aplicado.sum()) / saldo_aplicado.sum()) * 100

    # Top 3 Altas e Baixas
    df_ordenado = df.sort_values(by="Variação_dia", ascending=False)
    top_altas = df_ordenado.head(3)
    top_baixas = df_ordenado.tail(3).sort_values(by="Variação_dia")

    print("---")
    print("📊 RESUMO GERAL")
    print(f"- Valor aplicado: R$ {saldo_aplicado.sum():,.2f}")
    print(f"- Saldo bruto: R$ {saldo_total.sum():,.2f}")
    print(f"- Variação do dia: {variacao_total:+.2f}%")
    print("---")

    print("📈 Top 3 Altas do Dia")
    for idx, row in top_altas.iterrows():
        print(f"{idx+1}. {row['Ativo']} — {row['Variação_dia']:+.2f}%")

    print("\n📉 Top 3 Baixas do Dia")
    for idx, row in top_baixas.iterrows():
        print(f"{idx+1}. {row['Ativo']} — {row['Variação_dia']:+.2f}%")

    print("---")
    print("📁 Detalhamento dos ativos:")
    print("Ativo | Abertura | Fechamento | Variação Dia | Var. Investidor10 Início | Var. Investidor10 Fim")
    for _, row in df.iterrows():
        print(f"{row['Ativo']} | R$ {row['Preço Atual_inicio']:.2f} | R$ {row['Preço Atual_fim']:.2f} | {row['Variação_dia']:+.2f}% | {row.get('Variação_inicio','-')} | {row.get('Variação_fim','-')}")

if __name__ == "__main__":
    arq_inicio, arq_fim = encontrar_arquivos_json()
    gerar_relatorio(os.path.join("dados", arq_inicio), os.path.join("dados", arq_fim))
