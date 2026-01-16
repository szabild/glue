# Capstone Project

Created by: `Levente Zádor` | Neptun Code: `JPANZP`

> **Task description:**<br>
> Go to the Data Engineering AWS Course (AWS Academy Data Engineering [136964])
> and launch the Capstone Project Lab. <br> Please solve the assignments written there.<br>
> Create one or more Markdown files to document the following:
>
> - The goal of the project
> - Steps taken
> - Executed code
> - Detailed explanations and interpretations of the outputs
> - In addition to the queries specified in the lab, create and analyze three of your own.

## Goal of the Project

The goal of this capstone project is to build a data engineering solution on AWS to host and analyze large datasets about global fisheries. The solution shows a real-world scenario where the data is used by analysts to create reports. The project includes creating an infrastructure from ingesting raw CSV data, transformation into optimized format, using AWS Glue and performing queries using Amazon Athena.

## Steps taken

### Initial Setup

- Created an EC2 environment named `CapstoneIDE`
- Created S3 buckets, one for raw/processed data and one for Athena query results
- 3 CSV files were downloaded to the local IDE
- Transformation included converting CSV files to Parquet using Python
- Uploaded Parquet files to S3 `data-source` bucket

```bash
wget https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/CUR-TF-200-ACDENG-1-91570/lab-capstone/S3/SAU-GLOBAL-1-v48-0.csv
wget https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/CUR-TF-200-ACDENG-1-91570/lab-capstone/S3/SAU-HighSeas-71-v48-0.csv
wget https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/CUR-TF-200-ACDENG-1-91570/lab-capstone/S3/SAU-EEZ-242-v48-0.csv
```

> Downloading CSVs

```python
import pandas as pd
# Read the CSV
df = pd.read_csv('SAU-GLOBAL-1-v48-0.csv')
# Write to Parquet
df.to_parquet('SAU-GLOBAL-1-v48-0.parquet')
```

> Converting File

### Crawling Data

- AWS Glue Crawler was created named `fishcrawler` pointing to S3 data bucket. The crawler populated the AWS Glue Data Catalog database (`fishdb`)
- Athena configured to query the fishdb database
- Created first view named `MackerelsCatch`, which can simplify repeated analysis

```sql
SELECT year, fishing_entity AS Country,
CAST(CAST(SUM(landed_value) AS DOUBLE) AS DECIMAL(38,2)) AS ValuePacificWCSeasCatch
FROM fishdb.data_source_40312
WHERE area_name LIKE '%Pacific%' AND fishing_entity = 'Fiji' AND year > 2000
GROUP BY year, fishing_entity
ORDER BY year;
```

> Analyze High Seas Catch by Fiji

```sql
CREATE OR REPLACE VIEW MackerelsCatch AS
SELECT year, area_name AS WhereCaught, fishing_entity as Country, SUM(tonnes) AS TotalWeight
FROM fishdb.data_source_40312
WHERE common_name LIKE '%Mackerels%' AND year > 2014
GROUP BY year, area_name, fishing_entity
ORDER BY TotalWeight DESC;
```

> Create View for Mackerel Analysis

### Data Transformation

- The third file contained columns which did not match the existing schema
- Used Pandas to rename these columns
- Re-ran the Glue Crawler to update metadata
- Ran queries to verify data integrity

```python
import pandas as pd
df = pd.read_csv('SAU-EEZ-242-v48-0.csv')

# Renaming columns to match existing schema
df.rename(columns = {"fish_name": "common_name", "country": "fishing_entity"}, inplace = True)

# Save as Parquet
df.to_parquet('SAU-EEZ-242-v48-0.parquet')
```

> Renaming columns

## Own Queries

### Biggest Catches

#### Goal of the query:

Get the largest catches (by weight) recorded in the database

```sql
SELECT year, fishing_entity, common_name, tonnes
FROM fishdb.data_source_40312
ORDER BY tonnes DESC
LIMIT 10;
```

- All top 10 records belong to **Peru**
- The largest catch happened in **1970** with approximately **12.3 million tonnes**

| Rank | Year | Fishing Entity | Tonnes     |
| :--- | :--- | :------------- | :--------- |
| 1    | 1970 | Peru           | 12,290,707 |
| 2    | 1994 | Peru           | 11,327,317 |
| 3    | 1971 | Peru           | 10,282,316 |
| 4    | 1968 | Peru           | 10,272,481 |
| 5    | 1967 | Peru           | 9,839,207  |
| 6    | 2000 | Peru           | 9,817,110  |
| 7    | 1969 | Peru           | 8,970,329  |
| 8    | 1964 | Peru           | 8,871,576  |
| 9    | 2004 | Peru           | 8,803,547  |
| 10   | 1996 | Peru           | 8,703,442  |

### Sharks

#### Goal of the query:

Get data regarding shark fishing to analyze the volume (tonne) across different areas and time

```sql
SELECT year, area_name, common_name, tonnes
FROM fishdb.data_source_40312
WHERE common_name LIKE '%Shark%'
```

The query results return `684 records`, mainly functional groups: `"Sharks, rays, skates"` and `"Sharks, rays, chimaeras"`. Geographically these catches are in two areas: `Pacific, Western Central` and `Fiji`. The peak is in `1991` for around `8895 tonnes`.

![Shark Query Results In Excel](shark.png)

### Countries in the Database

#### Goal of the query:

List all unique fishing entities (countries), that are in the dataset.

```sql
SELECT DISTINCT fishing_entity
FROM fishdb.data_source_40312
ORDER BY fishing_entity;
```

- `Unknown Fishing Country` indicates that there are records where fishing entity could not be identified
- The query returned **198** unique fishing entities
- AS expected there are no land-locked countries in the query result, like Hungary
