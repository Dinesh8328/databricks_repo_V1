-- ============================================================
-- 02_setup_table.sql
-- Run this ONCE in Databricks SQL Editor or Notebook
-- Creates the Bronze Delta table pointing to S3
-- ============================================================

CREATE TABLE IF NOT EXISTS deltalakeansh.bronze.sales_data
(
    order_id         INTEGER   COMMENT 'Unique order ID from source',
    product_name     STRING    COMMENT 'Name of the product',
    category         STRING    COMMENT 'Product category e.g. Beverages/Snacks',
    quantity         INTEGER   COMMENT 'Quantity ordered',
    unit_price       DOUBLE    COMMENT 'Price per unit in INR',
    order_date       STRING    COMMENT 'Order date in YYYY-MM-DD format',
    revenue          DOUBLE    COMMENT 'Calculated: quantity * unit_price',
    ingested_at      TIMESTAMP COMMENT 'Timestamp when Auto Loader processed this row',
    source_file      STRING    COMMENT 'Full S3 path of the source CSV file',
    pipeline_version STRING    COMMENT 'Version of the pipeline that processed this'
)
USING DELTA
LOCATION 's3://dinesh-databricks-delta/bronze/sales_data/'
COMMENT 'Bronze sales data ingested from S3 landing zone via Auto Loader'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact'   = 'true'
);

-- Verify table was created
DESCRIBE TABLE deltalakeansh.bronze.sales_data;
