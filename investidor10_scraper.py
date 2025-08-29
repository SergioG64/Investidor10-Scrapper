# investidor10_scraper.py
# Autor: ChatGPT para Sérgio Gaigher
# Objetivo: Capturar dados da carteira pública no Investidor10 em horários definidos, com logs detalhados e screenshot para debugging

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import json
import sys

print("🔥 SCRIPT INVESTIDOR10_INICIADO")


# URL da carteira
URL = "https://investidor10.com.br/carteira/545535/"

# Caminhos para salvar dados conforme o horário
ARQUIVOS = {
    "00:00": "data/crypto_open.json",
    "10:30": "data/open_prices.json",
    "17:00": "data/final_prices.json"
}

async def extrair_dados(horario_execucao):
    print(f"🕐 Entrou na função com horário: {horario_execucao}")

    print(f"[INÍCIO] Horário: {horario_execucao} | Data/Hora: {datetime.now()}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, timeout=60000)

        # Espera seletor e dá tempo extra para o JS renderizar
        await page.wait_for_selector(".table-responsive", timeout=60000)
        await page.wait_for_timeout(5000)

        # Cria pasta se não existir
        Path("data").mkdir(parents=True, exist_ok=True)

        # Salva screenshot para debug
        screenshot_path = f"data/screenshot_{horario_execucao.replace(':','')}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"[✔] Screenshot salva em: {screenshot_path}")

        # Captura HTML bruto da página
        conteudo = await page.content()
        html_path = f"data/carteira_{horario_execucao.replace(':','')}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(conteudo)
        print(f"[✔] HTML bruto salvo: {html_path}")

        # Captura conteúdo das tabelas
        tabelas = await page.query_selector_all(".table-responsive")
        print(f"[INFO] Quantidade de tabelas capturadas: {len(tabelas)}")

        dados = []
        for idx, tabela in enumerate(tabelas):
            html = await tabela.inner_html()
            dados.append({"index": idx, "html": html})

        await browser.close()

        # Salva JSON com dados HTML das tabelas
        destino_json = ARQUIVOS.get(horario_execucao)
        if destino_json:
            with open(destino_json, "w", encoding="utf-8") as f:
                json.dump({"data": str(datetime.now()), "tabelas": dados}, f, ensure_ascii=False, indent=2)
            print(f"[✔] Dados extraídos salvos em: {destino_json}")
        else:
            print("[⚠] Horário inválido fornecido. Nenhum JSON salvo.")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            horario = sys.argv[1]
            print(f"[ARGS] Horário recebido via argumento: {horario}")
        else:
            horario = "17:00"
            print("[ARGS] Nenhum argumento recebido, usando default: 17:00")

        print(f"[INFO] Executando script para horário: {horario}")
        asyncio.run(extrair_dados(horario))
        print("[INFO] Script finalizado com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha na execução: {str(e)}")
