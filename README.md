# Databricks Auto Loader Pipeline

Automated data ingestion pipeline using Databricks Auto Loader.
Picks up CSV files from S3 landing zone and loads into Bronze Delta table.

## Architecture

```
UPSTREAM TEAM
  drops CSV files
       │
       ▼
s3://dinesh-databricks-delta/landing/
       │
       │ Databricks Job (9 PM IST daily)
       ▼
AUTO LOADER (cloudFiles)
  → Detects only NEW files (checkpoint tracking)
  → Skips already processed files
  → Transforms: adds revenue, ingested_at, source_file
       │
       ▼
s3://dinesh-databricks-delta/bronze/sales_data/
  (Delta Lake files in S3)
       │
       ▼
DELTA TABLE: deltalakeansh.bronze.sales_data
  (Queryable from Databricks SQL / Notebooks)
```

## Repository Structure

```
databricks-autoloader-pipeline/
├── databricks.yml                          ← Job definition (like CloudFormation)
├── DEPLOYMENT.md                           ← Full deployment guide
├── notebooks/
│   ├── setup/setup_catalog.py             ← Creates schema + table
│   ├── bronze/autoloader_bronze.py        ← Main Auto Loader pipeline
│   └── validation/validate_bronze.py      ← Data quality checks
├── infrastructure/
│   ├── 01_setup_schema.sql                ← Run once in Databricks
│   ├── 02_setup_table.sql                 ← Run once in Databricks
│   └── 03_validate_setup.sql              ← Verify setup
├── config/pipeline_config.py              ← All configuration
├── tests/
│   ├── test_autoloader.py                 ← Unit tests
│   └── sample_data/
│       ├── sales_20260509_001.csv         ← Test file 1
│       └── sales_20260510_001.csv         ← Test file 2
└── .github/workflows/deploy.yml           ← Auto deploy on git push
```

## Quick Start

```bash
# 1. Clone repo
git clone https://github.com/YOUR-USERNAME/databricks-autoloader-pipeline
cd databricks-autoloader-pipeline

# 2. Install Databricks CLI
pip install databricks-cli databricks-sdk

# 3. Configure CLI
databricks configure --token

# 4. Run SQL scripts in Databricks SQL Editor
#    (see DEPLOYMENT.md Step 7)

# 5. Deploy job
databricks bundle deploy --target prod

# 6. Upload test file to S3
aws s3 cp tests/sample_data/sales_20260509_001.csv \
  s3://dinesh-databricks-delta/landing/

# 7. Run job manually to test
#    Databricks → Jobs → AutoLoader_Bronze_Sales_Pipeline → Run now

# 8. Query results
#    SELECT * FROM deltalakeansh.bronze.sales_data;
```

## Full Deployment Guide

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step instructions.

## Tech Stack

- **Databricks** — Compute, Auto Loader, Delta Lake, Unity Catalog
- **AWS S3** — Data storage (landing zone + bronze layer)
- **Databricks Asset Bundles** — Infrastructure as Code (like CloudFormation)
- **GitHub Actions** — CI/CD (auto deploy on push to main)
- **Delta Lake** — ACID-compliant table format on S3
