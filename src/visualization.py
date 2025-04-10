import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import pearsonr

# === Load dataset ===
df = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\running-trends-dataset.csv", sep=";")
df = df.drop_duplicates(subset=["Año", "CCAA"])

# === REMOVE OUTLIERS for robustness (based on 5%–95% percentiles) ===
def remove_outliers(df, column):
    p5 = df[column].quantile(0.05)
    p95 = df[column].quantile(0.95)
    return df[(df[column] >= p5) & (df[column] <= p95)]

df = remove_outliers(df, "Renta neta media por persona")
df = remove_outliers(df, "Total_paro")
df = remove_outliers(df, "busquedas_running")

# === H1: Communities with greater purchasing power are more interested in running ===
# 1. Normalized evolution of income and searches
evolution = df.groupby("Año")[["Renta neta media por persona", "busquedas_running"]].mean().dropna()
scaler = MinMaxScaler()
evolution[["Renta neta media por persona", "busquedas_running"]] = scaler.fit_transform(evolution)

plt.figure(figsize=(12, 6))
sns.lineplot(data=evolution, x=evolution.index, y="Renta neta media por persona", label="Normalized Income", linewidth=2)
sns.lineplot(data=evolution, x=evolution.index, y="busquedas_running", label="Normalized Searches", linewidth=2)
plt.title("Normalized Evolution of Income and 'Running' Searches in Spain (2004–2024)")
plt.xlabel("Year")
plt.ylabel("Normalized Value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\images\img1.png", dpi=300, bbox_inches='tight')
print("✅ Graphic saved: img1")
plt.show()

# 2. Distribution of average income per region
mean_income = df.groupby("CCAA", as_index=False)["Renta neta media por persona"].mean()
mean_val = mean_income["Renta neta media por persona"].mean()
median = mean_income["Renta neta media por persona"].median()
mode = mean_income["Renta neta media por persona"].mode()[0]

plt.figure(figsize=(10, 6))
sns.histplot(mean_income["Renta neta media por persona"], bins=10, kde=True, color='skyblue')
plt.axvline(mean_val, color='red', linestyle='--', label=f"Mean: {mean_val:.0f}€")
plt.axvline(median, color='green', linestyle='--', label=f"Median: {median:.0f}€")
plt.axvline(mode, color='purple', linestyle='--', label=f"Mode: {mode:.0f}€")
plt.title("Income Distribution by Region (2000–2024)")
plt.xlabel("Net Income (€)")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\images\img2.png", dpi=300, bbox_inches='tight')
print("✅ Graphic saved: img2")
plt.show()

# 3. Group regions by income
q1 = mean_income["Renta neta media por persona"].quantile(0.25)
q3 = mean_income["Renta neta media por persona"].quantile(0.75)

def classify_income(val):
    if val < q1:
        return "Low"
    elif val > q3:
        return "High"
    else:
        return "Medium"

mean_income["Income_Group"] = mean_income["Renta neta media por persona"].apply(classify_income)

# 4. Group regions by search score
mean_search = df.groupby("CCAA", as_index=False)["busquedas_running"].mean()
q1_s = mean_search["busquedas_running"].quantile(0.25)
q3_s = mean_search["busquedas_running"].quantile(0.75)

def classify_search(val):
    if val < q1_s:
        return "Low"
    elif val > q3_s:
        return "High"
    else:
        return "Medium"

mean_search["Search_Group"] = mean_search["busquedas_running"].apply(classify_search)

# 5. Merge both
merged = pd.merge(mean_income, mean_search, on="CCAA")

# 6. Correlation between income and searches
corr, p_val = pearsonr(merged["Renta neta media por persona"], merged["busquedas_running"])
print("\n📈 Pearson Correlation: Income vs Running")
print(f"Correlation: {corr:.2f}, p-value: {p_val:.4f}")
print("✅ Significant" if p_val < 0.05 else "⚠️ Not significant")

# 7. Evolution by group
income_group_df = df.merge(mean_income[["CCAA", "Income_Group"]], on="CCAA")

plt.figure(figsize=(12, 6))
sns.lineplot(data=income_group_df, x="Año", y="busquedas_running", hue="Income_Group", estimator="mean")
plt.title("Running Searches by Income Group (2004–2024)")
plt.xlabel("Year")
plt.ylabel("Average Search Score")
plt.grid(True)
plt.tight_layout()
plt.savefig(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\images\img4.png", dpi=300, bbox_inches='tight')
print("✅ Graphic saved: img4")
plt.show()

# === H2: Communities with the highest unemployment are less interested in running ===
# 1. Normalized evolution of unemployment rate and running searches
unemp_evolution = df.groupby("Año")[["Total_paro", "busquedas_running"]].mean().dropna()
scaler = MinMaxScaler()
unemp_evolution[["Total_paro", "busquedas_running"]] = scaler.fit_transform(unemp_evolution)

plt.figure(figsize=(12, 6))
sns.lineplot(data=unemp_evolution, x=unemp_evolution.index, y="Total_paro", label="Normalized Unemployment", linewidth=2)
sns.lineplot(data=unemp_evolution, x=unemp_evolution.index, y="busquedas_running", label="Normalized Running Searches", linewidth=2)
plt.title("Normalized Evolution of Unemployment Rate and Running Searches (2004–2024)")
plt.xlabel("Year")
plt.ylabel("Normalized Value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\images\img5.png", dpi=300, bbox_inches='tight')
print("✅ Graphic saved: img5")
plt.show()

# 2. Distribution of average unemployment rate by region
mean_unemp_stats = df.groupby("CCAA", as_index=False)["Total_paro"].mean()
mean_val_unemp = mean_unemp_stats["Total_paro"].mean()
median_unemp = mean_unemp_stats["Total_paro"].median()
mode_unemp = mean_unemp_stats["Total_paro"].mode()[0]
q1_unemp = mean_unemp_stats["Total_paro"].quantile(0.25)
q3_unemp = mean_unemp_stats["Total_paro"].quantile(0.75)

# Print stats
print("\n📊 Unemployment Statistics (2000–2024)")
print(f"Mean: {mean_val_unemp:.2f}%")
print(f"Median: {median_unemp:.2f}%")
print(f"Mode: {mode_unemp:.2f}%")
print(f"Q1: {q1_unemp:.2f}%")
print(f"Q3: {q3_unemp:.2f}%")

# Group unemployment
def classify_unemployment_group(rate):
    if rate < q1_unemp:
        return "Low"
    elif rate > q3_unemp:
        return "High"
    else:
        return "Medium"

mean_unemp_stats["Unemp_Group"] = mean_unemp_stats["Total_paro"].apply(classify_unemployment_group)
mean_search_unemp = df.groupby("CCAA", as_index=False)["busquedas_running"].mean()
df_h2_grouped = pd.merge(mean_unemp_stats, mean_search_unemp, on="CCAA")

# Correlation Unemployment vs Searches
x = df_h2_grouped["Total_paro"]
y = df_h2_grouped["busquedas_running"]
corr, p_val = pearsonr(x, y)

print("\n📉 Pearson Correlation: Unemployment vs Running Searches")
print(f"Correlation: {corr:.2f}, p-value: {p_val:.4f}")
print("✅ Significant" if p_val < 0.05 else "⚠️ Not significant")

# 3. Lineplot by group
df_unemp_evol = df.merge(mean_unemp_stats[["CCAA", "Unemp_Group"]], on="CCAA")

plt.figure(figsize=(12, 6))
sns.lineplot(data=df_unemp_evol, x="Año", y="busquedas_running", hue="Unemp_Group", estimator="mean")
plt.title("Running Searches by Unemployment Group (2004–2024)")
plt.xlabel("Year")
plt.ylabel("Google Trends Score")
plt.grid(True)
plt.tight_layout()
plt.savefig(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\images\img8.png", dpi=300, bbox_inches='tight')
print("✅ Graphic saved: img8")
plt.show()

# === Load dataset ===
powerbi_cleaned = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\running-trends-dataset.csv", sep=";")
powerbi_cleaned = powerbi_cleaned.drop_duplicates(subset=["Año", "CCAA"]).copy()

# === Drop missing values in relevant columns ===
powerbi_cleaned.dropna(subset=["Renta neta media por persona", "Total_paro", "busquedas_running"])

# === Remove outliers using IQR method ===
def remove_outliers_iqr(data, column):
    q1 = data[column].quantile(0.25)
    q3 = data[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return data[(data[column] >= lower) & (data[column] <= upper)]

powerbi_cleaned = remove_outliers_iqr(powerbi_cleaned, "Renta neta media por persona")
powerbi_cleaned = remove_outliers_iqr(powerbi_cleaned, "Total_paro")
powerbi_cleaned = remove_outliers_iqr(powerbi_cleaned, "busquedas_running")

# === Clasificación por año ===
# Cuartiles por año
q_income = powerbi_cleaned.groupby("Año")["Renta neta media por persona"].quantile([0.25, 0.75]).unstack()
q_unemp = powerbi_cleaned.groupby("Año")["Total_paro"].quantile([0.25, 0.75]).unstack()
q_search = powerbi_cleaned.groupby("Año")["busquedas_running"].quantile([0.25, 0.75]).unstack()

# Clasificación por grupos
def classify_by_quartiles(row, q, col):
    if row[col] < q.loc[row["Año"], 0.25]:
        return "Low"
    elif row[col] > q.loc[row["Año"], 0.75]:
        return "High"
    else:
        return "Medium"

powerbi_cleaned["Income_Group"] = powerbi_cleaned.apply(lambda row: classify_by_quartiles(row, q_income, "Renta neta media por persona"), axis=1)
powerbi_cleaned["Unemp_Group"] = powerbi_cleaned.apply(lambda row: classify_by_quartiles(row, q_unemp, "Total_paro"), axis=1)
powerbi_cleaned["Search_Group"] = powerbi_cleaned.apply(lambda row: classify_by_quartiles(row, q_search, "busquedas_running"), axis=1)

# === Save final clean CSV for Power BI ===
output_path = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\processed\running_trends_cleaned_for_powerbi.csv"
powerbi_cleaned.to_csv(output_path, index=False)
print("✅ CSV with group classification and cleaned data saved to:")
print(output_path)


# === H3: Communities with the highest GPD are potential running races organizators ===
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

# === 1. Cargar datasets ===
# Carreras scrapeadas (ya unidas)
df_carreras = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\raw\runedia\carreras_unidas.csv")

# Dataset original con el PIB
df_pib = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\processed\running_trends_cleaned_for_powerBI.csv", sep=",")
df_pib = df_pib.drop_duplicates(subset=["Año", "CCAA"])

# === 2. Procesar: número de carreras por CCAA ===
carreras_por_ccaa = df_carreras.groupby("provincia").size().reset_index(name="num_carreras")

# Normalizar nombre de provincias si hace falta (ej: valencia -> Comunidad Valenciana)
carreras_por_ccaa["provincia"] = carreras_por_ccaa["provincia"].str.lower().str.replace("-", " ").str.strip()

# Mapeo de provincias a CCAA oficial (si es necesario)
# Aquí puedes adaptar según tus provincias exactas
mapa_ccaa = {
    "valencia": "Comunidad Valenciana",
    "catalunya": "Catalunya",
    "madrid": "Madrid",
    "euskadi": "Pais Vasco",
    "illes balears": "Baleares",
    "castilla la mancha": "CastillaLaMancha",
    "castilla y leon": "CastillaLeon",
    "la rioja": "LaRioja",
    "andalucia": "Andalucia",
    "galicia": "Galicia",
    "navarra": "Navarra",
    "murcia": "Murcia",
    "cantabria": "Cantabria",
    "asturias": "Asturias",
    "aragon": "Aragon",
    "canarias": "Canarias",
    "extremadura": "Extremadura",
    "melilla": "Melilla",
    "ceuta": "Ceuta"
}
carreras_por_ccaa["CCAA"] = carreras_por_ccaa["provincia"].map(mapa_ccaa)

# === 3. PIB medio por comunidad autónoma ===
pib_promedio = df_pib.groupby("CCAA", as_index=False)["PIB_anual"].mean()

# === 4. Merge ambos datasets ===
df_h3 = pd.merge(carreras_por_ccaa, pib_promedio, on="CCAA")

# === 5. Gráfico de dispersión ===
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_h3, x="PIB_anual", y="num_carreras", hue="CCAA")
sns.regplot(data=df_h3, x="PIB_anual", y="num_carreras", scatter=False, color="red")
plt.title("Número de carreras vs PIB por Comunidad Autónoma")
plt.xlabel("PIB Medio Anual (€)")
plt.ylabel("Número de Carreras")
plt.grid(True)
plt.tight_layout()
plt.savefig(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\images\img_h3_correlacion_pib_carreras.png", dpi=300)
plt.show()

# === 6. Correlación ===
corr, pval = pearsonr(df_h3["PIB_anual"], df_h3["num_carreras"])
print(f"\n📊 Correlación PIB ↔ Número de carreras")
print(f"Coeficiente de correlación: {corr:.2f}")
print(f"P-value: {pval:.4f}")
if pval < 0.05:
    print("✅ Correlación estadísticamente significativa.")
else:
    print("⚠️ No es significativa.")
