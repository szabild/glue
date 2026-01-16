# AWS Academy Data Engineering Capstone: Global Fishery Impact Analysis

## 1. Project Goal
The goal of this project was to build a data lake and analytics pipeline to investigate the impact of global fishing across three distinct maritime zones: **Open Seas**, **Specific High Seas Areas**, and **Exclusive Economic Zones (EEZs)**. 

The project demonstrates the ability to:
* Set up a cloud-based development environment (Cloud9).
* Perform local data engineering (Pandas) to clean and convert legacy CSV data into high-performance **Apache Parquet** format.
* Automate schema discovery using **AWS Glue**.
* Perform serverless SQL analytics on big data using **Amazon Athena**.

---

## 2. Architecture Overview
The pipeline follows a modern Data Lake architecture:
1. **Compute:** AWS Cloud9 (IDE) used for data preparation and CLI operations.
2. **Storage:** Amazon S3 (Data Source and Query Results).
3. **ETL & Cataloging:** AWS Glue Crawlers and Data Catalog.
4. **Analytics:** Amazon Athena (Presto-based SQL engine).



---

## 3. Steps Taken

### Phase 1: Environment Setup & Data Prep
* **IDE Configuration:** Launched an AWS Cloud9 environment inside a custom VPC.
* **Bucket Creation:** Provisioned two S3 buckets: `data-source-40627` for the Parquet files and `query-results-20046` for Athena logs.
* **Data Ingestion:** Downloaded three datasets from the "Sea Around Us" repository (Global, High Seas, and Fiji EEZ).
* **Local Transformation:** Used Python (Pandas) to convert raw CSVs to Parquet. This step included renaming mismatched columns (`fish_name` -> `common_name` and `country` -> `fishing_entity`) to ensure schema uniformity.

### Phase 2: Schema Discovery
* **Data Cataloging:** Configured an AWS Glue database (`fishdb`) and a Crawler (`fishcrawler`).
* **Crawler Execution:** Ran the crawler to scan S3. The crawler successfully identified the union of all schemas across the three files, handling both shared and unique columns.

### Phase 3: SQL Analytics
* **Validation:** Verified the data using `SELECT DISTINCT` on area names.
* **Reporting:** Calculated fishery values (in 2010 USD) for Fiji across different zones.
* **Optimization:** Created an Athena **View** (`MackerelsCatch`) to simplify complex aggregation for specific species.

---

## 4. Executed Code


```wget https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/CUR-TF-200-ACDENG-1-91570/lab-capstone/s3/SAU-GLOBAL-1-v48-0.csv
wget https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/CUR-TF-200-ACDENG-1-91570/lab-capstone/s3/SAU-HighSeas-71-v48-0.csv
wget https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/CUR-TF-200-ACDENG-1-91570/lab-capstone/s3/SAU-EEZ-242-v48-0.csv
head -6 SAU-GLOBAL-1-v48-0.csv
sudo pip3 install pandas pyarrow fastparquet
python3
import pandas as pd
df = pd.read_csv('SAU-GLOBAL-1-v48-0.csv')
df.to_parquet('SAU-GLOBAL-1-v48-0.parquet')
exit()
aws s3 cp /home/ec2-user/environment/SAU-GLOBAL-1-v48-0.parquet s3://data-source-40627
head -6 SAU-HighSeas-71-v48-0.csv
rm SAU-HighSeas-71-v48-0.csv
wget https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/CUR-TF-200-ACDENG-1-91570/lab-capstone/s3/SAU-HighSeas-71-v48-0.csv
python3
import pandas as pd
df = pd.read_csv('SAU-HighSeas-71-v48-0.csv')
df.to_parquet('SAU-HighSeas-71-v48-0.csv')
exit()
aws s3 cp /home/ec2-user/environment/SAU-HighSeas-71-v48-0.parquet s3://data-source-40627
cp SAU-EEZ-242-v48-0.csv SAU-EEZ-242-v48-0-old.csv
python3
import pandas as pd
data_location = 'SAU-EEZ-242-v48-0-old.csv'
df = pd.read_csv(data_location)
print(df.head(1))
df.rename(columns = {"fish_name": "common_name", "country": "fishing_entity"}, inplace = True) 
print(df.head(1))
df.to_csv('SAU-EEZ-242-v48-0.csv', header=True, index=False)
df.to_parquet('SAU-EEZ-242-v48-0.parquet')
exit()
aws s3 cp /home/ec2-user/environment/SAU-EEZ-242-v48-0.parquet s3://data-source-40627
```
---
## 5. Detailed Explanations and Interpretations of Outputs


### A. Data Format Transformation (CSV to Parquet)
* **Observation:** The original dataset was in CSV format (row-based). After processing in Cloud9, it was converted to Apache Parquet (columnar-based).
* **Interpretation:** This is a critical optimization. Parquet stores data by column rather than by row. When Athena runs a query like `SELECT SUM(landed_value)`, it only has to read the data in the `landed_value` column, ignoring the others. This reduces **S3 data scanning costs** and increases **query speed** by up to 90% compared to querying the raw CSV.

### B. Glue Crawler & Schema Inference
* **Observation:** The Glue Crawler created a single table even though there were three different files with slightly different columns.
* **Interpretation:** AWS Glue successfully performed "Schema Evolution." It recognized that while the `HighSeas` file had an `area_name` and the `Global` file did not, they could exist in the same table. The missing data in the Global file was correctly marked as `NULL`. This allows data analysts to query all maritime zones simultaneously using a single SQL endpoint.

### C. Fiji Fishery Impact Analysis (Athena Output)
* **Observation:** The query for Fiji's catch in the EEZ vs. Open Seas showed distinct totals that, when added together, matched the combined query.
* **Interpretation:** This confirms **Data Integrity**. 
    * **ValueOpenSeasCatch:** Represents fishing in international waters (Area Name is NULL).
    * **ValueEEZCatch:** Represents fishing within 200 miles of the Fiji coast (Area Name LIKE '%Fiji%').
* **Business Insight:** By comparing these two values, the organization can determine if Fiji’s fishing industry is more dependent on local coastal resources or international high-seas activity.

### D. The MackerelsCatch View
* **Observation:** The view filtered data for the species "Mackerels" for years > 2014 and sorted them by weight.
* **Interpretation:** * **Data Abstraction:** Using a `VIEW` allows us to hide the complex `CAST` and `JOIN` logic from the end user. A business analyst only needs to run `SELECT * FROM MackerelsCatch` without knowing the underlying SQL.
    * **Top Performers:** The output identified which "fishing entities" (countries) have the highest impact on Mackerel populations. For example, if China appears at the top of the list with the highest `TotalWeight`, it indicates their fleet is the primary driver of Mackerel extraction in those specific zones.

### E. Interpretation of the `CAST` functions
* **Observation:** The SQL used `CAST(CAST(SUM(landed_value) AS DOUBLE) AS DECIMAL(38,2))`.
* **Interpretation:** Raw scientific data often outputs in "E notation" (e.g., 1.5E7). By casting the data to `DECIMAL(38,2)`, we transformed the output into a human-readable "Dollars and Cents" format. This ensures the data is "Boardroom Ready" for non-technical stakeholders.

## 6. 3 Queries of my own

### Query 1: Economic Market Leaders in Western Central Pacific
**Goal:** Identify the top 5 countries by total landed value (USD) in the 'Pacific, Western Central' area.

| Rank | Country | Total Value (USD - Scientific) | Interpretation |
| :--- | :--- | :--- | :--- |
| 1 | Japan | 8.248E11 | Primary economic stakeholder in the region. |
| 2 | Indonesia | 7.505E11 | Significant regional competitor. |
| 3 | Philippines | 2.506E11 | Strong mid-tier industrial impact. |
| 4 | South Korea | 2.026E11 | Major distant-water fishing fleet presence. |
| 5 | USA | 1.670E11 | Key Western presence in Pacific high-seas. |

**Analysis:**
The output shows that **Japan** and **Indonesia** are the dominant economic forces in the Western Central Pacific, with Japan leading at over **$824 Billion** (total cumulative value). The presence of scientific notation (E11) indicates the massive scale of these fisheries. From a data engineering perspective, this confirms the `landed_value` column was successfully aggregated across the different Parquet files.

---

### Query 2: Biodiversity Count (Species Richness)
**Goal:** Compare the variety of species (Common Names) across different maritime zones.

| Area Name | Distinct Species Count |
| :--- | :--- |
| **Fiji** | 98 |
| **Pacific, Western Central** | 23 |

**Analysis:**
The results reveal a significant difference in biodiversity reporting. **Fiji (EEZ)** shows **98 distinct species**, while the **Pacific, Western Central (High Seas)** only shows **23**. 
* **Interpretation:** This suggests that coastal EEZ areas are either more biologically diverse or, more likely, have stricter reporting requirements for specific species compared to international high-seas areas.

---

### Query 3: Peak Productivity Year for Fiji
**Goal:** Find the single most productive year for Fiji in the 21st century.

**Output:**
* **Year:** 2017
* **Total Weight:** 82,815.98 tonnes



**Analysis:**
The query identifies **2017** as the peak year for Fiji’s fishing industry within this dataset. 
* **Industrial Scale:** A harvest of nearly **83,000 tonnes** in a single year represents a high point in fleet efficiency and resource availability. 
* **Business Insight:** This "Peak Harvest" serves as a benchmark for Fiji. Analysts can use this 2017 data to set future quotas and compare environmental conditions (like El Niño cycles) that may have contributed to such a successful year.