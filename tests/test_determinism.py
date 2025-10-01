import os
import tempfile
import shutil
import pandas as pd
import pytest
from tablefaker.tablefaker import TableFaker
from tablefaker import tablefaker

def _write_yaml(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def _run_pandas_yaml(yaml_path):
    """Return the pandas dataframe dict produced by TableFaker for a yaml file."""
    tf = TableFaker()
    return tf.to_pandas(yaml_path)

def _concat_csv_files(dirpath):
    """Read all .csv files in dirpath (sorted) and concatenate into a single DataFrame."""
    files = sorted([os.path.join(dirpath, f) for f in os.listdir(dirpath) if f.endswith(".csv")])
    dfs = [pd.read_csv(f) for f in files]
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)

def test_same_seed_same_output(tmp_path):
    """Same YAML + same seed should produce identical output across runs."""
    yaml = """
version: 1
config:
  locale: en_US
  seed: 42
tables:
  - table_name: users
    row_count: 20
    columns:
      - column_name: user_id
        data: row_id
        is_primary_key: true
      - column_name: email
        data: fake.unique.email()
"""
    cfg = tmp_path / "det.yaml"
    _write_yaml(cfg, yaml)
    dfs1 = _run_pandas_yaml(str(cfg))
    dfs2 = _run_pandas_yaml(str(cfg))
    csv1 = dfs1["users"].to_csv(index=False)
    csv2 = dfs2["users"].to_csv(index=False)
    assert csv1 == csv2

def test_different_seeds_produce_different_output(tmp_path):
    """Different seeds should produce different outputs for the same YAML structure."""
    base_yaml = """
version: 1
config:
  locale: en_US
  seed: {seed}
tables:
  - table_name: users
    row_count: 20
    columns:
      - column_name: user_id
        data: row_id
        is_primary_key: true
      - column_name: email
        data: fake.unique.email()
"""
    cfg1 = tmp_path / "s1.yaml"
    cfg2 = tmp_path / "s2.yaml"
    _write_yaml(cfg1, base_yaml.format(seed=42))
    _write_yaml(cfg2, base_yaml.format(seed=43))
    csv1 = _run_pandas_yaml(str(cfg1))["users"].to_csv(index=False)
    csv2 = _run_pandas_yaml(str(cfg2))["users"].to_csv(index=False)
    assert csv1 != csv2

def test_chunked_export_equals_single_file(tmp_path):
    """When export_file_row_count splits a table into multiple files, the combined data equals a single-file run."""
    # single-file YAML (no export_file_row_count)
    yaml_single = """
version: 1
config:
  locale: en_US
  seed: 99
tables:
  - table_name: users
    row_count: 20
    columns:
      - column_name: user_id
        data: row_id
        is_primary_key: true
      - column_name: email
        data: fake.unique.email()
"""
    single_yaml = tmp_path / "single.yaml"
    _write_yaml(single_yaml, yaml_single)

    # chunked YAML (export_file_row_count causes multiple csvs when target is a directory)
    yaml_chunked = """
version: 1
config:
  locale: en_US
  seed: 99
tables:
  - table_name: users
    row_count: 20
    export_file_row_count: 5
    columns:
      - column_name: user_id
        data: row_id
        is_primary_key: true
      - column_name: email
        data: fake.unique.email()
"""
    chunked_yaml = tmp_path / "chunked.yaml"
    _write_yaml(chunked_yaml, yaml_chunked)

    # Single-file run -> explicit file path
    single_out = tmp_path / "out_single.csv"
    tablefaker.to_csv(str(single_yaml), str(single_out))
    df_single = pd.read_csv(single_out)

    # Chunked run -> target is a directory
    chunk_dir = tmp_path / "chunks"
    os.makedirs(chunk_dir, exist_ok=True)
    # Ensure directory empty
    for f in os.listdir(chunk_dir):
        os.remove(os.path.join(chunk_dir, f))
    tablefaker.to_csv(str(chunked_yaml), str(chunk_dir))
    df_combined = _concat_csv_files(str(chunk_dir))

    # The concatenated chunked output should equal the single-file output (order preserved)
    # Reset index and compare via pandas equals after cast to same dtypes
    assert df_single.reset_index(drop=True).equals(df_combined.reset_index(drop=True))

def test_fake_unique_across_tables_and_runs(tmp_path):
    """fake.unique should be deterministic across the run when seed is set and reuse of Faker is enabled (unique across tables)."""
    yaml = """
version: 1
config:
  locale: en_US
  seed: 7
tables:
  - table_name: customers
    row_count: 5
    columns:
      - column_name: customer_id
        data: row_id
        is_primary_key: true
      - column_name: email
        data: fake.unique.email()
  - table_name: orders
    row_count: 5
    columns:
      - column_name: order_id
        data: row_id
        is_primary_key: true
      - column_name: customer_email
        data: fake.unique.email()
"""
    cfg = tmp_path / "two_tables.yaml"
    _write_yaml(cfg, yaml)

    dfs1 = _run_pandas_yaml(str(cfg))
    dfs2 = _run_pandas_yaml(str(cfg))

    combined1 = list(dfs1["customers"]["email"]) + list(dfs1["orders"]["customer_email"])
    combined2 = list(dfs2["customers"]["email"]) + list(dfs2["orders"]["customer_email"])

    # Deterministic across runs
    assert combined1 == combined2
    # Unique across the combined set
    assert len(set(combined1)) == len(combined1)