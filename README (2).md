# 📦 Brazilian E‑Commerce End‑to‑End Analytics Pipeline

**Kaggle → CSV → Meltano → BigQuery → dbt → Machine Learning → HTML
Dashboard**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Meltano](https://img.shields.io/badge/Meltano-ELT-orange)
![BigQuery](https://img.shields.io/badge/BigQuery-Cloud-green)
![dbt](https://img.shields.io/badge/dbt-Transformations-red)
![ML](https://img.shields.io/badge/Machine%20Learning-Predictive-purple)
![HTML](https://img.shields.io/badge/Dashboard-HTML-yellowgreen)

------------------------------------------------------------------------

## ✅ Project Objectives

This project demonstrates a **production‑ready data engineering +
analytics workflow**:

✅ Download Kaggle datasets automatically\
✅ Store raw CSV safely\
✅ Load into BigQuery using Meltano\
✅ Verify CSV row counts match BigQuery\
✅ Transform data using dbt\
✅ Apply Machine Learning for prediction\
✅ Build HTML dashboards for business users

------------------------------------------------------------------------

## 📁 Project Structure

    meltano_kaggle_csv/
    │
    ├── data/
    ├── meltano.yml
    ├── download_kaggle.py
    ├── check_all_csvs.py
    ├── dbt/
    ├── ml/
    ├── dashboard/
    ├── .env
    ├── .gitignore
    └── README.md

------------------------------------------------------------------------

## 🐍 1. Conda Environment

``` bash
conda env create -f eltn_environment.yml
conda activate eltn
```

------------------------------------------------------------------------

## 🔑 2. Kaggle API Key Setup

1.  Go to: https://www.kaggle.com/settings\
2.  Click **Create New API Token**
3.  Download `kaggle.json`

------------------------------------------------------------------------

## 🧪 3. Setup `.env`

``` env
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_key
GCP_PROJECT_ID=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=/home/user/bq-key.json
```

------------------------------------------------------------------------

## 🛑 4. Setup `.gitignore`

``` gitignore
.env
*.json
.meltano/
data/*.csv
__pycache__/
```

------------------------------------------------------------------------

## ⬇️ 5. Download Kaggle CSVs

``` bash
python download_kaggle.py
```

------------------------------------------------------------------------

## ☁️ 6. Generate BigQuery Service Account

Create a Service Account with BigQuery Admin role and download JSON key.

------------------------------------------------------------------------

## 🔄 7. Initialize Meltano

``` bash
meltano init meltano_kaggle_csv
cd meltano_kaggle_csv
```

------------------------------------------------------------------------

## 🔌 8. Add Plugins

``` bash
meltano add extractor tap-csv
meltano add loader target-bigquery
```

------------------------------------------------------------------------

## ▶️ 9. Run Data Pipeline

``` bash
meltano run tap-csv target-bigquery
```

------------------------------------------------------------------------

## 🔍 10. Validate CSV vs BigQuery

``` bash
python check_all_csvs.py
```

------------------------------------------------------------------------

## 🧱 11. dbt Transformations

``` bash
pip install dbt-bigquery
dbt init olist_dbt
```

------------------------------------------------------------------------

## 🤖 12. Machine Learning Use Cases

-   Delivery Delay Prediction
-   Customer Lifetime Value
-   Review Sentiment Analysis

------------------------------------------------------------------------

## 📊 13. HTML Dashboard

Built using Chart.js & static exports.

------------------------------------------------------------------------

## 👔 Resume‑Ready Summary

> Built a full cloud‑based data engineering pipeline with Meltano,
> BigQuery, dbt, ML, and dashboards.

------------------------------------------------------------------------
