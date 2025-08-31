import sys
import os
import json
from bs4 import BeautifulSoup

def parse_table(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    all_tables = soup.find_all("table", class_="table table-bordered")

    ativos = []

    for table in all_tables:
        rows = table.find_all("tr")[1:]  # Ignora o cabeçalho

        for row in rows:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) < 5:
                continue

            ativo = {
                "ativo": cols[0],
                "quantidade": cols[1],
                "preco_medio": cols[2],
                "preco_atual": cols[3],
                "variacao": cols[4],
                "saldo": cols[5] if len(cols) > 5 else None,
                "categoria": None  # opcional, podemos inferir depois
            }

            ativos.append(ativo)

    return ativos

if __name__ == "__main__":
    horario = sys.argv[1] if len(sys.argv) > 1 else "manual"
    html_path = f"data/html_raw_{horario}.html"
    output_path = f"data/parsed_{horario}.json"

    if not os.path.exists(html_path):
        print(f"Arquivo HTML não encontrado: {html_path}")
        sys.exit(1)

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    parsed_data = parse_table(html_content)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)

    print(f"✅ JSON gerado: {output_path}")
