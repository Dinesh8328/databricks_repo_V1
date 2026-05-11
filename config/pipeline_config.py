# ============================================================
# Pipeline Configuration
# All environment-specific settings in one place
# ============================================================

PIPELINE_CONFIG = {
    "dev": {
        "env":              "dev",
        "catalog":          "deltalakeansh",
        "schema":           "bronze",
        "table":            "deltalakeansh.bronze.sales_data",
        "landing_path":     "s3://dinesh-databricks-delta/landing/",
        "bronze_path":      "s3://dinesh-databricks-delta/bronze/sales_data/",
        "checkpoint_path":  "s3://dinesh-databricks-delta/checkpoints/bronze_sales/",
        "schema_location":  "s3://dinesh-databricks-delta/checkpoints/bronze_sales/schema/",
        "pipeline_version": "v1.0",
    },
    "prod": {
        "env":              "prod",
        "catalog":          "deltalakeansh",
        "schema":           "bronze",
        "table":            "deltalakeansh.bronze.sales_data",
        "landing_path":     "s3://dinesh-databricks-delta/landing/",
        "bronze_path":      "s3://dinesh-databricks-delta/bronze/sales_data/",
        "checkpoint_path":  "s3://dinesh-databricks-delta/checkpoints/bronze_sales/",
        "schema_location":  "s3://dinesh-databricks-delta/checkpoints/bronze_sales/schema/",
        "pipeline_version": "v1.0",
    }
}


def get_config(env: str) -> dict:
    """Get configuration for the given environment."""
    if env not in PIPELINE_CONFIG:
        raise ValueError(f"Unknown environment: {env}. Choose from: {list(PIPELINE_CONFIG.keys())}")
    return PIPELINE_CONFIG[env]
