# Databricks notebook source
# ============================================================
# TASK 1: Setup Infrastructure
# Creates schema and Delta table if they don't exist
# ============================================================

# COMMAND ----------

# Get environment parameter
dbutils.widgets.text("env", "prod")
env = dbutils.widgets.get("env")
print(f"Setting up infrastructure for environment: {env}")

# COMMAND ----------

# Step 1: Create Schema
spark.sql("""
    CREATE SCHEMA IF NOT EXISTS deltalakeansh.bronze
    COMMENT 'Bronze layer - raw ingested data from S3 via Auto Loader'
""")
print("✅ Schema deltalakeansh.bronze created (or already exists)")

# COMMAND ----------

# Step 2: Create Delta Table pointing to S3
spark.sql("""
    CREATE TABLE IF NOT EXISTS deltalakeansh.bronze.sales_data
    (
        order_id         INTEGER   COMMENT 'Unique order ID from source',
        product_name     STRING    COMMENT 'Name of the product',
        category         STRING    COMMENT 'Product category e.g. Beverages/Snacks',
        quantity         INTEGER   COMMENT 'Quantity ordered',
        unit_price       DOUBLE    COMMENT 'Price per unit',
        order_date       STRING    COMMENT 'Order date in YYYY-MM-DD format',
        revenue          DOUBLE    COMMENT 'Calculated: quantity * unit_price',
        ingested_at      TIMESTAMP COMMENT 'Timestamp when Auto Loader processed this row',
        source_file      STRING    COMMENT 'Full S3 path of the source CSV file',
        pipeline_version STRING    COMMENT 'Version of the pipeline that processed this'
    )
    USING DELTA
    LOCATION 's3://dinesh-databricks-delta/bronze/sales_data/'
    COMMENT 'Bronze sales data - ingested from S3 landing zone via Auto Loader'
    TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact'   = 'true'
    )
""")
print("✅ Table deltalakeansh.bronze.sales_data created (or already exists)")

# COMMAND ----------

# Step 3: Verify setup
print("\n📋 Table Details:")
spark.sql("DESCRIBE TABLE deltalakeansh.bronze.sales_data").show(truncate=False)

print("\n📋 Table Location:")
spark.sql("DESCRIBE DETAIL deltalakeansh.bronze.sales_data") \
     .select("format", "location", "numFiles", "sizeInBytes") \
     .show(truncate=False)

print("\n✅ Infrastructure setup complete!")
