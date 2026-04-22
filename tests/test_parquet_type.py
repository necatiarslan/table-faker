import sys, os
sys.path.append(os.path.abspath("."))
import pytest
import pyarrow.parquet as pq
import pyarrow as pa
from tablefaker import tablefaker
from tablefaker.tablefaker import TableFaker


# ---------------------------------------------------------------------------
# Inline YAML helpers
# ---------------------------------------------------------------------------

YAML_BASIC_PARQUET_TYPES = """
version: 1
tables:
  - table_name: product
    row_count: 5
    columns:
      - column_name: id
        data: row_id
        is_primary_key: true
        parquet_type: int32
      - column_name: name
        data: fake.word()
        parquet_type: string
      - column_name: price
        data: round(random.uniform(1.0, 100.0), 2)
        parquet_type: float32
      - column_name: quantity
        data: random.randint(1, 500)
        parquet_type: int16
"""

YAML_DECIMAL128 = """
version: 1
tables:
  - table_name: order_line
    row_count: 5
    columns:
      - column_name: id
        data: row_id
        is_primary_key: true
      - column_name: amount
        data: round(random.uniform(10.0, 9999.99), 2)
        parquet_type: decimal128(10, 2)
"""

YAML_NO_PARQUET_TYPE = """
version: 1
tables:
  - table_name: employee
    row_count: 5
    columns:
      - column_name: id
        data: row_id
        is_primary_key: true
      - column_name: name
        data: fake.name()
      - column_name: salary
        data: random.randint(50000, 120000)
"""

YAML_TYPE_AND_PARQUET_TYPE = """
version: 1
tables:
  - table_name: item
    row_count: 5
    columns:
      - column_name: id
        data: row_id
        is_primary_key: true
        type: int32
        parquet_type: int64
      - column_name: label
        data: fake.word()
"""

YAML_UNKNOWN_PARQUET_TYPE = """
version: 1
tables:
  - table_name: bad
    row_count: 2
    columns:
      - column_name: id
        data: row_id
        is_primary_key: true
        parquet_type: not_a_real_type
"""

YAML_IGNORED_FOR_CSV = """
version: 1
tables:
  - table_name: person
    row_count: 5
    columns:
      - column_name: id
        data: row_id
        is_primary_key: true
        parquet_type: int32
      - column_name: name
        data: fake.name()
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def _write_yaml(tmp_path, content, name="config.yaml"):
    config_path = tmp_path / name
    config_path.write_text(content)
    return str(config_path)

def test_parquet_type_basic(tmp_path):
    """Columns with parquet_type are written with the specified Arrow types."""
    config_path = _write_yaml(tmp_path, YAML_BASIC_PARQUET_TYPES, "basic.yaml")
    result = tablefaker.to_parquet(config_path, str(tmp_path))
    files = list(tmp_path.glob("*.parquet"))
    assert len(files) == 1

    schema = pq.read_schema(files[0])
    assert schema.field("id").type == pa.int32()
    assert schema.field("name").type == pa.string()
    assert schema.field("price").type == pa.float32()
    assert schema.field("quantity").type == pa.int16()


def test_parquet_type_decimal128(tmp_path):
    """decimal128(precision, scale) is correctly applied."""
    config_path = _write_yaml(tmp_path, YAML_DECIMAL128, "decimal.yaml")
    result = tablefaker.to_parquet(config_path, str(tmp_path))
    files = list(tmp_path.glob("*.parquet"))
    assert len(files) == 1

    schema = pq.read_schema(files[0])
    assert schema.field("amount").type == pa.decimal128(10, 2)


def test_no_parquet_type_still_works(tmp_path):
    """Tables without any parquet_type export successfully."""
    config_path = _write_yaml(tmp_path, YAML_NO_PARQUET_TYPE, "no_parquet_type.yaml")
    result = tablefaker.to_parquet(config_path, str(tmp_path))
    files = list(tmp_path.glob("*.parquet"))
    assert len(files) == 1

    table = pq.read_table(files[0])
    assert "id" in table.schema.names
    assert "name" in table.schema.names
    assert "salary" in table.schema.names


def test_type_and_parquet_type_coexist(tmp_path):
    """type (pandas cast) and parquet_type (parquet schema) are independent."""
    config_path = _write_yaml(tmp_path, YAML_TYPE_AND_PARQUET_TYPE, "both_types.yaml")
    result = tablefaker.to_parquet(config_path, str(tmp_path))
    files = list(tmp_path.glob("*.parquet"))
    assert len(files) == 1

    schema = pq.read_schema(files[0])
    # parquet_type: int64 wins in the parquet file, even though type: int32 was used for pandas
    assert schema.field("id").type == pa.int64()


def test_unknown_parquet_type_raises(tmp_path):
    """An unrecognised parquet_type string raises an Exception."""
    config_path = _write_yaml(tmp_path, YAML_UNKNOWN_PARQUET_TYPE, "bad_type.yaml")
    with pytest.raises(Exception, match="Unknown parquet_type"):
        tablefaker.to_parquet(config_path, str(tmp_path))


def test_parquet_type_ignored_for_csv(tmp_path):
    """parquet_type is silently ignored when exporting to CSV."""
    config_path = _write_yaml(tmp_path, YAML_IGNORED_FOR_CSV, "ignored_for_csv.yaml")
    result = tablefaker.to_csv(config_path, str(tmp_path))
    files = list(tmp_path.glob("*.csv"))
    assert len(files) == 1


def test_parse_parquet_type_all_simple():
    """_parse_parquet_type maps every documented simple type string correctly."""
    cases = {
        "int8": pa.int8(),
        "int16": pa.int16(),
        "int32": pa.int32(),
        "int64": pa.int64(),
        "uint8": pa.uint8(),
        "uint16": pa.uint16(),
        "uint32": pa.uint32(),
        "uint64": pa.uint64(),
        "float16": pa.float16(),
        "float32": pa.float32(),
        "float64": pa.float64(),
        "double": pa.float64(),
        "string": pa.string(),
        "utf8": pa.string(),
        "large_string": pa.large_string(),
        "large_utf8": pa.large_string(),
        "binary": pa.binary(),
        "large_binary": pa.large_binary(),
        "bool": pa.bool_(),
        "boolean": pa.bool_(),
        "date32": pa.date32(),
        "date64": pa.date64(),
        "time32[s]": pa.time32("s"),
        "time32[ms]": pa.time32("ms"),
        "time64[us]": pa.time64("us"),
        "time64[ns]": pa.time64("ns"),
        "timestamp[s]": pa.timestamp("s"),
        "timestamp[ms]": pa.timestamp("ms"),
        "timestamp[us]": pa.timestamp("us"),
        "timestamp[ns]": pa.timestamp("ns"),
    }
    for type_str, expected in cases.items():
        assert TableFaker._parse_parquet_type(type_str) == expected, f"Failed for {type_str}"


def test_parse_parquet_type_decimal128_variants():
    """decimal128 with varying whitespace is parsed correctly."""
    assert TableFaker._parse_parquet_type("decimal128(10, 2)") == pa.decimal128(10, 2)
    assert TableFaker._parse_parquet_type("decimal128(18,6)") == pa.decimal128(18, 6)
    assert TableFaker._parse_parquet_type("decimal128( 5 , 3 )") == pa.decimal128(5, 3)
