import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import pearsonr

# === Load dataset ===
df = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\processed\powerbi_combined_dataset.csv", sep=",")
df = df.drop_duplicates(subset=["Año", "CCAA"])

# === REMOVE OUTLIERS (based on 5% and 95% percentiles) ===
def remove_outliers(df, column):
    p5 = df[column].quantile(0.05)
    p95 = df[column].quantile(0.95)
    return df[(df[column] >= p5) & (df[column] <= p95)]

for col in ["Renta neta media por persona", "Total_paro", "busquedas_running"]:
    df = remove_outliers(df, col)

# === H1: Higher income, more running interest ===
evolution = df.groupby("Año")[["Renta neta media por persona", "busquedas_running"]].mean().dropna()
scaler = MinMaxScaler()
evolution_scaled = pd.DataFrame(scaler.fit_transform(evolution), columns=evolution.columns, index=evolution.index)

plt.figure(figsize=(12, 6))
sns.lineplot(data=evolution_scaled, x=evolution_scaled.index, y="Renta neta media por persona", label="Income")
sns.lineplot(data=evolution_scaled, x=evolution_scaled.index, y="busquedas_running", label="Running searches")
plt.title("Normalized Income and Running Searches Evolution")
plt.xlabel("Year")
plt.ylabel("Normalized value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("C:/Users/evaru/Downloads/EVOLVE/python/running-trends/images/evolution_income_search.png", dpi=300)
plt.show()

# === Pearson Correlation for H1: Income vs Running Searches ===
corr_h1, pval_h1 = pearsonr(evolution["Renta neta media por persona"], evolution["busquedas_running"])
print(f"\n📈 H1 - Pearson correlation (Income vs Running searches): {corr_h1:.2f} (p-value: {pval_h1:.4f})")
if pval_h1 < 0.05:
    print("Podemos dar la hipótesis nula como válida (hay correlación significativa entre ingresos y búsquedas de running).")
else:
    print("No tenemos suficiente evidencia para invalidar el contrario a la hipótesis nula.")

# === H2: Higher unemployment, less interest in running ===
unemp_evolution = df.groupby("Año")[["Total_paro", "busquedas_running"]].mean().dropna()
unemp_scaled = pd.DataFrame(scaler.fit_transform(unemp_evolution), columns=unemp_evolution.columns, index=unemp_evolution.index)

plt.figure(figsize=(12, 6))
sns.lineplot(data=unemp_scaled, x=unemp_scaled.index, y="Total_paro", label="Unemployment")
sns.lineplot(data=unemp_scaled, x=unemp_scaled.index, y="busquedas_running", label="Running searches")
plt.title("Normalized Unemployment and Running Searches Evolution")
plt.xlabel("Year")
plt.ylabel("Normalized value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("C:/Users/evaru/Downloads/EVOLVE/python/running-trends/images/evolution_unemployment_search.png", dpi=300)
plt.show()

# === Pearson Correlation for H2: Unemployment vs Running Searches ===
corr_h2, pval_h2 = pearsonr(unemp_evolution["Total_paro"], unemp_evolution["busquedas_running"])
print(f"\n📉 H2 - Pearson correlation (Unemployment vs Running searches): {corr_h2:.2f} (p-value: {pval_h2:.4f})")
if pval_h2 < 0.05:
    print("Podemos dar la hipótesis nula como válida (hay correlación significativa entre desempleo y búsquedas de running).")
else:
    print("No tenemos suficiente evidencia para invalidar el contrario a la hipótesis nula.")

# === H3: Communities with higher GDP host more races ===
pib_avg = df.groupby("CCAA")["PIB_anual"].mean().reset_index()
race_total = df.groupby("CCAA")["num_carreras"].sum().reset_index()
merge_pib_races = pd.merge(pib_avg, race_total, on="CCAA")

plt.figure(figsize=(10, 6))
sns.regplot(data=merge_pib_races, x="PIB_anual", y="num_carreras", scatter=True, color='teal')
plt.title("Relation Between GDP and Number of Races")
plt.xlabel("Average GDP")
plt.ylabel("Total Races")
plt.grid(True)
plt.tight_layout()
plt.savefig("C:/Users/evaru/Downloads/EVOLVE/python/running-trends/images/h3_pib_vs_races.png", dpi=300)
plt.show()

corr_h3, pval_h3 = pearsonr(merge_pib_races["PIB_anual"], merge_pib_races["num_carreras"])
print(f"\n📊 H3 - Pearson correlation (GDP vs Total Races): {corr_h3:.2f} (p-value: {pval_h3:.4f})")
if pval_h3 < 0.05:
    print("Podemos dar la hipótesis nula como válida (hay correlación significativa entre PIB y número de carreras).")
else:
    print("No tenemos suficiente evidencia para invalidar el contrario a la hipótesis nula.")

# === H4: Race distribution behavior ===
carreras = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\processed\races_dataset.csv")
carreras["año"] = carreras["año"].astype(int)
carreras["provincia"] = carreras["provincia"].str.title()
carreras["tipo"] = carreras["tipo"].str.lower().str.strip()

# Evolution of total races per year
carreras_by_year = carreras.groupby("año").size().reset_index(name="total_carreras")
plt.figure(figsize=(12, 6))
sns.lineplot(data=carreras_by_year, x="año", y="total_carreras", marker="o")
plt.title("Number of Races in Spain (2000–2024)")
plt.xlabel("Year")
plt.ylabel("Total Races")
plt.grid(True)
plt.tight_layout()
plt.savefig("C:/Users/evaru/Downloads/EVOLVE/python/running-trends/images/h4_races_by_year.png", dpi=300)
plt.show()

# Top 10 race types
race_types = carreras["tipo"].value_counts().reset_index()
race_types.columns = ["tipo", "total"]
plt.figure(figsize=(10, 6))
sns.barplot(data=race_types.head(10), x="tipo", y="total", palette="magma")
plt.title("Top 10 Race Types")
plt.xlabel("Race Type")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("C:/Users/evaru/Downloads/EVOLVE/python/running-trends/images/h4_race_types.png", dpi=300)
plt.show()
