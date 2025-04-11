
import os
import pandas as pd

# === Combine all race files into a single dataset ===
def combine_runedia_races():
    folder_path = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\raw\runedia"
    expected_columns = ['dia', 'mes', 'titulo', 'enlace', 'localidad', 'tipo', 'distancia', 'provincia', 'año']
    all_dfs = []

    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            path = os.path.join(folder_path, file)
            try:
                df = pd.read_csv(path)
                if len(df.columns) == 1:
                    df = pd.read_csv(path, sep=";")
                if not df.empty and list(df.columns[:9]) == expected_columns:
                    all_dfs.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")

    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df = combined_df.drop_duplicates().dropna()

        output_path = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\processed\races_dataset.csv"
        combined_df.to_csv(output_path, index=False)
        print(f"Race dataset saved to: {output_path}")
    else:
        print("No valid race files found.")


# === Combine all socioeconomic data into a single dataset ===
def create_combined_powerbi_dataset():
    socio_path = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\processed\running_trends_cleaned_for_powerbi.csv"
    race_path = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\processed\races_dataset.csv"

    socio_df = pd.read_csv(socio_path, sep=",")
    race_df = pd.read_csv(race_path, sep=",")

    # Clean and align columns
    socio_df["CCAA"] = socio_df["CCAA"].str.strip().str.lower()
    race_df["provincia"] = race_df["provincia"].str.strip().str.lower()
    socio_df["Año"] = socio_df["Año"].astype(int)
    race_df["año"] = race_df["año"].astype(int)

    # Rename to join properly
    race_df = race_df.rename(columns={"provincia": "ccaa", "año": "Año"})

    # Count races per year and region
    race_counts = race_df.groupby(["Año", "ccaa"], as_index=False).size().rename(columns={"size": "num_carreras"})

    # Merge
    merged_df = pd.merge(socio_df, race_counts, how="left", left_on=["Año", "CCAA"], right_on=["Año", "ccaa"])
    merged_df["num_carreras"] = merged_df["num_carreras"].fillna(0).astype(int)
    merged_df = merged_df.drop(columns=["ccaa"])  # clean up duplicate

    # Save result
    output_path = r"C:\Users\evaru\Downloads\EVOLVE\python\running-trends\data\processed\powerbi_combined_dataset.csv"
    merged_df.to_csv(output_path, index=False)
    print(f" Combined Power BI dataset saved to: {output_path}")


if __name__ == "__main__":
    combine_runedia_races()
    create_combined_powerbi_dataset()
