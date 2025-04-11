import os
import pandas as pd

# === 1. LOAD GDP DATA ===
gdp_path = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\running-trends-dataset.csv"
df = pd.read_csv(gdp_path, sep=";")

# === 2. CLEAN GDP COLUMNS ===
df["PIB_anual"] = (
    df["PIB_anual"]
    .astype(str)
    .str.replace("\xa0", "")
    .str.replace("M€", "")
    .str.replace(",", ".")
    .astype(float)
)

df["PIB_capita"] = (
    df["PIB_capita"]
    .astype(str)
    .str.replace("\xa0", "")
    .str.replace("€", "")
    .str.replace(",", ".")
    .astype(float)
)

# === 3. LOAD AND TRANSFORM INCOME DATA ===
income_path = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\raw\RentaESP-ccaa.csv"
income_df = pd.read_csv(income_path, sep=";")

pivoted_income_df = income_df.pivot(
    index=["Periodo", "Comunidades y Ciudades Autónomas"],
    columns="Renta anual neta media por persona y por unidad de consumo",
    values="Total"
).reset_index()

pivoted_income_df = pivoted_income_df.rename(columns={
    "Periodo": "Año",
    "Comunidades y Ciudades Autónomas": "CCAA"
})

pivoted_income_df["CCAA"] = pivoted_income_df["CCAA"].replace({
    "01 Andalucía": "Andalucia",
    "02 Aragón": "Aragon",
    "03 Asturias, Principado de": "Asturias",
    "05 Canarias": "Canarias",
    "06 Cantabria": "Cantabria",
    "07 Castilla y León": "CastillaLeon",
    "08 Castilla - La Mancha": "CastillaLaMancha",
    "09 Cataluña": "Catalunya",
    "10 Comunitat Valenciana": "ComunidadValenciana",
    "13 Madrid, Comunidad de": "Madrid",
    "11 Extremadura": "Extremadura",
    "12 Galicia": "Galicia",
    "04 Balears, Illes": "Baleares",
    "17 Rioja, La": "LaRioja",
    "19 Melilla": "Melilla",
    "15 Navarra, Comunidad Foral de": "Navarra",
    "16 País Vasco": "PaisVasco",
    "18 Ceuta": "Ceuta",
    "14 Murcia, Región de": "Murcia",
    "Total Nacional": "Total_Nacional"
})

pivoted_income_df["Año"] = pivoted_income_df["Año"].astype(int)
df = pd.merge(df, pivoted_income_df, on=["Año", "CCAA"], how="left")

# === 4. LOAD AND CLEAN UNEMPLOYMENT DATA ===
unemployment_path = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\raw\TasaParoESP-ccaa.csv"
unemployment_df = pd.read_csv(unemployment_path, sep=";")
unemployment_df = unemployment_df[(unemployment_df["Sexo"] == "Ambos sexos") & (unemployment_df["Edad"] == "Total")]

unemployment_df = unemployment_df.rename(columns={
    "Periodo": "Año",
    "Comunidades y Ciudades Autónomas": "CCAA",
    "Total": "Total_paro"
})

unemployment_df["Total_paro"] = unemployment_df["Total_paro"].astype(str).str.replace(",", ".").astype(float)
unemployment_df["Año"] = unemployment_df["Año"].astype(str).str[:4].astype(int)

unemployment_df["CCAA"] = unemployment_df["CCAA"].replace(pivoted_income_df["CCAA"].to_dict())
df = pd.merge(df, unemployment_df[["Año", "CCAA", "Total_paro"]], on=["Año", "CCAA"], how="left")

# === 5. LOAD AND MERGE GOOGLE TRENDS DATA ===
google_folder = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\raw\google-trends"
all_trends = []

for file in os.listdir(google_folder):
    if file.endswith(".csv"):
        year = os.path.splitext(file)[0]
        path = os.path.join(google_folder, file)
        trends_df = pd.read_csv(path, skiprows=1)
        trends_df.columns = ["CCAA", "Busqueda_running"]
        trends_df["Año"] = int(year)
        all_trends.append(trends_df)

df_trends = pd.concat(all_trends, ignore_index=True)

df_trends["CCAA"] = df_trends["CCAA"].replace({
    "Andalucía": "Andalucia",
    "Aragón": "Aragon",
    "Principado de Asturias": "Asturias",
    "Castilla y León": "CastillaLeon",
    "Castilla-La Mancha": "CastillaLaMancha",
    "Cataluña": "Catalunya",
    "Comunidad Valenciana": "ComunidadValenciana",
    "Comunidad de Madrid": "Madrid",
    "Islas Baleares": "Baleares",
    "La Rioja": "LaRioja",
    "País Vasco": "PaisVasco",
    "Región de Murcia": "Murcia",
    "Canarias": "Canarias",
    "Cantabria": "Cantabria",
    "Ceuta": "Ceuta",
    "Extremadura": "Extremadura",
    "Galicia": "Galicia",
    "Melilla": "Melilla",
    "Navarra": "Navarra"
})

df = pd.merge(df, df_trends, on=["Año", "CCAA"], how="left")

# === 6. EXPORT FINAL CLEANED DATASET ===
output_path = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\processed\running_trends_cleaned_for_powerbi.csv"
df.to_csv(output_path, index=False, sep=";")
print(f"\n✅ Final dataset saved to: {output_path}")
