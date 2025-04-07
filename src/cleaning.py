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
display(df_PIB_anual.head(10))
display(df_PIB_capita.head(10))

#Unify the dataframes
complete_df = pd.merge(df_PIB_anual, df_PIB_capita, on=["Año", "CCAA"], how="outer")
display(complete_df.head())

#Convert columns PIB_anual and PIB_capita to numeric values
complete_df["PIB anual (€)"] = (
    complete_df["PIB anual (€)"]
    .astype(str)
    .str.replace("\xa0", "")  # Clean the spaces
    .str.replace("M€", "")  # Remove the "M€" suffix
    .str.replace(",", ".")  # Replace comma with dot
    .astype(float)  # Convert to float
)

complete_df["PIB per cápita (€)"] = (
    complete_df["PIB per cápita (€)"]
    .astype(str)
    .str.replace("\xa0", "")  
    .str.replace("€", "")  
    .str.replace(",", ".") 
    .astype(float) 
)

complete_df.info()

# Clean the "CCAA" column values
complete_df["CCAA"].unique()

#Modificar los nombres de las comunidades autónomas para que sean más legibles
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
})

display(complete_df.sample(15))

#Save the DataFrame to a CSV file
complete_df.to_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\running-trends-dataset.csv", index=False, sep=";")

# Clean the data from "Renta ESP file"
#Load the data
import pandas as pd
renta_df = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\raw\RentaESP-ccaa.csv", sep=";")

# Clean the data
renta_cleaned_df = renta_df.pivot_table(index=renta_df.columns[0], columns=renta_df.columns[1], values=renta_df.columns[3])

#Join the dataframe to our dataset 
'''(como no puedo visualizarlo, no sé si este código está ok) - OJO con el orden de los valores'''
# complete_df = renta_cleaned_df.merge(renta_cleaned_df, how='left', left_on='PIB_Capita', right_index=True)
# print(complete_df.head())

# Clean the data from "Tasa paro ESP file"
# Load the data
unemployment_df = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\raw\TasaParoESP-ccaa.csv", sep=";")
# Clean the data
column_ordered = ['Periodo', 'Comunidades y Ciudades Autónomas', 'Total', 'Edad', 'Sexo']
unemployment_df = unemployment_df[column_ordered]
unemployment_df['Periodo'] = unemployment_df['Periodo'].astype(str).str[:4]
unemployment_df = unemployment_df[unemployment_df['Sexo'] == 'Ambos sexos']
unemployment_df = unemployment_df[unemployment_df['Edad'] == 'Total']
unemployment_df['Total'] = unemployment_df['Total'].str.replace(',', '.').astype(float)
sum_by_period = unemployment_df.groupby(['Periodo', 'Comunidades y Ciudades Autónomas'])['Total'].sum().reset_index()
#Show the result
print(sum_by_period.head())

''' Ahora según el resultado que saquemos, tendremos que unirlo a nuestro dataset'''

# Extract the data from Google trends
# Extract the data from Runedia
# Clean the data from "Licencias ESP file"

