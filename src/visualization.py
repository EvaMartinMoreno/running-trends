import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import pearsonr

# === Load dataset ===
df = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\running-trends-dataset.csv", sep=";")
df = df.drop_duplicates(subset=["Año", "CCAA"])

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

# 6. Plot average searches by income group
group_search = merged.groupby("Income_Group", as_index=False)["busquedas_running"].mean()

plt.figure(figsize=(8, 6))
sns.barplot(data=group_search, x="Income_Group", y="busquedas_running", palette="viridis", order=["High", "Medium", "Low"])
plt.title("Average Running Searches by Income Group")
plt.xlabel("Income Group")
plt.ylabel("Google Trends Score")
plt.grid(axis="y")
plt.tight_layout()
plt.show()

# 7. Correlation between income and searches
corr, p_val = pearsonr(merged["Renta neta media por persona"], merged["busquedas_running"])
print("\n📈 Pearson Correlation: Income vs Running")
print(f"Correlation: {corr:.2f}, p-value: {p_val:.4f}")
print("✅ Significant" if p_val < 0.05 else "⚠️ Not significant")

# 8. Evolution by group
income_group_df = df.merge(mean_income[["CCAA", "Income_Group"]], on="CCAA")

plt.figure(figsize=(12, 6))
sns.lineplot(data=income_group_df, x="Año", y="busquedas_running", hue="Income_Group", estimator="mean")
plt.title("Running Searches by Income Group (2004–2024)")
plt.xlabel("Year")
plt.ylabel("Average Search Score")
plt.grid(True)
plt.tight_layout()
plt.show()

# === H2: Communities with the highest unemployment are less interested in running ===

# === H2 extra: Evolution and distribution of Unemployment and Running Interest ===

# 1. Normalized evolution of unemployment rate and running searches
unemp_evolution = df.groupby("Año")[["Total_paro", "busquedas_running"]].mean().dropna()

# Normalization
scaler = MinMaxScaler()
unemp_evolution[["Total_paro", "busquedas_running"]] = scaler.fit_transform(unemp_evolution)

# Plot normalized evolution
plt.figure(figsize=(12, 6))
sns.lineplot(data=unemp_evolution, x=unemp_evolution.index, y="Total_paro", label="Normalized Unemployment", linewidth=2)
sns.lineplot(data=unemp_evolution, x=unemp_evolution.index, y="busquedas_running", label="Normalized Running Searches", linewidth=2)
plt.title("Normalized Evolution of Unemployment Rate and Running Searches (2004–2024)")
plt.xlabel("Year")
plt.ylabel("Normalized Value (0 - 1)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# 2. Distribution of average unemployment rate by region
mean_unemp_stats = df.groupby("CCAA", as_index=False)["Total_paro"].mean()
mean_val_unemp = mean_unemp_stats["Total_paro"].mean()
median_unemp = mean_unemp_stats["Total_paro"].median()
mode_unemp = mean_unemp_stats["Total_paro"].mode()[0]
q1_unemp = mean_unemp_stats["Total_paro"].quantile(0.25)
q3_unemp = mean_unemp_stats["Total_paro"].quantile(0.75)

# Print statistics
print("\n📊 Unemployment Statistics (2000–2024)")
print(f"Mean: {mean_val_unemp:.2f}%")
print(f"Median: {median_unemp:.2f}%")
print(f"Mode: {mode_unemp:.2f}%")
print(f"Q1: {q1_unemp:.2f}%")
print(f"Q3: {q3_unemp:.2f}%")

# Plot distribution
plt.figure(figsize=(10, 6))
sns.histplot(mean_unemp_stats["Total_paro"], bins=10, kde=True, color='salmon')
plt.axvline(mean_val_unemp, color='red', linestyle='--', label=f"Mean: {mean_val_unemp:.2f}%")
plt.axvline(median_unemp, color='green', linestyle='--', label=f"Median: {median_unemp:.2f}%")
plt.axvline(mode_unemp, color='purple', linestyle='--', label=f"Mode: {mode_unemp:.2f}%")
plt.title("Unemployment Rate Distribution by Region (2000–2024)")
plt.xlabel("Unemployment Rate (%)")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === H2 continuation: Grouping regions by unemployment level ===

# Usamos los cuartiles ya calculados: q1_unemp, q3_unemp

def classify_unemployment_group(rate):
    if rate < q1_unemp:
        return "Low"
    elif rate > q3_unemp:
        return "High"
    else:
        return "Medium"

mean_unemp_stats["Unemp_Group"] = mean_unemp_stats["Total_paro"].apply(classify_unemployment_group)

# Agrupamos también búsquedas medias
mean_search_unemp = df.groupby("CCAA", as_index=False)["busquedas_running"].mean()

# Unimos ambas tablas
df_h2_grouped = pd.merge(mean_unemp_stats, mean_search_unemp, on="CCAA")

# === 1. Gráfico de barras: Búsquedas medias por grupo de desempleo ===
search_by_unemp_group = df_h2_grouped.groupby("Unemp_Group", as_index=False)["busquedas_running"].mean()

plt.figure(figsize=(8, 6))
sns.barplot(data=search_by_unemp_group, x="Unemp_Group", y="busquedas_running", palette="coolwarm", order=["High", "Medium", "Low"])
plt.title("Average 'Running' Searches by Unemployment Group")
plt.xlabel("Unemployment Group")
plt.ylabel("Google Trends Score")
plt.grid(axis="y")
plt.tight_layout()
plt.show()

# === 2. Correlación entre tasa de paro y búsquedas ===
x = df_h2_grouped["Total_paro"]
y = df_h2_grouped["busquedas_running"]
corr, p_val = pearsonr(x, y)

print("\n📉 Pearson Correlation: Unemployment vs Running Searches")
print(f"Correlation: {corr:.2f}, p-value: {p_val:.4f}")
if p_val < 0.05:
    print("✅ Statistically significant correlation.")
else:
    print("⚠️ Correlation is not statistically significant.")

# === 3. Evolución temporal de búsquedas por grupo de desempleo ===

# Añadimos el grupo al dataset original
df_unemp_evol = df.merge(mean_unemp_stats[["CCAA", "Unemp_Group"]], on="CCAA")

# Gráfico de evolución
plt.figure(figsize=(12, 6))
sns.lineplot(data=df_unemp_evol, x="Año", y="busquedas_running", hue="Unemp_Group", estimator="mean")
plt.title("Evolution of 'Running' Searches by Unemployment Group (2004–2024)")
plt.xlabel("Year")
plt.ylabel("Google Trends Score")
plt.grid(True)
plt.tight_layout()
plt.show()


# === FULL YEARLY DATASET for Power BI ===

# 1. Clasificamos los grupos de renta por año
q1_income = df.groupby("Año")["Renta neta media por persona"].quantile(0.25)
q3_income = df.groupby("Año")["Renta neta media por persona"].quantile(0.75)

def classify_income_row(row):
    year = row["Año"]
    val = row["Renta neta media por persona"]
    if val < q1_income[year]:
        return "Low"
    elif val > q3_income[year]:
        return "High"
    else:
        return "Medium"

# 2. Clasificamos el grupo de desempleo por año
q1_unemp = df.groupby("Año")["Total_paro"].quantile(0.25)
q3_unemp = df.groupby("Año")["Total_paro"].quantile(0.75)

def classify_unemp_row(row):
    year = row["Año"]
    val = row["Total_paro"]
    if val < q1_unemp[year]:
        return "Low"
    elif val > q3_unemp[year]:
        return "High"
    else:
        return "Medium"

# 3. Clasificamos el grupo de búsquedas por año
q1_search = df.groupby("Año")["busquedas_running"].quantile(0.25)
q3_search = df.groupby("Año")["busquedas_running"].quantile(0.75)

def classify_search_row(row):
    year = row["Año"]
    val = row["busquedas_running"]
    if val < q1_search[year]:
        return "Low"
    elif val > q3_search[year]:
        return "High"
    else:
        return "Medium"

# 4. Creamos nuevo DataFrame para exportar
df_powerbi = df[[
    "Año", "CCAA", 
    "Renta neta media por persona", 
    "Total_paro", 
    "busquedas_running"
]].dropna()

# 5. Aplicamos clasificaciones
df_powerbi["Income_Group"] = df_powerbi.apply(classify_income_row, axis=1)
df_powerbi["Unemp_Group"] = df_powerbi.apply(classify_unemp_row, axis=1)
df_powerbi["Search_Group"] = df_powerbi.apply(classify_search_row, axis=1)

# 6. Guardar en CSV
df_powerbi.to_csv("C:/Users/evaru/Downloads/EVOLVE/python/running-trends/data/processed/running_trends_evolution_dataset.csv", index=False)
print("✅ Archivo 'running_trends_evolution_dataset.csv' creado correctamente con todos los años.")
