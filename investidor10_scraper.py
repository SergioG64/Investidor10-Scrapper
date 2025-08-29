# investidor10_scraper.py
# Autor: ChatGPT para Sérgio Gaigher
# Objetivo: Capturar dados da carteira pública no Investidor10 em horários definidos

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import json
import sys

# URL pública da carteira
URL = "https://investidor10.com.br/carteira/545535/"

# Caminhos de destino conforme horário de execução
ARQUIVOS = {
    "00:00": "data/crypto_open.json",
    "10:30": "data/open_prices.json",
    "17:00": "data/final_prices.json"
}

# Função principal de extração
async def extrair_dados(horario_execucao):
    print(f"[INÍCIO] Horário: {horario_execucao} | Data/Hora: {datetime.now()}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, timeout=60000)
        
        # Aguarda o carregamento explícito do DOM + tempo extra para JS
        await page.wait_for_selector(".table-responsive", timeout=60000)
        await page.wait_for_timeout(5000)  # aguarda mais 5 segundos para garantir


        # Captura HTML
        conteudo = await page.content()

        # Cria pasta se necessário
        Path("data").mkdir(parents=True, exist_ok=True)

        # Salva HTML bruto para debug
        nome_html = f"data/carteira_{horario_execucao.replace(':','')}.html"
        with open(nome_html, "w", encoding="utf-8") as f:
            f.write(conteudo)
        print(f"[✔] HTML bruto salvo: {nome_html}")

        # Captura todas as tabelas visíveis
        tabelas = await page.query_selector_all(".table-responsive")
        dados = []

        for idx, tabela in enumerate(tabelas):
            html = await tabela.inner_html()
            dados.append({"index": idx, "html": html})
        print(f"[INFO] Quantidade de tabelas capturadas: {len(tabelas)}")

        # Fecha o navegador
        await browser.close()

        # Salva como JSON
        destino_json = ARQUIVOS.get(horario_execucao)
        if destino_json:
            with open(destino_json, "w", encoding="utf-8") as f:
                json.dump({"data": str(datetime.now()), "tabelas": dados}, f, ensure_ascii=False, indent=2)
            print(f"[✔] Dados extraídos salvos em: {destino_json}")
        else:
            print("[⚠] Horário inválido fornecido. Nenhum JSON salvo.")
        screenshot_path = f"data/screenshot_{horario_execucao.replace(':','')}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"[✔] Screenshot salva em: {screenshot_path}")


# Ponto de entrada
if __name__ == "__main__":
    try:
        horario = sys.argv[1] if len(sys.argv) > 1 else "17:00"
        print(f"[INFO] Executando script para horário: {horario}")
        asyncio.run(extrair_dados(horario))
        print("[INFO] Script finalizado com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha na execução: {str(e)}")
