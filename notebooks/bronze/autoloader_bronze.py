# Databricks notebook source
# ============================================================
# TASK 2: Auto Loader Bronze Pipeline
# Picks up CSV files from S3 landing zone
# Writes Delta files to S3 bronze layer
# ============================================================

# COMMAND ----------

import datetime
from pyspark.sql.functions import col, current_timestamp, lit
from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, StringType, DoubleType
)

# COMMAND ----------

# ============================================================
# SECTION 1: CONFIGURATION
# ============================================================

dbutils.widgets.text("env", "prod")
env = dbutils.widgets.get("env")

# Configuration
LANDING_PATH     = "s3://dinesh-databricks-delta/landing/"
BRONZE_PATH      = "s3://dinesh-databricks-delta/bronze/sales_data/"
CHECKPOINT_PATH  = "s3://dinesh-databricks-delta/checkpoints/bronze_sales/"
SCHEMA_LOCATION  = "s3://dinesh-databricks-delta/checkpoints/bronze_sales/schema/"
BRONZE_TABLE     = "deltalakeansh.bronze.sales_data"
PIPELINE_VERSION = "v1.0"

print("=" * 60)
print("🚀 AUTO LOADER BRONZE PIPELINE")
print("=" * 60)
print(f"  Environment:     {env}")
print(f"  Landing Zone:    {LANDING_PATH}")
print(f"  Bronze Path:     {BRONZE_PATH}")
print(f"  Checkpoint:      {CHECKPOINT_PATH}")
print(f"  Bronze Table:    {BRONZE_TABLE}")
print(f"  Pipeline Ver:    {PIPELINE_VERSION}")
print(f"  Started At:      {datetime.datetime.now()}")
print("=" * 60)

# COMMAND ----------

# ============================================================
# SECTION 2: PRE-RUN STATUS REPORT
# ============================================================

print("\n📂 FILES IN S3 LANDING ZONE:")
print("-" * 60)

try:
    all_files = dbutils.fs.ls(LANDING_PATH)
    if len(all_files) == 0:
        print("  ⚠️  No files in landing zone!")
        print(f"     Upload CSV files to: {LANDING_PATH}")
        dbutils.notebook.exit("No files to process")
    else:
        for f in all_files:
            print(f"  📄  {f.name}  ({f.size} bytes)")
        print(f"\n  Total files in landing: {len(all_files)}")
except Exception as e:
    print(f"  Error accessing landing zone: {e}")
    raise

# Rows before run
print("\n📊 BRONZE TABLE STATUS BEFORE THIS RUN:")
print("-" * 60)
try:
    rows_before = spark.sql(
        f"SELECT COUNT(*) as cnt FROM {BRONZE_TABLE}"
    ).collect()[0]["cnt"]
    print(f"  Rows currently in Bronze table: {rows_before}")
except Exception:
    rows_before = 0
    print("  Rows currently in Bronze table: 0 (first run)")

# COMMAND ----------

# ============================================================
# SECTION 3: CSV SCHEMA DEFINITION
# ============================================================

# Explicit schema — always better than inferSchema in production
schema = StructType([
    StructField("order_id",     IntegerType(), True),
    StructField("product_name", StringType(),  True),
    StructField("category",     StringType(),  True),
    StructField("quantity",     IntegerType(), True),
    StructField("unit_price",   DoubleType(),  True),
    StructField("order_date",   StringType(),  True),
])

print("\n📋 INPUT SCHEMA:")
print("-" * 60)
for field in schema.fields:
    print(f"  {field.name:20} {str(field.dataType):15} nullable={field.nullable}")

# COMMAND ----------

# ============================================================
# SECTION 4: AUTO LOADER — READ FROM S3
# ============================================================

print("\n🔄 STARTING AUTO LOADER...")
print("-" * 60)
print("  Mode: Directory Listing (no SQS needed)")
print("  Trigger: availableNow (process all new files then stop)")

df_stream = (
    spark.readStream
         .format("cloudFiles")
         .option("cloudFiles.format",            "csv")
         .option("cloudFiles.schemaLocation",    SCHEMA_LOCATION)
         .option("cloudFiles.useNotifications",  "false")     # No SQS
         .option("header",                       "true")
         .schema(schema)
         .load(LANDING_PATH)
)

# COMMAND ----------

# ============================================================
# SECTION 5: TRANSFORMATIONS
# ============================================================

df_enriched = (
    df_stream
    # Business transformation
    .withColumn("revenue",
                col("quantity") * col("unit_price"))

    # Metadata columns
    .withColumn("ingested_at",
                current_timestamp())

    # Source file tracking
    # NOTE: Using _metadata.file_path (NOT input_file_name)
    # input_file_name() is blocked by Unity Catalog
    .withColumn("source_file",
                col("_metadata.file_path"))

    # Pipeline version
    .withColumn("pipeline_version",
                lit(PIPELINE_VERSION))
)

print("✅ Transformations defined:")
print("   + revenue = quantity * unit_price")
print("   + ingested_at = current timestamp")
print("   + source_file = _metadata.file_path")
print(f"  + pipeline_version = {PIPELINE_VERSION}")

# COMMAND ----------

# ============================================================
# SECTION 6: WRITE TO BRONZE DELTA TABLE
# ============================================================

query = (
    df_enriched
    .writeStream
    .format("delta")
    .option("checkpointLocation", CHECKPOINT_PATH)
    .option("mergeSchema",        "true")
    .outputMode("append")
    .trigger(availableNow=True)         # Process all new files then stop
    .toTable(BRONZE_TABLE)
)

print("\n⏳ Processing files...")
query.awaitTermination()
print("✅ Auto Loader finished!")

# COMMAND ----------

# ============================================================
# SECTION 7: POST-RUN SUMMARY REPORT
# ============================================================

print("\n" + "=" * 60)
print("📊 POST-RUN SUMMARY")
print("=" * 60)

# Rows after run
rows_after = spark.sql(
    f"SELECT COUNT(*) as cnt FROM {BRONZE_TABLE}"
).collect()[0]["cnt"]

new_rows = rows_after - rows_before

print(f"\n  Rows before this run:    {rows_before}")
print(f"  Rows after this run:     {rows_after}")
print(f"  New rows added:          {new_rows}")

if new_rows > 0:
    print(f"\n  ✅ Successfully loaded {new_rows} new rows!")
else:
    print(f"\n  ⏭️  No new rows — all files already processed (checkpoint)")

# File-level breakdown
print("\n📁 FILE-LEVEL BREAKDOWN:")
print("-" * 60)
try:
    breakdown = spark.sql(f"""
        SELECT
            SUBSTRING_INDEX(source_file, '/', -1) AS file_name,
            COUNT(*)                               AS rows_loaded,
            ROUND(SUM(revenue), 2)                 AS total_revenue,
            MIN(ingested_at)                       AS processed_at
        FROM {BRONZE_TABLE}
        WHERE source_file IS NOT NULL
        GROUP BY source_file
        ORDER BY processed_at DESC
    """)
    display(breakdown)
except Exception as e:
    print(f"  Error: {e}")

# Latest 5 rows
print("\n🔍 LATEST 5 ROWS IN BRONZE TABLE:")
print("-" * 60)
latest = spark.sql(f"""
    SELECT * FROM {BRONZE_TABLE}
    ORDER BY ingested_at DESC
    LIMIT 5
""")
display(latest)

# Delta table history
print("\n📜 DELTA TABLE HISTORY (last 5 operations):")
print("-" * 60)
spark.sql(f"""
    SELECT version, timestamp, operation, operationMetrics
    FROM (DESCRIBE HISTORY {BRONZE_TABLE})
    ORDER BY version DESC
    LIMIT 5
""").show(truncate=False)

print("\n" + "=" * 60)
print(f"✅ PIPELINE COMPLETE — {datetime.datetime.now()}")
print("=" * 60)
