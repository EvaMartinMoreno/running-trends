import requests
import pandas as pd
import time
import os
from bs4 import BeautifulSoup

# === Función para obtener el HTML de una página ===
def obtener_html(provincia, fecha, pagina):
    url = f"https://runedia.mundodeportivo.com/calendario-carreras/espana/{provincia}/provincia/tipo/distancia/{fecha}/0/0/{pagina}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"❌ Error {response.status_code} en página {pagina} de {provincia}")
        return None

# === Función para extraer datos de una carrera individual ===
def parsear_caja_carrera(div, provincia):
    try:
        dia = div.find("span", class_="dia").text.strip()
        mes = div.find("span", class_="mes").text.strip()
    except:
        dia, mes = None, None

    try:
        enlace_tag = div.find("a", class_="nom-cursa")
        titulo = enlace_tag.text.strip()
        enlace = enlace_tag["href"]
    except:
        titulo, enlace = None, None

    try:
        localidad = div.find("span", class_="lloc").text.strip()
    except:
        localidad = None

    try:
        spans = div.find_all("span")
        tipo = spans[-2].text.strip() if len(spans) >= 2 else None
        distancia = spans[-1].text.strip() if len(spans) >= 1 else None
    except:
        tipo, distancia = None, None

    return {
        "dia": dia,
        "mes": mes,
        "titulo": titulo,
        "enlace": f"https://runedia.mundodeportivo.com{enlace}" if enlace and enlace.startswith("/") else enlace,
        "localidad": localidad,
        "tipo": tipo,
        "distancia": distancia,
        "provincia": provincia
    }

# === Función principal para scrapear todas las páginas de una provincia y año ===
def obtener_carreras(provincia, fecha):
    carreras = []
    pagina = 1
    while True:
        print(f"🌐 Scrapeando página {pagina} de {provincia} ({fecha})")
        html = obtener_html(provincia, fecha, pagina)
        if html is None:
            break

        soup = BeautifulSoup(html, "html.parser")
        cajas = soup.find_all("div", class_="item-cursa")
        if not cajas:
            print("🔚 Fin de resultados (no hay más carreras).")
            break

        carreras += [parsear_caja_carrera(div, provincia) for div in cajas]
        if len(carreras) > 500:
            print("⚠️ Demasiadas carreras, deteniendo scraping por seguridad...")
            break
        pagina += 1
        time.sleep(1)

    df = pd.DataFrame(carreras)
    if not df.empty:
        df["año"] = int(fecha.split("-")[0])
    return df

# === Guardar los datos en CSV ===
def guardar_csv(df, provincia, año):
    os.makedirs("data", exist_ok=True)
    ruta = f"data/raw/runedia/carreras_{provincia}_{año}.csv"
    df.to_csv(ruta, index=False)
    print(f"✅ Archivo guardado: {ruta}")

# === EJECUCIÓN GENERAL ===
def run():
    provincias = [
        "andalucia", "navarra", "asturias", "aragon", "canarias", "cantabria",
        "castilla-la-mancha", "castilla-y-leon", "catalunya", "ceuta", "euskadi",
        "extremadura", "galicia", "illes-balears", "la-rioja", "madrid", "melilla",
        "murcia", "valencia"
    ]

    for year in range(2000, 2026):
        fecha_inicio = f"{year}-01"
        for provincia in provincias:
            print(f"\n🔎 Iniciando scraping para: {provincia} ({year})")
            df = obtener_carreras(provincia, fecha_inicio)
            if not df.empty:
                guardar_csv(df, provincia, year)
            else:
                print(f"⚠️ No se encontraron carreras para {provincia} en {year}")

if __name__ == "__main__":
    run()
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from IPython.display import display

# Dictionaries to store the data
total_data = {"PIB_anual": {}, "PIB_capita": {}}

# Range of years to scrape
years = range(2000, 2025) 

# Loop through each year and scrape the data
for year in years:
    url = f"https://datosmacro.expansion.com/pib/espana-comunidades-autonomas?anio={year}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find all the tables
    tables = soup.find_all("table")
    
    # Scrape the first table (PIB anual)
    if len(tables) > 0:
        table_pib_anual = tables[0]
        for row in table_pib_anual.find_all("tr")[1:]: 
            cols = row.find_all("td")
            if len(cols) > 1:
                comunidad = cols[0].text.strip()
                pib_crudo = cols[2].text.strip()
                
                # Save the data in the dictionary
                if year not in total_data["PIB_anual"]:
                    total_data["PIB_anual"][year] = []
                total_data["PIB_anual"][year].append({
                    "CCAA": comunidad,
                    "PIB_anual": pib_crudo
                })
    
    # Scrape the second table (PIB per cápita)
    if len(tables) > 1:
        table_pib_per_capita = tables[1]
        for row in table_pib_per_capita.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) > 1:
                comunidad = cols[0].text.strip()
                pib_per_capita = cols[2].text.strip()
                
                # Save the data in the dictionary
                if year not in total_data["PIB_capita"]:
                    total_data["PIB_capita"][year] = []
                total_data["PIB_capita"][year].append({
                    "CCAA": comunidad,
                    "PIB_capita": pib_per_capita
                })

# Convert the dictionaries to DataFrames
df_PIB_anual = pd.DataFrame([
    {"Año": year, **dato}
    for year, datos in total_data["PIB_anual"].items()
    for dato in datos
])

df_PIB_capita = pd.DataFrame([
    {"Año": year, **dato}
    for year, datos in total_data["PIB_capita"].items()
    for dato in datos
])

# Show the first 10 rows of each DataFrame
print("Head of anual GDP table")
display(df_PIB_anual.head(10))
print("Head of GDP per capita table")
display(df_PIB_capita.head(10))

#Unify the dataframes
complete_df = pd.merge(df_PIB_anual, df_PIB_capita, on=["Año", "CCAA"], how="outer")
display(complete_df.head())

#Save the DataFrame to a CSV file
complete_df.to_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\running-trends-dataset.csv", index=False, sep=";")




