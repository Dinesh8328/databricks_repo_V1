# Databricks notebook source
# ============================================================
# TASK 3: Data Quality Validation
# Validates Bronze table after Auto Loader run
# If any check fails → raises exception → fails the job
# ============================================================

# COMMAND ----------

import datetime

dbutils.widgets.text("env", "prod")
env = dbutils.widgets.get("env")

BRONZE_TABLE = "deltalakeansh.bronze.sales_data"

print("=" * 60)
print("🔍 DATA QUALITY VALIDATION")
print("=" * 60)
print(f"  Table:      {BRONZE_TABLE}")
print(f"  Started At: {datetime.datetime.now()}")
print("=" * 60)

# COMMAND ----------

# Track pass/fail
results = []

def check(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    results.append({"check": name, "status": status, "details": details})
    print(f"  {status}  {name}")
    if details:
        print(f"         → {details}")
    return passed

# COMMAND ----------

# ============================================================
# DATA QUALITY CHECKS
# ============================================================

print("\n📋 RUNNING CHECKS:")
print("-" * 60)

# Load the data
df = spark.sql(f"SELECT * FROM {BRONZE_TABLE}")
total_rows = df.count()

# Check 1: Table has data
check(
    "Table has rows",
    total_rows > 0,
    f"Total rows: {total_rows}"
)

# Check 2: No null order_ids
null_ids = spark.sql(f"""
    SELECT COUNT(*) as cnt
    FROM {BRONZE_TABLE}
    WHERE order_id IS NULL
""").collect()[0]["cnt"]

check(
    "No null order_ids",
    null_ids == 0,
    f"Null order_ids found: {null_ids}"
)

# Check 3: Revenue calculation is correct
wrong_revenue = spark.sql(f"""
    SELECT COUNT(*) as cnt
    FROM {BRONZE_TABLE}
    WHERE ABS(revenue - (quantity * unit_price)) > 0.01
""").collect()[0]["cnt"]

check(
    "Revenue = quantity * unit_price",
    wrong_revenue == 0,
    f"Rows with wrong revenue: {wrong_revenue}"
)

# Check 4: No null ingested_at
null_ingested = spark.sql(f"""
    SELECT COUNT(*) as cnt
    FROM {BRONZE_TABLE}
    WHERE ingested_at IS NULL
""").collect()[0]["cnt"]

check(
    "No null ingested_at",
    null_ingested == 0,
    f"Null ingested_at rows: {null_ingested}"
)

# Check 5: No null source_file
null_source = spark.sql(f"""
    SELECT COUNT(*) as cnt
    FROM {BRONZE_TABLE}
    WHERE source_file IS NULL
""").collect()[0]["cnt"]

check(
    "No null source_file",
    null_source == 0,
    f"Null source_file rows: {null_source}"
)

# Check 6: All quantities are positive
neg_qty = spark.sql(f"""
    SELECT COUNT(*) as cnt
    FROM {BRONZE_TABLE}
    WHERE quantity <= 0
""").collect()[0]["cnt"]

check(
    "All quantities are positive",
    neg_qty == 0,
    f"Rows with quantity <= 0: {neg_qty}"
)

# Check 7: All prices are positive
neg_price = spark.sql(f"""
    SELECT COUNT(*) as cnt
    FROM {BRONZE_TABLE}
    WHERE unit_price <= 0
""").collect()[0]["cnt"]

check(
    "All unit_prices are positive",
    neg_price == 0,
    f"Rows with unit_price <= 0: {neg_price}"
)

# COMMAND ----------

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("📊 VALIDATION SUMMARY")
print("=" * 60)

passed = sum(1 for r in results if "PASS" in r["status"])
failed = sum(1 for r in results if "FAIL" in r["status"])

print(f"\n  Total checks:  {len(results)}")
print(f"  Passed:        {passed}")
print(f"  Failed:        {failed}")

if failed > 0:
    print(f"\n❌ VALIDATION FAILED — {failed} check(s) failed!")
    print("   Failed checks:")
    for r in results:
        if "FAIL" in r["status"]:
            print(f"   → {r['check']}: {r['details']}")
    raise Exception(f"Data quality validation failed: {failed} check(s) failed")
else:
    print(f"\n✅ ALL CHECKS PASSED!")
    print(f"   Bronze table {BRONZE_TABLE} is clean and ready.")

print("\n" + "=" * 60)
print(f"✅ VALIDATION COMPLETE — {datetime.datetime.now()}")
print("=" * 60)
