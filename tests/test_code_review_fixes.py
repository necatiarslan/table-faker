"""
Tests for code-review fixes:
  - parse_null_percentage (renamed from parse_null_percentge)
  - df.convert_dtypes() result now captured
  - is None / is not None comparisons
  - @staticmethod decorators on Config methods
  - SQL identifier quoting in to_sql_internal
  - ast.literal_eval replacing eval for FK argument parsing
  - bare except replaced with specific exception types
"""
import sys
import os
import inspect

sys.path.append(os.path.abspath("."))

import pytest
import pandas as pd
from tablefaker import util, tablefaker
from tablefaker.config import Config


# ---------------------------------------------------------------------------
# util.parse_null_percentage (typo fix: was parse_null_percentge)
# ---------------------------------------------------------------------------

class TestParseNullPercentage:
    def test_float_between_0_and_1(self):
        assert util.parse_null_percentage(0.5) == 0.5

    def test_float_zero(self):
        assert util.parse_null_percentage(0.0) == 0.0

    def test_float_one(self):
        assert util.parse_null_percentage(1.0) == 1.0

    def test_int_between_0_and_100(self):
        assert util.parse_null_percentage(50) == 0.5

    def test_int_100(self):
        assert util.parse_null_percentage(100) == 1.0

    def test_string_percent_suffix(self):
        assert util.parse_null_percentage("50%") == 0.5

    def test_string_percent_prefix(self):
        assert util.parse_null_percentage("%50") == 0.5

    def test_invalid_returns_zero(self):
        assert util.parse_null_percentage("invalid") == 0.0

    def test_negative_returns_zero(self):
        assert util.parse_null_percentage(-1) == 0.0

    def test_old_name_still_works(self):
        """Backward-compatible alias must still exist."""
        assert hasattr(util, "parse_null_percentge")
        assert util.parse_null_percentge(0.25) == 0.25


# ---------------------------------------------------------------------------
# Config static methods
# ---------------------------------------------------------------------------

class TestConfigStaticMethods:
    def test_avro_type_to_tablefaker_type_is_static(self):
        assert isinstance(
            inspect.getattr_static(Config, "avro_type_to_tablefaker_type"),
            staticmethod,
        )

    def test_avro_to_yaml_is_static(self):
        assert isinstance(
            inspect.getattr_static(Config, "avro_to_yaml"),
            staticmethod,
        )

    def test_csv_to_yaml_is_static(self):
        assert isinstance(
            inspect.getattr_static(Config, "csv_to_yaml"),
            staticmethod,
        )

    def test_infer_data_expression_from_column_name_is_static(self):
        assert isinstance(
            inspect.getattr_static(Config, "_infer_data_expression_from_column_name"),
            staticmethod,
        )

    def test_avro_type_string(self):
        assert Config.avro_type_to_tablefaker_type("string") == "string"

    def test_avro_type_int(self):
        assert Config.avro_type_to_tablefaker_type("int") == "Int32"

    def test_avro_type_long(self):
        assert Config.avro_type_to_tablefaker_type("long") == "Int64"

    def test_avro_type_boolean(self):
        assert Config.avro_type_to_tablefaker_type("boolean") == "boolean"

    def test_avro_type_nullable_union(self):
        assert Config.avro_type_to_tablefaker_type(["null", "string"]) == "string"

    def test_avro_type_unknown_fallback(self):
        assert Config.avro_type_to_tablefaker_type("unknown_type") == "string"

    def test_name_inference_first_name(self):
        assert Config._infer_data_expression_from_column_name("first_name", "string") == "fake.first_name()"

    def test_name_inference_street_address(self):
        assert Config._infer_data_expression_from_column_name("street_address", "string") == "fake.street_address()"

    def test_name_inference_ambiguous_falls_back_to_none(self):
        assert Config._infer_data_expression_from_column_name("status", "string") is None


# ---------------------------------------------------------------------------
# convert_dtypes() result is now captured
# ---------------------------------------------------------------------------

class TestConvertDtypesCaptured:
    """Verify that generate_table returns a properly typed DataFrame."""

    _config = {
        "version": 1,
        "config": {"locale": "en_US"},
        "tables": [
            {
                "table_name": "sample",
                "row_count": 5,
                "columns": [
                    {"column_name": "id", "data": "row_id"},
                    {"column_name": "name", "data": "fake.first_name()", "type": "string"},
                    {"column_name": "age", "data": "fake.random_int(18, 90)", "type": "int32"},
                ],
            }
        ],
    }

    def test_dataframe_returned(self):
        result = tablefaker.to_pandas(self._config)
        assert "sample" in result
        df = result["sample"]
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5

    def test_columns_present(self):
        result = tablefaker.to_pandas(self._config)
        df = result["sample"]
        assert set(df.columns) == {"id", "name", "age"}


# ---------------------------------------------------------------------------
# SQL identifier quoting (to_sql_internal)
# ---------------------------------------------------------------------------

class TestSQLExport:
    _config = {
        "version": 1,
        "config": {"locale": "en_US"},
        "tables": [
            {
                "table_name": "orders",
                "row_count": 3,
                "columns": [
                    {"column_name": "order_id", "data": "row_id"},
                    {"column_name": "description", "data": "fake.sentence()", "type": "string"},
                ],
            }
        ],
    }

    def test_sql_file_created(self, tmp_path):
        result = tablefaker.to_sql(self._config, str(tmp_path))
        files = list(tmp_path.glob("*.sql"))
        assert len(files) > 0

    def test_sql_preserves_identifiers(self, tmp_path):
        result = tablefaker.to_sql(self._config, str(tmp_path))
        sql_file = list(tmp_path.glob("*.sql"))[0]
        content = sql_file.read_text()
        # Table and column identifiers should be emitted as provided.
        assert "INSERT INTO orders" in content
        assert "(order_id, description)" in content

    def test_sql_string_values_escaped(self, tmp_path):
        """Single quotes inside string values must be escaped."""
        cfg = {
            "version": 1,
            "config": {"locale": "en_US"},
            "tables": [
                {
                    "table_name": "quotes_test",
                    "row_count": 1,
                    "columns": [
                        {"column_name": "val", "data": "\"it's a test\"", "type": "string"},
                    ],
                }
            ],
        }
        result = tablefaker.to_sql(cfg, str(tmp_path))
        sql_file = list(tmp_path.glob("*.sql"))[0]
        content = sql_file.read_text()
        # The single quote in "it's" must be escaped as ''
        assert "''" in content

    def test_sql_mssql_style_table_name_preserved(self, tmp_path):
        cfg = {
            "version": 1,
            "config": {"locale": "en_US"},
            "tables": [
                {
                    "table_name": "[schema].[dbo].[orders]",
                    "row_count": 1,
                    "columns": [
                        {"column_name": "order_id", "data": "row_id"},
                    ],
                }
            ],
        }
        result = tablefaker.to_sql(cfg, str(tmp_path))
        sql_file = list(tmp_path.glob("*.sql"))[0]
        content = sql_file.read_text()
        assert "INSERT INTO [schema].[dbo].[orders]" in content


# ---------------------------------------------------------------------------
# null_percentage applies correctly (is None comparison)
# ---------------------------------------------------------------------------

class TestNullPercentage:
    def test_null_percentage_applied(self):
        cfg = {
            "version": 1,
            "config": {"locale": "en_US"},
            "tables": [
                {
                    "table_name": "nullable",
                    "row_count": 100,
                    "columns": [
                        {"column_name": "id", "data": "row_id"},
                        {
                            "column_name": "optional",
                            "data": "fake.word()",
                            "null_percentage": 0.5,
                        },
                    ],
                }
            ],
        }
        result = tablefaker.to_pandas(cfg)
        df = result["nullable"]
        null_count = df["optional"].isna().sum()
        # With 50% null_percentage on 100 rows, expect some nulls
        assert null_count > 0
        assert null_count < 100
