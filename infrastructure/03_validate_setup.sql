-- ============================================================
-- 03_validate_setup.sql
-- Run this to verify everything is set up correctly
-- ============================================================

-- Check 1: Schema exists
SHOW SCHEMAS IN deltalakeansh;

-- Check 2: Table exists
SHOW TABLES IN deltalakeansh.bronze;

-- Check 3: Table structure
DESCRIBE TABLE deltalakeansh.bronze.sales_data;

-- Check 4: Table location (should show S3 path)
DESCRIBE DETAIL deltalakeansh.bronze.sales_data;

-- Check 5: Table history
DESCRIBE HISTORY deltalakeansh.bronze.sales_data;

-- Check 6: Row count
SELECT COUNT(*) AS total_rows FROM deltalakeansh.bronze.sales_data;
