import os
import json
import datetime
import pandas as pd

# Caminho da pasta onde os arquivos JSON serão salvos
data_dir = "dados"

def encontrar_arquivos_json():
    arquivos = sorted(os.listdir(data_dir))
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    arquivos_hoje = [f for f in arquivos if f.startswith(hoje) and f.endswith(".json")]
    if len(arquivos_hoje) < 2:
        raise Exception(f"Esperado 2 arquivos para {hoje}, mas encontrado: {arquivos_hoje}")
    return os.path.join(data_dir, arquivos_hoje[0]), os.path.join(data_dir, arquivos_hoje[1])

def carregar_dados(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def gerar_relatorio(inicio, fim):
    df_inicio = pd.DataFrame(inicio)
    df_fim = pd.DataFrame(fim)

    df = df_fim.merge(df_inicio, on="ticker", suffixes=("_fim", "_inicio"))
    df["variacao_dia"] = df["preco_fim"] / df["preco_inicio"] - 1

    df.sort_values("variacao_dia", ascending=False, inplace=True)

    # Resumo
    valor_aplicado = fim[0].get("valor_aplicado", 0)
    saldo_bruto = fim[0].get("saldo_bruto", 0)
    variacao_total = fim[0].get("variacao", 0)

    print("""\n📊 RESUMO GERAL
- Valor aplicado: R$ {:.2f}
- Saldo bruto: R$ {:.2f}
- Variação do dia: {:.2%}
""".format(valor_aplicado, saldo_bruto, variacao_total))

    print("**📈 Top 3 Altas do Dia**")
    for i, row in df.head(3).iterrows():
        print(f"{i+1}. {row['ticker']} — +{row['variacao_dia']*100:.2f}%")

    print("\n**📉 Top 3 Baixas do Dia**")
    for i, row in df.tail(3).sort_values("variacao_dia").iterrows():
        print(f"{i+1}. {row['ticker']} — {row['variacao_dia']*100:.2f}%")

    print("\n---\n**📁 Detalhamento por categoria:**")
    for categoria in df["categoria"].unique():
        print(f"\n{categoria} | Ativo | Abertura | Preço ~17h | Variação")
        for _, row in df[df["categoria"] == categoria].iterrows():
            print(f"{row['ticker']} | {row['preco_inicio']:.2f} | {row['preco_fim']:.2f} | {row['variacao_dia']*100:.2f}%")

if __name__ == "__main__":
    arq_inicio, arq_fim = encontrar_arquivos_json()
    dados_inicio = carregar_dados(arq_inicio)
    dados_fim = carregar_dados(arq_fim)
    gerar_relatorio(dados_inicio, dados_fim)
