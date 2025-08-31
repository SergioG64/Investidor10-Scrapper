import os
import json
from bs4 import BeautifulSoup

# Detectar qual arquivo HTML usar
html_files = [f for f in os.listdir("data") if f.startswith("html_raw_") and f.endswith(".html")]
html_files.sort()
latest_html_file = os.path.join("data", html_files[-1])

with open(latest_html_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

tables = soup.select("table.table-bordered")
all_data = []

for table in tables:
    headers = []
    for th in table.select("thead tr th"):
        header = th.get_text(strip=True)
        headers.append(header if header else "Unnamed")

    # Ignora tabelas sem headers relevantes
    if not headers or headers.count("Ativo") == len(headers):
        continue

    for row in table.select("tbody tr"):
        cols = row.find_all("td")
        if not cols or len(cols) != len(headers):
            continue
        item = {}
        for i, col in enumerate(cols):
            item[headers[i]] = col.get_text(strip=True)
        all_data.append(item)

# Salvar o JSON extraído
output_file = latest_html_file.replace(".html", ".json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"[✅] JSON gerado com {len(all_data)} ativos: {output_file}")
