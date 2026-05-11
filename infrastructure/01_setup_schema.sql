-- ============================================================
-- 01_setup_schema.sql
-- Run this ONCE in Databricks SQL Editor or Notebook
-- Creates the bronze schema
-- ============================================================

CREATE SCHEMA IF NOT EXISTS deltalakeansh.bronze
COMMENT 'Bronze layer - raw ingested data from S3 via Auto Loader';

-- Verify
SHOW SCHEMAS IN deltalakeansh;
