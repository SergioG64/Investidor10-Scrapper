import json
import os
from datetime import datetime
import pandas as pd

def encontrar_arquivos_json():
    hoje = datetime.now().strftime("%Y-%m-%d")
    arquivos = sorted([f for f in os.listdir("dados") if f.startswith(hoje) and f.endswith(".json")])

    if len(arquivos) == 0:
        raise Exception(f"Nenhum arquivo encontrado para {hoje} na pasta dados/")

    if len(arquivos) == 1:
        print(f"⚠️ Apenas um arquivo encontrado para {hoje}, relatório será gerado com dados repetidos.")
        return arquivos[0], arquivos[0]

    return arquivos[0], arquivos[-1]

def carregar_dados(path):
    with open(path, encoding='utf-8') as f:
        dados = json.load(f)

    # Corrigir colunas e normalizar
    for item in dados:
        if 'Ativo' in item and 'ticker' not in item:
            item['ticker'] = item['Ativo'][:6]  # Corrige caso tenha ticker repetido (ex: WEGE3WEGE3)

    return pd.DataFrame(dados)

def gerar_relatorio(dados_inicio, dados_fim):
    df_inicio = carregar_dados(dados_inicio)
    df_fim = carregar_dados(dados_fim)

    df = df_fim.merge(df_inicio, on="ticker", suffixes=("_fim", "_inicio"))

    # Conversões numéricas
    def parse_percent(val):
        try:
            return float(val.replace("%", "").replace(",", "."))
        except:
            return 0.0

    def parse_reais(val):
        try:
            return float(val.replace("R$", "").replace(" ", "").replace(".", "").replace(",", "."))
        except:
            return 0.0

    df["var_dia"] = df["Preço Atual_fim"].apply(parse_reais) - df["Preço Atual_inicio"].apply(parse_reais)
    df["var_dia_pct"] = (df["var_dia"] / df["Preço Atual_inicio"].apply(parse_reais)) * 100

    # Ordenar por variação
    df_sorted = df.sort_values("var_dia_pct", ascending=False)

    top_altas = df_sorted.head(3)
    top_baixas = df_sorted.tail(3).sort_values("var_dia_pct")

    saldo_total = df["Saldo_fim"].apply(parse_reais).sum()
    saldo_aplicado = df["Preço Médio_fim"].apply(parse_reais) * df["Quantidade_fim"].astype(float)
    valor_aplicado = saldo_aplicado.sum()
    variacao_total = (saldo_total - valor_aplicado) / valor_aplicado * 100

    print("""
🎯 **RELATÓRIO DIÁRIO DA CARTEIRA INVESTIDOR10**

---
📊 **RESUMO GERAL**
- Valor aplicado: R$ {:.2f}
- Saldo bruto: R$ {:.2f}
- Variação do dia: {:.2f}%
---
📈 **Top 3 Altas do Dia**""".format(valor_aplicado, saldo_total, df["var_dia_pct"].mean()))

    for i, row in top_altas.iterrows():
        print(f"{row['ticker']} — +{row['var_dia_pct']:.2f}%")

    print("\n📉 **Top 3 Baixas do Dia**")
    for i, row in top_baixas.iterrows():
        print(f"{row['ticker']} — {row['var_dia_pct']:.2f}%")

    print("\n---\n📁 **Detalhamento por Ativo**")
    for _, row in df.iterrows():
        print(f"{row['ticker']}: Abertura {row['Preço Atual_inicio']}, Fechamento {row['Preço Atual_fim']}, Variação do dia {row['var_dia_pct']:.2f}%")

if __name__ == "__main__":
    arq_inicio, arq_fim = encontrar_arquivos_json()
    gerar_relatorio(os.path.join("dados", arq_inicio), os.path.join("dados", arq_fim))
