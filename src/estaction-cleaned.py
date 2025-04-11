# ========================
# FILE: extraction.py
# ========================

import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

# --- Runedia Web Scraper ---
def get_html(province, date, page):
    url = f"https://runedia.mundodeportivo.com/calendario-carreras/espana/{province}/provincia/tipo/distancia/{date}/0/0/{page}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

def parse_race(div, province):
    def safe_extract(selector):
        try: return selector.text.strip()
        except: return None

    spans = div.find_all("span")
    return {
        "day": safe_extract(div.find("span", class_="dia")),
        "month": safe_extract(div.find("span", class_="mes")),
        "title": safe_extract(div.find("a", class_="nom-cursa")),
        "link": "https://runedia.mundodeportivo.com" + div.find("a", class_="nom-cursa")["href"] if div.find("a", class_="nom-cursa") else None,
        "location": safe_extract(div.find("span", class_="lloc")),
        "type": spans[-2].text.strip() if len(spans) >= 2 else None,
        "distance": spans[-1].text.strip() if len(spans) >= 1 else None,
        "province": province
    }

def scrape_races(province, date):
    all_races, page = [], 1
    while True:
        html = get_html(province, date, page)
        if not html:
            break
        soup = BeautifulSoup(html, "html.parser")
        races = soup.find_all("div", class_="item-cursa")
        if not races:
            break
        all_races.extend([parse_race(div, province) for div in races])
        if len(all_races) > 500:
            break
        page += 1
        time.sleep(1)
    df = pd.DataFrame(all_races)
    if not df.empty:
        df["year"] = int(date.split("-")[0])
    return df

def save_races(df, province, year):
    os.makedirs("data/raw/runedia", exist_ok=True)
    path = f"data/raw/runedia/carreras_{province}_{year}.csv"
    df.to_csv(path, index=False)
    print(f"✅ Saved: {path}")

def run_scraping():
    provinces = [
        "andalucia", "navarra", "asturias", "aragon", "canarias", "cantabria",
        "castilla-la-mancha", "castilla-y-leon", "catalunya", "ceuta", "euskadi",
        "extremadura", "galicia", "illes-balears", "la-rioja", "madrid", "melilla",
        "murcia", "valencia"
    ]
    for year in range(2000, 2026):
        for province in provinces:
            print(f"\n🔎 Scraping: {province} - {year}")
            df = scrape_races(province, f"{year}-01")
            if not df.empty:
                save_races(df, province, year)

if __name__ == "__main__":
    run_scraping()


# --- GDP Data Scraper ---
def scrape_gdp():
    total_data = {"PIB_anual": {}, "PIB_capita": {}}
    for year in range(2000, 2025):
        url = f"https://datosmacro.expansion.com/pib/espana-comunidades-autonomas?anio={year}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table")

        if tables:
            for row in tables[0].find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) > 1:
                    region, pib = cols[0].text.strip(), cols[2].text.strip()
                    total_data["PIB_anual"].setdefault(year, []).append({"CCAA": region, "PIB_anual": pib})

        if len(tables) > 1:
            for row in tables[1].find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) > 1:
                    region, per_capita = cols[0].text.strip(), cols[2].text.strip()
                    total_data["PIB_capita"].setdefault(year, []).append({"CCAA": region, "PIB_capita": per_capita})

    df_anual = pd.DataFrame([{"Year": y, **d} for y, lst in total_data["PIB_anual"].items() for d in lst])
    df_capita = pd.DataFrame([{"Year": y, **d} for y, lst in total_data["PIB_capita"].items() for d in lst])
    df_merged = pd.merge(df_anual, df_capita, on=["Year", "CCAA"], how="outer")
    df_merged.to_csv("data/raw/gdp_dataset.csv", index=False, sep=";")
    print("✅ GDP dataset saved to data/raw/gdp_dataset.csv")

if __name__ == "__main__":
    scrape_gdp()
