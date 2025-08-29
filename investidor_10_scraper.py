# investidor10_scraper.py
# Autor: ChatGPT para Sérgio Gaigher
# Objetivo: Extrair dados da carteira Investidor10 em três horários diários para gerar relatório automatizado.

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import json

# URL da carteira
URL = "https://investidor10.com.br/carteira/545535/"

# Caminho para armazenar os dados
ARQUIVOS = {
    "00:00": "data/crypto_open.json",
    "10:30": "data/open_prices.json",
    "17:00": "data/final_prices.json"
}

# Função principal
async def extrair_dados(horario_execucao):
    print(f"Iniciando captura: {horario_execucao} | {datetime.now()}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, timeout=60000)
        await page.wait_for_selector(".table-responsive", timeout=60000)

        conteudo = await page.content()
        await browser.close()

        # Salvando HTML bruto (para debugging)
        Path("data").mkdir(parents=True, exist_ok=True)
        with open(f"data/carteira_{horario_execucao.replace(':','')}.html", "w", encoding="utf-8") as f:
            f.write(conteudo)

        # Simples extração de exemplo (ajuste conforme necessidade):
        tabelas = await page.query_selector_all(".table-responsive")
        dados = []

        for tabela in tabelas:
            html = await tabela.inner_html()
            dados.append(html)

        # Salva dados no arquivo correspondente
        with open(ARQUIVOS[horario_execucao], "w", encoding="utf-8") as f:
            json.dump({"data": str(datetime.now()), "htmls": dados}, f, ensure_ascii=False, indent=2)

        print(f"Captura finalizada: {ARQUIVOS[horario_execucao]}")

if __name__ == "__main__":
    import sys
    horario = sys.argv[1] if len(sys.argv) > 1 else "17:00"
    asyncio.run(extrair_dados(horario))
