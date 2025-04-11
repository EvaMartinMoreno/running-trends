# === EXTRACTION SCRIPT ===
# Combines the web scraping of races (Runedia) and GDP (datosmacro) data

import requests
import pandas as pd
import os
import time
from bs4 import BeautifulSoup

# === SCRAPER FOR RUNEDIA ===
def get_html(province, date, page):
    url = f"https://runedia.mundodeportivo.com/calendario-carreras/espana/{province}/provincia/tipo/distancia/{date}/0/0/{page}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

def parse_race_box(div, province):
    try:
        day = div.find("span", class_="dia").text.strip()
        month = div.find("span", class_="mes").text.strip()
    except:
        day, month = None, None

    try:
        title_tag = div.find("a", class_="nom-cursa")
        title = title_tag.text.strip()
        link = title_tag["href"]
    except:
        title, link = None, None

    try:
        location = div.find("span", class_="lloc").text.strip()
    except:
        location = None

    try:
        spans = div.find_all("span")
        type_ = spans[-2].text.strip() if len(spans) >= 2 else None
        distance = spans[-1].text.strip() if len(spans) >= 1 else None
    except:
        type_, distance = None, None

    return {
        "dia": day,
        "mes": month,
        "titulo": title,
        "enlace": f"https://runedia.mundodeportivo.com{link}" if link and link.startswith("/") else link,
        "localidad": location,
        "tipo": type_,
        "distancia": distance,
        "provincia": province
    }

def scrape_races(province, year):
    races = []
    page = 1
    date = f"{year}-01"
    while True:
        print(f"Scraping page {page} of {province} in {year}...")
        html = get_html(province, date, page)
        if html is None:
            break
        soup = BeautifulSoup(html, "html.parser")
        boxes = soup.find_all("div", class_="item-cursa")
        if not boxes:
            break
        races += [parse_race_box(box, province) for box in boxes]
        if len(races) > 500:
            break
        page += 1
        time.sleep(1)
    df = pd.DataFrame(races)
    if not df.empty:
        df["año"] = year
    return df

def save_race_data(df, province, year):
    path = f"data/raw/runedia/carreras_{province}_{year}.csv"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved: {path}")

def run_race_scraping():
    provinces = [
        "andalucia", "navarra", "asturias", "aragon", "canarias", "cantabria",
        "castilla-la-mancha", "castilla-y-leon", "catalunya", "ceuta", "euskadi",
        "extremadura", "galicia", "illes-balears", "la-rioja", "madrid", "melilla",
        "murcia", "valencia"
    ]
    for year in range(2000, 2026):
        for province in provinces:
            df = scrape_races(province, year)
            if not df.empty:
                save_race_data(df, province, year)

# === SCRAPER FOR GDP (DATOSMACRO) ===
def scrape_gdp_data():
    total_data = {"PIB_anual": {}, "PIB_capita": {}}
    for year in range(2000, 2025):
        url = f"https://datosmacro.expansion.com/pib/espana-comunidades-autonomas?anio={year}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table")

        if len(tables) > 0:
            for row in tables[0].find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) > 1:
                    comunidad = cols[0].text.strip()
                    pib_anual = cols[2].text.strip()
                    total_data["PIB_anual"].setdefault(year, []).append({"CCAA": comunidad, "PIB_anual": pib_anual})

        if len(tables) > 1:
            for row in tables[1].find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) > 1:
                    comunidad = cols[0].text.strip()
                    pib_capita = cols[2].text.strip()
                    total_data["PIB_capita"].setdefault(year, []).append({"CCAA": comunidad, "PIB_capita": pib_capita})

    df_anual = pd.DataFrame([{"Año": y, **entry} for y, data in total_data["PIB_anual"].items() for entry in data])
    df_capita = pd.DataFrame([{"Año": y, **entry} for y, data in total_data["PIB_capita"].items() for entry in data])
    df_gdp = pd.merge(df_anual, df_capita, on=["Año", "CCAA"], how="outer")

    output_path = "data/processed/gdp_dataset.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_gdp.to_csv(output_path, index=False, sep=";")
    print(f"GDP dataset saved to: {output_path}")

# === MAIN RUN ===
if __name__ == "__main__":
    run_race_scraping()
    scrape_gdp_data()
