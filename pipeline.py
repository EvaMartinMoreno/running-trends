import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import pearsonr

# === Load dataset ===
df = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\running-trends-dataset.csv", sep=";")
df = df.drop_duplicates(subset=["Año", "CCAA"])

# === Remove outliers ===
def remove_outliers_iqr(data, column):
    q1 = data[column].quantile(0.25)
    q3 = data[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return data[(data[column] >= lower) & (data[column] <= upper)]

for col in ["Renta neta media por persona", "Total_paro", "busquedas_running"]:
    df = remove_outliers_iqr(df, col)

# === H1: Income vs Running Searches ===
evolution = df.groupby("Año")[["Renta neta media por persona", "busquedas_running"]].mean().dropna()
scaler = MinMaxScaler()
evolution.loc[:, ["Renta neta media por persona", "busquedas_running"]] = scaler.fit_transform(evolution)

plt.figure(figsize=(12, 6))
sns.lineplot(data=evolution, x=evolution.index, y="Renta neta media por persona", label="Normalized Income")
sns.lineplot(data=evolution, x=evolution.index, y="busquedas_running", label="Normalized Searches")
plt.title("Normalized Evolution: Income vs Running Searches")
plt.xlabel("Year")
plt.ylabel("Normalized Value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\images\img1.png", dpi=300)
plt.close()

mean_income = df.groupby("CCAA", as_index=False)["Renta neta media por persona"].mean()
q1_income = mean_income["Renta neta media por persona"].quantile(0.25)
q3_income = mean_income["Renta neta media por persona"].quantile(0.75)

mean_income["Income_Group"] = mean_income["Renta neta media por persona"].apply(
    lambda x: "Low" if x < q1_income else ("High" if x > q3_income else "Medium")
)

mean_search = df.groupby("CCAA", as_index=False)["busquedas_running"].mean()
q1_search = mean_search["busquedas_running"].quantile(0.25)
q3_search = mean_search["busquedas_running"].quantile(0.75)

mean_search["Search_Group"] = mean_search["busquedas_running"].apply(
    lambda x: "Low" if x < q1_search else ("High" if x > q3_search else "Medium")
)

merged = pd.merge(mean_income, mean_search, on="CCAA")
corr_income, pval_income = pearsonr(merged["Renta neta media por persona"], merged["busquedas_running"])

print(f"Income vs Searches Correlation: r = {corr_income:.2f}, p = {pval_income:.4f}")

# === H2: Unemployment vs Running Searches ===
mean_unemp = df.groupby("CCAA", as_index=False)["Total_paro"].mean()
q1_unemp = mean_unemp["Total_paro"].quantile(0.25)
q3_unemp = mean_unemp["Total_paro"].quantile(0.75)

mean_unemp["Unemp_Group"] = mean_unemp["Total_paro"].apply(
    lambda x: "Low" if x < q1_unemp else ("High" if x > q3_unemp else "Medium")
)

df_unemp = pd.merge(mean_unemp, mean_search, on="CCAA")
corr_unemp, pval_unemp = pearsonr(df_unemp["Total_paro"], df_unemp["busquedas_running"])

print(f"Unemployment vs Searches Correlation: r = {corr_unemp:.2f}, p = {pval_unemp:.4f}")

# === Save final dataset for Power BI ===
quartiles = {
    "Income_Group": ("Renta neta media por persona", q1_income, q3_income),
    "Unemp_Group": ("Total_paro", q1_unemp, q3_unemp),
    "Search_Group": ("busquedas_running", q1_search, q3_search),
}

def classify(row, col, q1, q3):
    val = row[col]
    if val < q1:
        return "Low"
    elif val > q3:
        return "High"
    return "Medium"

for group, (col, q1, q3) in quartiles.items():
    df[group] = df.apply(lambda row: classify(row, col, q1, q3), axis=1)

output_path = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\processed\running_trends_cleaned_for_powerbi.csv"
df.to_csv(output_path, index=False)
print(f"✅ Clean CSV saved to {output_path}")
