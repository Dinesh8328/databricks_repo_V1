# DEPLOYMENT GUIDE
# Step-by-Step Instructions to Deploy the Pipeline

## Overview

```
WHAT THIS GUIDE DOES:
─────────────────────
Step 1-3:  One-time setup (do this once)
Step 4:    Push code to GitHub
Step 5-6:  Deploy to Databricks
Step 7:    Test the pipeline
Step 8:    Verify everything works
Step 9:    Ongoing operation
```

---

## PREREQUISITES

Before starting, make sure you have:
- GitHub account
- Databricks workspace access: https://dbc-6cfad-58be.cloud.databricks.com
- AWS S3 bucket configured: dinesh-databricks-delta
- External Location set up in Databricks (pointing to S3 bucket)
- IAM Role configured: databricks-s3-role

---

## STEP 1: GENERATE DATABRICKS TOKEN

```
1. Go to: https://dbc-6cfad-58be.cloud.databricks.com
2. Click your profile icon (top right corner)
3. Click "Settings"
4. Click "Developer" (left sidebar)
5. Click "Access tokens"
6. Click "Generate new token"
7. Name: deployment-token
8. Expiry: 90 days
9. Click "Generate"
10. COPY THE TOKEN — you won't see it again!
    Example: YOUR-DATABRICKS-TOKEN-HERE
```

---

## STEP 2: CREATE GITHUB REPOSITORY

```
1. Go to: https://github.com
2. Click "+" (top right) → "New repository"
3. Repository name: databricks-autoloader-pipeline
4. Visibility: Private
5. Click "Create repository"
6. Note the repository URL:
   https://github.com/YOUR-USERNAME/databricks-autoloader-pipeline
```

---

## STEP 3: ADD GITHUB SECRETS

```
1. Go to your GitHub repository
2. Click "Settings" tab
3. Click "Secrets and variables" → "Actions"
4. Click "New repository secret"

Add Secret 1:
  Name:  DATABRICKS_HOST
  Value: https://dbc-6cfad-58be.cloud.databricks.com
  Click "Add secret"

Add Secret 2:
  Name:  DATABRICKS_TOKEN
  Value: (paste the token from Step 1)
  Click "Add secret"

You should now see 2 secrets listed.
```

---

## STEP 4: PUSH CODE TO GITHUB

Open terminal on your laptop and run:

```bash
# 1. Clone the project files
# (Download files from wherever you received them)

# 2. Initialize Git in the project folder
cd databricks-autoloader-project
git init

# 3. Add remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/databricks-autoloader-pipeline.git

# 4. Add all files
git add .

# 5. Commit
git commit -m "feat: initial databricks auto loader pipeline"

# 6. Push to GitHub
git branch -M main
git push -u origin main
```

After this, go to GitHub and verify all files are there.

---

## STEP 5: INSTALL DATABRICKS CLI ON YOUR LAPTOP

```bash
# Install Databricks CLI
pip install databricks-cli
pip install databricks-sdk

# Verify installation
databricks --version
```

---

## STEP 6: CONFIGURE DATABRICKS CLI

```bash
# Configure with your token
databricks configure --token

# It will ask:
Databricks Host: https://dbc-6cfad-58be.cloud.databricks.com
Token: (paste your token from Step 1)

# Verify connection
databricks workspace list /
```

---

## STEP 7: RUN INFRASTRUCTURE SQL SCRIPTS

This creates the schema and Delta table in Databricks.

```
1. Open Databricks workspace:
   https://dbc-6cfad-58be.cloud.databricks.com

2. Click "SQL Editor" (left sidebar)

3. Run 01_setup_schema.sql:
   Copy contents of infrastructure/01_setup_schema.sql
   Paste in SQL Editor
   Click "Run"
   Expected: "deltalakeansh.bronze" appears in catalog

4. Run 02_setup_table.sql:
   Copy contents of infrastructure/02_setup_table.sql
   Paste in SQL Editor
   Click "Run"
   Expected: Table created at s3://dinesh-databricks-delta/bronze/sales_data/

5. Run 03_validate_setup.sql:
   Copy contents of infrastructure/03_validate_setup.sql
   Paste in SQL Editor
   Click "Run"
   Expected: All queries return results without errors
```

---

## STEP 8: DEPLOY JOB TO DATABRICKS

From your laptop terminal, in the project folder:

```bash
# Go to project folder
cd databricks-autoloader-project

# Validate the bundle (checks for errors)
databricks bundle validate

# Expected output:
# Name: sales-autoloader-pipeline
# Target: prod
# Workspace: https://dbc-6cfad-58be.cloud.databricks.com
# Bundle is valid!

# Deploy to Databricks PROD
databricks bundle deploy --target prod

# Expected output:
# Uploading bundle files to /Users/...
# Deploying resources...
# Updating deployment state...
# Bundle deployed successfully!
```

---

## STEP 9: VERIFY JOB IN DATABRICKS UI

```
1. Go to: https://dbc-6cfad-58be.cloud.databricks.com
2. Click "Jobs & Pipelines" (left sidebar)
3. You should see: "AutoLoader_Bronze_Sales_Pipeline"
4. Click on it
5. Verify:
   ✅ Schedule shows: Daily at 9:00 PM IST
   ✅ 3 tasks visible:
      - setup_infrastructure
      - run_autoloader
      - validate_data
   ✅ Email notifications configured
```

---

## STEP 10: TEST THE PIPELINE

### Upload Sample File to S3

```
Method 1: AWS Console
  1. Go to: https://console.aws.amazon.com/s3
  2. Open bucket: dinesh-databricks-delta
  3. Click "Create folder" → name: landing
  4. Open the landing folder
  5. Click "Upload"
  6. Upload file: tests/sample_data/sales_20260509_001.csv
  7. Click "Upload"

Method 2: AWS CLI
  aws s3 cp tests/sample_data/sales_20260509_001.csv \
    s3://dinesh-databricks-delta/landing/
```

### Run the Job Manually

```
1. In Databricks → Jobs & Pipelines
2. Click: AutoLoader_Bronze_Sales_Pipeline
3. Click: "Run now"
4. Watch the tasks execute:
   ✅ setup_infrastructure  → Running → Success
   ✅ run_autoloader        → Running → Success
   ✅ validate_data         → Running → Success
```

### Verify Data in Bronze Table

```sql
-- Run in Databricks SQL Editor:

-- Check row count
SELECT COUNT(*) as total_rows
FROM deltalakeansh.bronze.sales_data;
-- Expected: 10 rows

-- View the data
SELECT * FROM deltalakeansh.bronze.sales_data;
-- Expected: 10 rows with all columns including revenue, ingested_at, source_file

-- Check which file was processed
SELECT DISTINCT source_file, COUNT(*) as rows
FROM deltalakeansh.bronze.sales_data
GROUP BY source_file;
-- Expected: shows sales_20260509_001.csv with 10 rows
```

---

## STEP 11: TEST INCREMENTAL LOAD

This proves Auto Loader only processes NEW files.

### Upload Second File

```bash
# Upload second file
aws s3 cp tests/sample_data/sales_20260510_001.csv \
  s3://dinesh-databricks-delta/landing/
```

### Run Job Again

```
Databricks → Jobs & Pipelines
→ AutoLoader_Bronze_Sales_Pipeline
→ Run now
```

### Verify Only New File Processed

```sql
-- Should now show 15 rows (10 + 5)
SELECT COUNT(*) FROM deltalakeansh.bronze.sales_data;

-- Should show 2 files
SELECT DISTINCT source_file, COUNT(*) as rows
FROM deltalakeansh.bronze.sales_data
GROUP BY source_file;

-- Expected:
-- sales_20260509_001.csv  → 10 rows (from run 1)
-- sales_20260510_001.csv  →  5 rows (from run 2)
```

---

## STEP 12: VERIFY CI/CD WORKS

```
1. Make a small change to README.md
   (add a space or change a word)

2. Push to GitHub:
   git add README.md
   git commit -m "test: verify cicd pipeline"
   git push origin main

3. Go to GitHub → your repository
4. Click "Actions" tab
5. You will see the workflow running automatically
6. It will:
   → Run unit tests
   → Deploy to Databricks
   All automatically!
```

---

## ONGOING OPERATION

Once everything is set up:

```
DAILY OPERATION:
────────────────
1. Upstream team uploads CSV to:
   s3://dinesh-databricks-delta/landing/

2. At 9:00 PM IST, Databricks job triggers automatically:
   Task 1: Setup infrastructure (ensures table exists)
   Task 2: Auto Loader picks up new files only
   Task 3: Validates data quality

3. Data is available in:
   deltalakeansh.bronze.sales_data

4. Query the data:
   SELECT * FROM deltalakeansh.bronze.sales_data;

MONITORING:
───────────
- Job run history: Databricks → Jobs & Pipelines → Runs
- Email on failure: dineshthanneru123@gmail.com
- Email on success: dineshthanneru123@gmail.com

DEPLOYING CHANGES:
──────────────────
- Make code changes in your laptop
- git add . && git commit -m "your message"
- git push origin main
- GitHub Actions automatically deploys to Databricks
```

---

## TROUBLESHOOTING

### Error: sqs:tagqueue permission

```
Fix: In autoloader_bronze.py, verify this option is set:
  .option("cloudFiles.useNotifications", "false")
```

### Error: Table not found

```
Fix: Run infrastructure SQL scripts again:
  SQL Editor → Run 01_setup_schema.sql
  SQL Editor → Run 02_setup_table.sql
```

### Error: No files to process

```
Fix: Upload CSV files to S3:
  s3://dinesh-databricks-delta/landing/
```

### Error: Permission denied on S3

```
Fix: Check IAM Role (databricks-s3-role) has S3 full access
  AWS Console → IAM → Roles → databricks-s3-role
  → Permissions → Verify s3:* is allowed
```

### Error: Bundle validation failed

```
Fix: Check databricks.yml syntax
  databricks bundle validate
  Look for YAML formatting errors
```

---

## ARCHITECTURE SUMMARY

```
UPSTREAM TEAM
  drops CSV files
       │
       ▼
s3://dinesh-databricks-delta/landing/
       │
       │ (9 PM IST daily schedule)
       ▼
DATABRICKS JOB: AutoLoader_Bronze_Sales_Pipeline
  │
  ├── Task 1: setup_infrastructure
  │   Creates schema + table if not exists
  │
  ├── Task 2: run_autoloader
  │   Auto Loader reads new files only
  │   Writes Delta files to S3 bronze path
  │
  └── Task 3: validate_data
      Checks data quality
      Fails job if quality issues found
       │
       ▼
s3://dinesh-databricks-delta/bronze/sales_data/
  (Delta Lake files)
       │
       ▼
DELTA TABLE: deltalakeansh.bronze.sales_data
  (Queryable from Databricks SQL)
```
