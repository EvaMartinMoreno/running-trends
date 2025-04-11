# === RUNNING TRENDS - VISUALIZATION SCRIPT ===

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import pearsonr

# === Load dataset ===
df = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\running-trends-dataset.csv", sep=";")
df = df.drop_duplicates(subset=["Year", "CCAA"])

# === Remove Outliers ===
def remove_outliers(df, column):
    p5 = df[column].quantile(0.05)
    p95 = df[column].quantile(0.95)
    return df[(df[column] >= p5) & (df[column] <= p95)]

for col in ["Net_Income", "Unemployment_Rate", "Running_Searches"]:
    if col in df.columns:
        df = remove_outliers(df, col)

# === HYPOTHESIS 1: Income vs Running Searches ===
evolution = df.groupby("Year")[["Net_Income", "Running_Searches"]].mean().dropna()
scaler = MinMaxScaler()
evolution[["Net_Income", "Running_Searches"]] = scaler.fit_transform(evolution)

plt.figure(figsize=(12, 6))
sns.lineplot(data=evolution, x=evolution.index, y="Net_Income", label="Normalized Income")
sns.lineplot(data=evolution, x=evolution.index, y="Running_Searches", label="Normalized Searches")
plt.title("Evolution of Income vs Running Interest (2000–2024)")
plt.xlabel("Year")
plt.ylabel("Normalized Score")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("images/h1_income_vs_searches.png", dpi=300)
plt.show()

# Correlation check
mean_income = df.groupby("CCAA", as_index=False)["Net_Income"].mean()
mean_search = df.groupby("CCAA", as_index=False)["Running_Searches"].mean()
merged = pd.merge(mean_income, mean_search, on="CCAA")

corr, p = pearsonr(merged["Net_Income"], merged["Running_Searches"])
print(f"H1 Correlation Income vs Searches: {corr:.2f} (p-value: {p:.4f})")

# === HYPOTHESIS 2: Unemployment vs Running Searches ===
unemp_evolution = df.groupby("Year")[["Unemployment_Rate", "Running_Searches"]].mean().dropna()
unemp_evolution = pd.DataFrame(scaler.fit_transform(unemp_evolution), columns=unemp_evolution.columns, index=unemp_evolution.index)

plt.figure(figsize=(12, 6))
sns.lineplot(data=unemp_evolution, x=unemp_evolution.index, y="Unemployment_Rate", label="Normalized Unemployment")
sns.lineplot(data=unemp_evolution, x=unemp_evolution.index, y="Running_Searches", label="Normalized Running Searches")
plt.title("Evolution of Unemployment vs Running Interest (2000–2024)")
plt.xlabel("Year")
plt.ylabel("Normalized Score")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("images/h2_unemp_vs_searches.png", dpi=300)
plt.show()

# Correlation check
mean_unemp = df.groupby("CCAA", as_index=False)["Unemployment_Rate"].mean()
merged2 = pd.merge(mean_unemp, mean_search, on="CCAA")

corr, p = pearsonr(merged2["Unemployment_Rate"], merged2["Running_Searches"])
print(f"H2 Correlation Unemployment vs Searches: {corr:.2f} (p-value: {p:.4f})")

# === HYPOTHESIS 3: GDP vs Number of Races ===
races = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\raw\runedia\carreras_unidas.csv")
races["province"] = races["province"].str.lower().str.strip()
races["year"] = races["year"].astype(int)

race_counts = races.groupby("province", as_index=False).size().rename(columns={"province": "ccaa", "size": "total_races"})
df_pib = df.groupby("CCAA", as_index=False)["GDP_Total"].mean().rename(columns={"CCAA": "ccaa", "GDP_Total": "avg_gdp"})

merged3 = pd.merge(race_counts, df_pib, on="ccaa")

corr, p = pearsonr(merged3["avg_gdp"], merged3["total_races"])
print(f"H3 Correlation GDP vs Races: {corr:.2f} (p-value: {p:.4f})")

plt.figure(figsize=(10, 6))
sns.regplot(data=merged3, x="avg_gdp", y="total_races", scatter=True)
plt.title("Correlation between GDP and Total Races by CCAA")
plt.xlabel("Average GDP")
plt.ylabel("Total Races")
plt.grid(True)
plt.tight_layout()
plt.savefig("images/h3_gdp_vs_races.png", dpi=300)
plt.show()

# === HYPOTHESIS 4: Evolution of Race Types ===
races["type"] = races["type"].str.lower().str.strip()
type_counts = races["type"].value_counts().reset_index()
type_counts.columns = ["type", "count"]

plt.figure(figsize=(12, 6))
sns.barplot(data=type_counts.head(10), x="type", y="count", palette="magma")
plt.title("Top 10 Most Common Race Types")
plt.xlabel("Race Type")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("images/h4_race_types.png", dpi=300)
plt.show()

print("✅ All hypothesis visualizations generated!")
