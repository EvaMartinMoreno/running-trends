import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import pearsonr

#**Visualization**
#H1: Communities with greater purchasing power are more interested in running*
# Load dataset
df = pd.read_csv(r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\running-trends-dataset.csv", sep=";")
df = df.drop_duplicates(subset=["Año", "CCAA"])

# === 1. Normalized Evolution of Income and Google Searches ===
evolution = df.groupby("Año")[["Renta neta media por persona", "busquedas_running"]].mean().dropna()
scaler = MinMaxScaler()
evolution[["Renta neta media por persona", "busquedas_running"]] = scaler.fit_transform(evolution)

plt.figure(figsize=(12, 6))
sns.lineplot(data=evolution, x=evolution.index, y="Renta neta media por persona", label="Normalized Income", linewidth=2)
sns.lineplot(data=evolution, x=evolution.index, y="busquedas_running", label="Normalized Searches", linewidth=2)
plt.title("Normalized Evolution of Income and 'Running' Searches in Spain (2004–2024)")
plt.xlabel("Year")
plt.ylabel("Normalized Value (0 - 1)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# === 2. Income Distribution and Stats ===
mean_income = df.groupby("CCAA", as_index=False)["Renta neta media por persona"].mean()
mean_val = mean_income["Renta neta media por persona"].mean()
median = mean_income["Renta neta media por persona"].median()
mode = mean_income["Renta neta media por persona"].mode()[0]
quantiles = mean_income["Renta neta media por persona"].quantile([0.25, 0.5, 0.75])

print(f"Mean: {mean_val:.2f} €")
print(f"Median: {median:.2f} €")
print(f"Mode: {mode:.2f} €")
print("Quartiles:")
print(quantiles)

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

# === 3. Group Regions by Income Level ===
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

# === 4. Group Regions by Search Volume ===
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

# === 5. Merge Income + Search ===
merged = pd.merge(mean_income, mean_search, on="CCAA")

# === 6. Plot Searches by Income Group ===
search_group_mean = merged.groupby("Income_Group", as_index=False)["busquedas_running"].mean()

plt.figure(figsize=(8, 6))
sns.barplot(data=search_group_mean, x="Income_Group", y="busquedas_running", palette="viridis", order=["High", "Medium", "Low"])
plt.title("Average 'Running' Searches by Income Group")
plt.xlabel("Income Group")
plt.ylabel("Average Google Trends Score")
plt.grid(axis="y")
plt.tight_layout()
plt.show()

# === 7. Pearson Correlation ===
x = merged["Renta neta media por persona"]
y = merged["busquedas_running"]
correlation, p_value = pearsonr(x, y)

print("\n📈 Pearson Correlation Analysis")
print(f"Correlation coefficient (r): {correlation:.2f}")
print(f"P-value: {p_value:.4f}")
if p_value < 0.05:
    print("✅ Statistically significant correlation.")
else:
    print("⚠️ No statistically significant correlation.")


#*H2.Communities with the highest unemployment are less interested in running*
# === Hypothesis 2: Communities with the highest unemployment are less interested in running ===

# 1. Calculate the average unemployment rate and running search interest by region
avg_unemployment = df.groupby("CCAA", as_index=False)["Total_paro"].mean()
avg_searches = df.groupby("CCAA", as_index=False)["busquedas_running"].mean()

# 2. Merge both metrics
df_h2 = pd.merge(avg_unemployment, avg_searches, on="CCAA")

# 3. Classify regions based on unemployment level using quartiles
q1 = df_h2["Total_paro"].quantile(0.25)
q3 = df_h2["Total_paro"].quantile(0.75)

def classify_unemployment(val):
    if val < q1:
        return "Low"
    elif val > q3:
        return "High"
    else:
        return "Medium"

df_h2["Unemployment_Group"] = df_h2["Total_paro"].apply(classify_unemployment)

# 4. Plot average Google search score per unemployment group
grouped_search = df_h2.groupby("Unemployment_Group", as_index=False)["busquedas_running"].mean()

plt.figure(figsize=(8, 6))
sns.barplot(data=grouped_search, x="Unemployment_Group", y="busquedas_running", palette="coolwarm", order=["High", "Medium", "Low"])
plt.title("Average 'Running' Search Score by Unemployment Group")
plt.xlabel("Unemployment Group")
plt.ylabel("Average Google Trends Score")
plt.grid(axis="y")
plt.tight_layout()
plt.show()

# 5. Pearson correlation between unemployment and search interest
x = df_h2["Total_paro"]
y = df_h2["busquedas_running"]
correlation, p_value = pearsonr(x, y)

# 6. Print correlation results
print("\n📈 Pearson Correlation: Unemployment vs. Running Interest")
print(f"Correlation coefficient (r): {correlation:.2f}")
print(f"P-value: {p_value:.4f}")

if p_value < 0.05:
    print("✅ Statistically significant correlation.")
else:
    print("⚠️ Correlation is not statistically significant.")
