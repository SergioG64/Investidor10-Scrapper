import asyncio
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import json

print("🔥 SCRIPT INVESTIDOR10_INICIADO")

if len(sys.argv) > 1:
    horario = sys.argv[1]
    print(f"[ARGS] Horário recebido via argumento: {horario}")
else:
    horario = "17:00"
    print("[ARGS] Nenhum argumento recebido, usando default: 17:00")

ARQUIVOS = {
    "00:00": "data/crypto_open.json",
    "10:30": "data/open_prices.json",
    "17:00": "data/final_prices.json"
}

URL = "https://investidor10.com.br/carteira/545535/"

async def extrair_dados(horario_execucao):
    print(f"🕐 Entrou na função com horário: {horario_execucao}")

    Path("data").mkdir(parents=True, exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(URL, timeout=60000)
            await page.wait_for_selector(".table-responsive", timeout=60000)
            await page.wait_for_timeout(5000)

            # Screenshot
            screenshot_path = f"data/screenshot_{horario_execucao.replace(':','')}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"[✔] Screenshot salva: {screenshot_path}")

            # HTML
            conteudo = await page.content()
            html_path = f"data/carteira_{horario_execucao.replace(':','')}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(conteudo)
            print(f"[✔] HTML salvo: {html_path}")

            # Tabelas
            tabelas = await page.query_selector_all(".table-responsive")
            print(f"[INFO] Quantidade de tabelas encontradas: {len(tabelas)}")

            dados = []
            for idx, tabela in enumerate(tabelas):
                html = await tabela.inner_html()
                dados.append({"index": idx, "html": html})

            await browser.close()

            json_dest = ARQUIVOS.get(horario_execucao)
            if json_dest:
                with open(json_dest, "w", encoding="utf-8") as f:
                    json.dump({
                        "data": str(datetime.now()),
                        "tabelas": dados
                    }, f, ensure_ascii=False, indent=2)
                print(f"[✔] JSON salvo: {json_dest}")
            else:
                print("[⚠] Horário inválido. JSON não salvo.")

    except Exception as e:
        print(f"[ERRO] Ocorreu um erro: {e}")

# Executa
asyncio.run(extrair_dados(horario))
