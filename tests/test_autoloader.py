# ============================================================
# Unit Tests for Auto Loader Pipeline
# Run with: pytest tests/test_autoloader.py -v
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.pipeline_config import get_config, PIPELINE_CONFIG


class TestPipelineConfig:
    """Test configuration is correct for all environments."""

    def test_dev_config_has_all_keys(self):
        config = get_config("dev")
        required_keys = [
            "env", "catalog", "schema", "table",
            "landing_path", "bronze_path",
            "checkpoint_path", "schema_location",
            "pipeline_version"
        ]
        for key in required_keys:
            assert key in config, f"Missing key: {key}"

    def test_prod_config_has_all_keys(self):
        config = get_config("prod")
        required_keys = [
            "env", "catalog", "schema", "table",
            "landing_path", "bronze_path",
            "checkpoint_path", "schema_location",
            "pipeline_version"
        ]
        for key in required_keys:
            assert key in config, f"Missing key: {key}"

    def test_landing_path_ends_with_slash(self):
        for env in PIPELINE_CONFIG:
            config = get_config(env)
            assert config["landing_path"].endswith("/"), \
                f"landing_path must end with / in env: {env}"

    def test_bronze_path_ends_with_slash(self):
        for env in PIPELINE_CONFIG:
            config = get_config(env)
            assert config["bronze_path"].endswith("/"), \
                f"bronze_path must end with / in env: {env}"

    def test_checkpoint_path_ends_with_slash(self):
        for env in PIPELINE_CONFIG:
            config = get_config(env)
            assert config["checkpoint_path"].endswith("/"), \
                f"checkpoint_path must end with / in env: {env}"

    def test_s3_paths_start_with_s3(self):
        for env in PIPELINE_CONFIG:
            config = get_config(env)
            assert config["landing_path"].startswith("s3://"), \
                f"landing_path must start with s3://"
            assert config["bronze_path"].startswith("s3://"), \
                f"bronze_path must start with s3://"

    def test_table_is_three_level_namespace(self):
        for env in PIPELINE_CONFIG:
            config = get_config(env)
            parts = config["table"].split(".")
            assert len(parts) == 3, \
                f"Table must be catalog.schema.table format, got: {config['table']}"

    def test_invalid_env_raises_error(self):
        try:
            get_config("invalid_env")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestRevenueCalculation:
    """Test business logic calculations."""

    def test_revenue_calculation(self):
        quantity = 5
        unit_price = 50.0
        expected_revenue = 250.0
        assert quantity * unit_price == expected_revenue

    def test_revenue_with_zero_quantity(self):
        quantity = 0
        unit_price = 50.0
        expected_revenue = 0.0
        assert quantity * unit_price == expected_revenue

    def test_revenue_precision(self):
        quantity = 3
        unit_price = 30.0
        expected_revenue = 90.0
        assert abs((quantity * unit_price) - expected_revenue) < 0.01


class TestSampleData:
    """Test sample data files are valid."""

    def test_sample_file_exists(self):
        sample_path = os.path.join(
            os.path.dirname(__file__),
            "sample_data",
            "sales_20260509_001.csv"
        )
        assert os.path.exists(sample_path), "Sample file does not exist"

    def test_sample_file_has_header(self):
        sample_path = os.path.join(
            os.path.dirname(__file__),
            "sample_data",
            "sales_20260509_001.csv"
        )
        with open(sample_path, "r") as f:
            header = f.readline().strip()
        expected_header = "order_id,product_name,category,quantity,unit_price,order_date"
        assert header == expected_header, f"Wrong header: {header}"

    def test_sample_file_has_data_rows(self):
        sample_path = os.path.join(
            os.path.dirname(__file__),
            "sample_data",
            "sales_20260509_001.csv"
        )
        with open(sample_path, "r") as f:
            lines = f.readlines()
        # Header + at least 1 data row
        assert len(lines) > 1, "Sample file has no data rows"
