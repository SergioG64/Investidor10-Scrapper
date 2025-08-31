
import sys
import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def main(horario):
    timestamp = datetime.now().strftime("%Y-%m-%d")
    folder = Path("data")
    folder.mkdir(exist_ok=True)
    
    html_path = folder / f"carteira_{horario.replace(':', '')}_{timestamp}.html"
    screenshot_pre = folder / f"screenshot_pre_selector_{horario.replace(':', '')}.png"
    screenshot_post = folder / f"screenshot_post_modal_{horario.replace(':', '')}.png"
    screenshot_fail = folder / f"screenshot_table_fail_{horario.replace(':', '')}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        log("Acessando a página...")
        page.goto("https://investidor10.com.br/carteira/545535/", timeout=60000)
        page.wait_for_timeout(5000)
        page.screenshot(path=str(screenshot_pre))
        
        # Fechar modal se estiver presente
        try:
            if page.locator("#modal-sign").is_visible():
                log("Modal detectado. Tentando fechar...")
                page.click(".modal-close")
                page.wait_for_timeout(2000)
                page.screenshot(path=str(screenshot_post))
            else:
                log("Nenhum modal visível.")
        except Exception as e:
            log(f"Erro ao fechar modal (ignorado): {e}")
        
        # Esperar pela tabela
        try:
            page.wait_for_selector(".table-responsive", timeout=30000)
            html = page.content()
            html_path.write_text(html, encoding="utf-8")
            log(f"HTML salvo em: {html_path}")
        except Exception as e:
            page.screenshot(path=str(screenshot_fail))
            log(f"Erro ao aguardar tabela: {e}")

        browser.close()

if __name__ == "__main__":
    horario = sys.argv[1] if len(sys.argv) > 1 else "manual"
    main(horario)
