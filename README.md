# EDA & Data Wrangling: Running Trends in Spain

## OVERVIEW

This project explores the evolution of **running** in Spain between **2000 and 2024**.  
The aim is to combine data from multiple sources to analyze trends and find relationships between **socioeconomic indicators** and **running interest or behavior**.

We explore the relationship between:
- **Economic indicators** (GDP, unemployment, and income levels)
- **Running indicators** (organized races and Google Trends interest)

We then validate or reject several hypotheses based on visualizations and statistics.

---

## LIBRARIES USED

- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `scikit-learn`
- `scipy`
- `beautifulsoup4`
- `requests`
- `os`

---

## HYPOTHESES

**Running: Habit or Trend?**

1. **Communities with greater purchasing power are more interested in running**

2. **Communities with higher unemployment rates are less interested in running**

3. **Regions with higher GDPs host more races**

---

## PROCESS

1. **Data Extraction**  
   - Web scraping from multiple sources (Runedia, Expansion Datosmacro, INE, Google Trends)
   - Saved in CSV format by province and year.

2. **Data Transformation & Cleaning**  
   - Harmonize province names across datasets  
   - Convert monetary/percentage values to numeric  
   - Merge datasets into a clean format

3. **Exploratory Data Analysis (EDA)**  
   - Remove outliers  
   - Normalize values  
   - Group variables into categories (High, Medium, Low)

4. **Visualizations**  
   - Time evolution graphs  
   - Scatter plots  
   - Histograms  
   - Group comparisons

5. **Power BI Dashboard**  
   - Dynamic visualizations to support insights  
   - Slicers for year and community filtering  
   - Maps and ranked bar charts for top-performing regions

---

## HYPOTHESIS EXAMPLES

### H1. Income vs Interest in Running 

We observe that communities with **higher average income** tend to have **higher running-related search scores** on Google. This is analyzed both at total and year-by-year levels.

We used scatter plots and line charts grouped by income categories (Low, Medium, High) to observe this relationship.

### H2. Unemployment vs Interest in Running 

By comparing **unemployment rates** and **Google Trends interest**, we noticed an inverse correlation:  
higher unemployment areas tend to show **lower interest** in running activities.

### H3. GDP vs Organized Races 

We aggregated race data from Runedia (per province and year), and compared it to GDP data.  
We find that wealthier regions (by average GDP) are often those organizing **more running races**.


---

## HOW TO RUN IT

1. Run `extraction.py` to collect data (Runedia, PIB, Google Trends, etc.)
2. Run `transformation.py` to merge and clean all datasets
3. Run `visualization.py` to generate the graphics used in the project
4. Use `powerbi_combined_dataset.csv` inside Power BI for dashboard design

---

## CONCLUSION

We find that **economic status influences running behavior**:
- More income or higher GDP → more running interest and organized events
- Higher unemployment → less running interest

This project shows how public data, web scraping, and visualization can help us discover behavioral patterns related to health and activity.

---

*Project developed as part of a Master's in Data Analytics*
