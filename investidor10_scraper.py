import sys
import os
from datetime import datetime
from playwright.async_api import async_playwright

async def main(horario):
    print("🔥 SCRIPT INVESTIDOR10_INICIADO")
    print(f"[ARGS] Horário recebido via argumento: {horario}")

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    filename_prefix = f"{horario.replace(':', '')}"
    screenshot_path = os.path.join(output_dir, f"screenshot_pre_selector_{filename_prefix}.png")
    html_output_path = os.path.join(output_dir, f"html_raw_{filename_prefix}.html")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://investidor10.com.br/carteira/545535/")

        await page.wait_for_timeout(1000)  # Aguarda elementos da página iniciarem

        # Tenta fechar modal se aparecer
        try:
            modal_close = page.locator("#modal-sign .modal-close").first
            if await modal_close.is_visible():
                print("📦 [INFO] Modal detectado, tentando fechar...")
                await modal_close.click(force=True)
                await page.wait_for_timeout(500)
        except Exception as e:
            print(f"⚠️ [WARN] Erro ao tentar fechar modal: {e}")

        # Salva screenshot antes de buscar a tabela
        await page.screenshot(path=screenshot_path)
        print(f"🖼️ Screenshot pre_selector salva: {screenshot_path}")

        # Aguarda a tabela principal aparecer
        print("📄 [INFO] Esperando tabela .table-bordered aparecer...")
        try:
            await page.wait_for_selector(".table-bordered", timeout=15000)
            content = await page.content()
            with open(html_output_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ HTML bruto salvo: {html_output_path}")

            # Extrai nomes das colunas da tabela (por debug)
            ths = await page.locator(".table-bordered thead tr th").all_inner_texts()
            print("📋 Colunas da Tabela:")
            for col in ths:
                print(f" - {col.strip()}")

        except Exception as e:
            print(f"❌ [ERRO] Tabela não carregada: {e}")

        await browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ Forneça o horário como argumento (ex: 10:30)")
        sys.exit(1)

    horario = sys.argv[1]
    import asyncio
    asyncio.run(main(horario))
