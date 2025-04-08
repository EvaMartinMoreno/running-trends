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

#Function to normalize CCAA names in all our dataframes
complete_df["CCAA"] = complete_df["CCAA"].replace({
    "Andalucía [+]": "Andalucia",
    "Aragón [+]": "Aragon",
    "Asturias [+]": "Asturias",
    "Canarias [+]": "Canarias", 
    "Cantabria [+]": "Cantabria",
    "Castilla y León [+]": "CastillaLeon",
    "Castilla-La Mancha [+]": "CastillaLaMancha",
    "Cataluña [+]": "Catalunya",
    "Ceuta [+]": "Ceuta",
    "Comunidad Valenciana [+]": "ComunidadValenciana",
    "Comunidad de Madrid [+]": "Madrid",
    "Extremadura [+]": "Extremadura",
    "Galicia [+]": "Galicia",
    "Islas Baleares [+]": "Baleares",
    "La Rioja [+]": "LaRioja",
    "Melilla [+]": "Melilla",
    "Navarra [+]": "Navarra",
    "País Vasco [+]": "PaisVasco",
    "Región de Murcia [+]": "Murcia",
    "Total Nacional" : "Total_Nacional"
})

#Convert columns PIB_anual and PIB_capita to numeric values
complete_df["PIB_anual"] = (
    complete_df["PIB_anual"]
    .astype(str)
    .str.replace("\xa0", "")  # Clean the spaces
    .str.replace("M€", "")  # Remove the "M€" suffix
    .str.replace(",", ".")  # Replace comma with dot
    .astype(float)  # Convert to float
)

complete_df["PIB_capita"] = (
    complete_df["PIB_capita"]
    .astype(str)
    .str.replace("\xa0", "")  
    .str.replace("€", "")  
    .str.replace(",", ".") 
    .astype(float) 
)

print("Basic info of PIB table created:")
complete_df.info()

print("Sample values:")
display(complete_df.sample(15))

#Save the DataFrame to a CSV file
complete_df.to_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\running-trends-dataset.csv", index=False, sep=";")

# Clean the data from "Renta ESP file"
renta_df = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\raw\RentaESP-ccaa.csv", sep=";")
renta_df.info()
display(renta_df.head())
renta_df.iloc[:, 1].unique()

# We have to transpose this dataframe to extract the data we need
pivoted_renta_df = renta_df.pivot(
    index=["Periodo", "Comunidades y Ciudades Autónomas"], 
    columns="Renta anual neta media por persona y por unidad de consumo",
    values="Total"
).reset_index()

# Rename columns to match the column in complete_df
pivoted_renta_df = pivoted_renta_df.rename(columns={
    "Periodo": "Año",
    "Comunidades y Ciudades Autónomas": "CCAA"
})

# Rename our columns to coincide with the dataset (running-data)
pivoted_renta_df["CCAA"] = pivoted_renta_df["CCAA"].replace({
    "01 Andalucía": "Andalucia",
    "02 Aragón": "Aragon",
    "03 Asturias, Principado de": "Asturias",
    "05 Canarias": "Canarias", 
    "06 Cantabria": "Cantabria",
    "07 Castilla y León": "CastillaLeon",
    "08 Castilla - La Mancha": "CastillaLaMancha",
    "09 Cataluña": "Catalunya",
    "18 Ceuta": "Ceuta",
    "10 Comunitat Valenciana": "ComunidadValenciana",
    "13 Madrid, Comunidad de": "Madrid",
    "11 Extremadura": "Extremadura",
    "12 Galicia": "Galicia",
    "04 Balears, Illes": "Baleares",
    "17 Rioja, La": "LaRioja",
    "19 Melilla": "Melilla",
    "15 Navarra, Comunidad Foral de": "Navarra",
    "16 País Vasco": "PaisVasco",
    "14 Murcia, Región de": "Murcia",
    "Total Nacional" : "Total_Nacional"
})

pivoted_renta_df = pivoted_renta_df.sort_values(by="Año", ascending=False)
display(pivoted_renta_df.head())

# Join the data
complete_df = pd.merge(complete_df, pivoted_renta_df, on=["Año", "CCAA"], how="left")
print("This is our dataset now")
display(complete_df.sample(10))


# Clean the data from "Tasa paro ESP file"
# Load the data
import pandas as pd
unemployment_df = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\raw\TasaParoESP-ccaa.csv", sep=";")
unemployment_df.info()
display(unemployment_df.head())

# Clean the data
column_ordered = ['Periodo', 'Comunidades y Ciudades Autónomas', 'Total', 'Edad', 'Sexo']
unemployment_df = unemployment_df[column_ordered]
unemployment_df['Periodo'] = unemployment_df['Periodo'].astype(str).str[:4]
unemployment_df = unemployment_df[unemployment_df['Sexo'] == 'Ambos sexos']
unemployment_df = unemployment_df[unemployment_df['Edad'] == 'Total']
unemployment_df['Total'] = unemployment_df['Total'].astype(str).str.replace(',', '.').astype(float)
unemployment_df = unemployment_df.rename(
    columns={'Comunidades y Ciudades Autónomas': 'CCAA',
             "Periodo": "Año",
             "Total" : "Total_paro"}
)

#Function to normalize CCAA names in all our dataframes
unemployment_df["CCAA"] = unemployment_df["CCAA"].replace({
    "01 Andalucía": "Andalucia",
    "02 Aragón": "Aragon",
    "03 Asturias, Principado de": "Asturias",
    "05 Canarias": "Canarias", 
    "06 Cantabria": "Cantabria",
    "07 Castilla y León": "CastillaLeon",
    "08 Castilla - La Mancha": "CastillaLaMancha",
    "09 Cataluña": "Catalunya",
    "18 Ceuta": "Ceuta",
    "10 Comunitat Valenciana": "ComunidadValenciana",
    "13 Madrid, Comunidad de": "Madrid",
    "11 Extremadura": "Extremadura",
    "12 Galicia": "Galicia",
    "04 Balears, Illes": "Baleares",
    "17 Rioja, La": "LaRioja",
    "19 Melilla": "Melilla",
    "15 Navarra, Comunidad Foral de": "Navarra",
    "16 País Vasco": "PaisVasco",
    "14 Murcia, Región de": "Murcia",
    "Total Nacional" : "Total_Nacional"
})

unemployment_df.groupby(['Año', 'CCAA'])['Total_paro'].sum().reset_index()
unemployment_df["Año"] = unemployment_df["Año"].astype(int)
complete_df["Año"] = complete_df["Año"].astype(int)
print(unemployment_df)

# Join the data to our dataset (running-trends)
complete_df = pd.merge(complete_df, unemployment_df[["Año", "CCAA", "Total_paro"]], on=["Año", "CCAA"], how="left")
display(complete_df.sample(10))

# Clean the google trends data
import os
import pandas as pd

# Path where your Google Trends CSVs are stored
folder_csv = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\raw\google-trends"

# Store cleaned DataFrames
dfs = []

# Load and clean all CSVs
for file in os.listdir(folder_csv):
    if file.endswith(".csv"):
        year = os.path.splitext(file)[0]  # Extract year from filename
        path = os.path.join(folder_csv, file)

        # Skip the first row (header info), then set proper headers
        df = pd.read_csv(path, skiprows=1)

        # Ensure correct column names
        df.columns = ["Región", "Busqueda_running"]
        df["Año"] = int(year)
        dfs.append(df)
        print(f" df_{year} loaded.")

# Combine all years into a single DataFrame
df_running_completo = pd.concat(dfs, ignore_index=True)

# Convert to wide format (one row per region, columns per year)
df_running_pivot = df_running_completo.pivot(
    index="Región",
    columns="Año",
    values="Busqueda_running"
)

# Rename columns like "busquedas_2004"
df_running_pivot.columns = [f"busquedas_{col}" for col in df_running_pivot.columns]
df_running_pivot = df_running_pivot.reset_index()

# Convert back to long format for merging
df_running_long = df_running_pivot.melt(
    id_vars="Región",
    var_name="Año",
    value_name="busquedas_running"
)

# Extract numeric year
df_running_long["Año"] = df_running_long["Año"].str.extract(r'(\d{4})').astype(int)

# Rename and normalize region names
df_running_long = df_running_long.rename(columns={"Región": "CCAA"})
df_running_long["CCAA"] = df_running_long["CCAA"].replace({
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

# Join this data to our running-trends dataset
complete_df = pd.merge(complete_df, df_running_long, on=["Año", "CCAA"], how="left")

# Final check
print("Final dataset with running searches added:")
display(complete_df.sample(10))

# Extract the data from Runediagi
# Clean the data from "Licencias ESP file"

