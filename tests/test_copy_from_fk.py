import sys, os, shutil
sys.path.append(os.path.abspath("."))

import tempfile
import pytest
import pandas as pd
from tablefaker.tablefaker import TableFaker

def _write_yaml(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def test_copy_from_fk_copies_parent_attributes(tmp_path):
    """Verify copy_from_fk() copies attributes from the parent row exactly."""
    yaml = """
version: 1
config:
  locale: en_US
tables:
  - table_name: customers
    row_count: 3
    columns:
      - column_name: customer_id
        data: row_id
        is_primary_key: true
      - column_name: email
        data: fake.email()
  - table_name: orders
    row_count: 10
    columns:
      - column_name: order_id
        data: row_id
        is_primary_key: true
      - column_name: customer_id
        data: foreign_key("customers","customer_id")
      - column_name: customer_email
        data: copy_from_fk("customers","customer_id","email")
"""
    cfg = tmp_path / "cfg.yaml"
    _write_yaml(cfg, yaml)
    tf = TableFaker()
    dfs = tf.to_pandas(str(cfg))
    customers = dfs["customers"]
    orders = dfs["orders"]
    # Build lookup map from customer_id -> email
    cust_map = dict(zip(customers["customer_id"], customers["email"]))
    for _, row in orders.iterrows():
        cid = row["customer_id"]
        assert row["customer_email"] == cust_map[cid]

def test_error_when_fk_parent_table_not_yet_generated(tmp_path):
    """If a child references a parent table that appears later in the YAML, an error should be raised."""
    yaml = """
version: 1
config:
  locale: en_US
tables:
  - table_name: orders
    row_count: 3
    columns:
      - column_name: order_id
        data: row_id
        is_primary_key: true
      - column_name: customer_id
        data: foreign_key("customers","customer_id")
      - column_name: customer_email
        data: copy_from_fk("customers","customer_id","email")
  - table_name: customers
    row_count: 2
    columns:
      - column_name: customer_id
        data: row_id
        is_primary_key: true
      - column_name: email
        data: fake.email()
"""
    cfg = tmp_path / "bad_order.yaml"
    _write_yaml(cfg, yaml)
    tf = TableFaker()
    with pytest.raises(Exception) as exc:
        tf.to_pandas(str(cfg))
    assert "Table customers not found" in str(exc.value) or "primary key" in str(exc.value)

def test_multiple_parent_tables_copy(tmp_path):
    """Test copy_from_fk works when child copies attributes from multiple different parent tables."""
    yaml = """
version: 1
config:
  locale: en_US
tables:
  - table_name: customers
    row_count: 2
    columns:
      - column_name: customer_id
        data: row_id
        is_primary_key: true
      - column_name: email
        data: fake.email()
  - table_name: vendors
    row_count: 2
    columns:
      - column_name: vendor_id
        data: row_id
        is_primary_key: true
      - column_name: vendor_name
        data: fake.company()
  - table_name: transactions
    row_count: 6
    columns:
      - column_name: txn_id
        data: row_id
        is_primary_key: true
      - column_name: customer_id
        data: foreign_key("customers","customer_id")
      - column_name: vendor_id
        data: foreign_key("vendors","vendor_id")
      - column_name: customer_email
        data: copy_from_fk("customers","customer_id","email")
      - column_name: vendor_name
        data: copy_from_fk("vendors","vendor_id","vendor_name")
"""
    cfg = tmp_path / "multi_parent.yaml"
    _write_yaml(cfg, yaml)
    tf = TableFaker()
    dfs = tf.to_pandas(str(cfg))
    customers = dfs["customers"]
    vendors = dfs["vendors"]
    txns = dfs["transactions"]
    cust_map = dict(zip(customers["customer_id"], customers["email"]))
    vend_map = dict(zip(vendors["vendor_id"], vendors["vendor_name"]))
    for _, r in txns.iterrows():
        assert r["customer_email"] == cust_map[r["customer_id"]]
        assert r["vendor_name"] == vend_map[r["vendor_id"]]

def test_name_inference_auto_resolves_to_copy_from_fk(tmp_path):
    """When infer_entity_attrs_by_name is true and a column is 'auto', it should be turned into copy_from_fk(...)"""
    yaml = """
version: 1
config:
  locale: en_US
  infer_entity_attrs_by_name: true
tables:
  - table_name: customers
    row_count: 2
    columns:
      - column_name: customer_id
        data: row_id
        is_primary_key: true
      - column_name: email
        data: fake.email()
  - table_name: orders
    row_count: 4
    columns:
      - column_name: order_id
        data: row_id
        is_primary_key: true
      - column_name: customer_id
        data: foreign_key("customers","customer_id")
      - column_name: customer_email
        data: auto
"""
    cfg = tmp_path / "infer.yaml"
    _write_yaml(cfg, yaml)
    tf = TableFaker()
    dfs = tf.to_pandas(str(cfg))
    customers = dfs["customers"]
    orders = dfs["orders"]
    cust_map = dict(zip(customers["customer_id"], customers["email"]))
    for _, r in orders.iterrows():
        assert r["customer_email"] == cust_map[r["customer_id"]]