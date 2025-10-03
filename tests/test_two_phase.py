import pytest
from tablefaker.tablefaker import TableFaker

def test_column_order_independence_two_phase(tmp_path):
    """Columns defined with copy_from_fk before foreign_key should still resolve via two-phase evaluation."""
    cfg = "tests/test_yaml_configs/two_phase_good.yaml"
    tf = TableFaker()
    dfs = tf.to_pandas(cfg)
    orders = dfs["orders"]
    customers = dfs["customers"]
    cust_map = dict(zip(customers["customer_id"], customers["email"]))
    for _, r in orders.iterrows():
        assert r["customer_email"] == cust_map[r["customer_id"]]

def test_copy_from_fk_accesses_phase_a_fk_values(tmp_path):
    """copy_from_fk must be able to read FK values computed in phase A during phase B execution."""
    cfg = "tests/test_yaml_configs/two_phase_good.yaml"
    tf = TableFaker()
    dfs = tf.to_pandas(cfg)
    # If no exceptions and values match, the test passes (redundant with above but explicit)
    orders = dfs["orders"]
    assert "customer_email" in orders.columns

def test_pk_null_guard_raises_on_null_percentage(tmp_path):
    """If a primary key column is annotated with null_percentage the generator should raise an error."""
    yaml = """
version: 1
config:
  locale: en_US
tables:
  - table_name: t1
    row_count: 3
    columns:
      - column_name: id
        data: row_id
        is_primary_key: true
        null_percentage: 0.5
      - column_name: value
        data: fake.word()
"""
    cfg = tmp_path / "bad_pk.yaml"
    with open(cfg, "w", encoding="utf-8") as f:
        f.write(yaml)
    tf = TableFaker()
    with pytest.raises(Exception):
        tf.to_pandas(str(cfg))