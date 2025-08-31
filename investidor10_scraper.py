
import sys
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

def salvar_screenshot(page, etapa, horario):
    filename = f"data/screenshot_{etapa}_{horario.replace(':', '')}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"[✓] Screenshot {etapa} salva: {filename}")

def main(horario):
    print("🔥 SCRIPT INVESTIDOR10_INICIADO")
    print(f"[ARGS] Horário recebido via argumento: {horario}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"🕓 Entrou na função com horário: {horario}")

        # Cria a pasta data/ se não existir
        os.makedirs("data", exist_ok=True)

        try:
            page.goto("https://investidor10.com.br/carteira/545535/", timeout=60000)
            salvar_screenshot(page, "pre_selector", horario)

            # Tenta fechar o modal de vídeo se visível
            try:
                modal_close = page.locator("button[aria-label='Fechar']")
                if modal_close.is_visible():
                    print("[INFO] Modal detectado. Fechando...")
                    modal_close.click()
                    page.wait_for_timeout(1000)
                else:
                    print("[INFO] Nenhum modal detectado.")
            except Exception as e:
                print("[WARN] Erro ao tentar fechar modal:", e)

            # Aguarda a tabela da carteira estar visível
            page.wait_for_selector(".table-responsive", timeout=30000)

            # Salva HTML bruto
            html_path = f"data/carteira_{horario.replace(':', '')}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(page.content())
            print(f"[✓] HTML salvo em: {html_path}")

            salvar_screenshot(page, "final", horario)
        except Exception as e:
            print("[ERRO] Ocorreu um erro:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        horario = sys.argv[1]
    else:
        horario = datetime.now().strftime("%H:%M")
    main(horario)
