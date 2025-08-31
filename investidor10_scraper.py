from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import os
import sys
import time
from datetime import datetime

# Argumento obrigatório: horario ("00:00", "10:30" ou "17:00")
if len(sys.argv) < 2:
    print("[ERRO] Horário não especificado. Use: python investidor10_scraper.py \"10:30\"")
    sys.exit(1)

horario = sys.argv[1]
print(f"🔥 SCRIPT INVESTIDOR10_INICIADO")
print(f"[ARGS] Horário recebido via argumento: {horario}")

url = "https://investidor10.com.br/carteira/545535/"
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--start-maximized"])
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    print(f"⏰ Entrou na função com horário: {horario}")
    page.goto(url, timeout=60000)

    # Screenshot antes de qualquer interação (debug)
    screenshot_pre = f"{data_dir}/screenshot_pre_selector_{horario.replace(':','')}.png"
    page.screenshot(path=screenshot_pre)
    print(f"✅ Screenshot pre_selector salva: {screenshot_pre}")

    # Tentar fechar modal de vídeo (se aparecer)
    try:
        modal = page.locator("#modal-sign.modal-tutorial.show")
        if modal.is_visible(timeout=5000):
            print("[INFO] Modal detectado, tentando fechar...")
            page.locator("#modal-sign .modal-close").click()
            modal.wait_for(state="hidden", timeout=5000)
            print("[INFO] Modal fechado com sucesso.")
        else:
            print("[INFO] Nenhum modal visível detectado.")
    except Exception as e:
        print(f"[WARN] Modal não tratado corretamente: {e}")

    # Espera a tabela principal renderizar
    try:
        print("[INFO] Esperando tabela .table-bordered aparecer...")
        page.wait_for_selector("table.table-bordered", timeout=30000)
    except PlaywrightTimeout:
        print("[ERRO] Timeout: Page.wait_for_selector: Timeout 30000ms exceeded.")
        screenshot_fail = f"{data_dir}/screenshot_table_fail_{horario.replace(':','')}.png"
        page.screenshot(path=screenshot_fail)
        print(f"[ERRO] Screenshot de erro salva: {screenshot_fail}")
        browser.close()
        sys.exit(1)

    # Extrai o HTML bruto (debug)
    html_raw = page.content()
    html_path = f"{data_dir}/html_raw_{horario.replace(':','')}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_raw)
    print(f"✅ HTML bruto salvo: {html_path}")

    # Parse com BeautifulSoup
    soup = BeautifulSoup(html_raw, "html.parser")
    table = soup.select_one("table.table-bordered")
    if not table:
        print("[ERRO] Tabela .table-bordered não encontrada no DOM.")
        browser.close()
        sys.exit(1)

    headers = [th.get_text(strip=True) for th in table.select("thead th")]
    print("\nColunas da Tabela:")
    for col in headers:
        print(" -", col)

    # Captura as linhas (opcional)
    rows = []
    for tr in table.select("tbody tr"):
        cols = [td.get_text(strip=True) for td in tr.select("td")]
        rows.append(cols)

    print(f"\nTotal de linhas capturadas: {len(rows)}")

    browser.close()
