import sys, os
sys.path.append(os.path.abspath("."))
import pytest
from tablefaker.tablefaker import TableFaker


def test_unique_fk_no_duplicates():
    """When is_unique=True, every FK value in the child table should be unique."""
    cfg = "tests/test_yaml_configs/unique_fk.yaml"
    tf = TableFaker()
    dfs = tf.to_pandas(cfg)
    managers = dfs["managers"]

    assert managers["dept_id"].nunique() == len(managers), \
        "Foreign key column should have all unique values when is_unique=True"


def test_unique_fk_values_exist_in_parent():
    """All FK values should be valid references to the parent table."""
    cfg = "tests/test_yaml_configs/unique_fk.yaml"
    tf = TableFaker()
    dfs = tf.to_pandas(cfg)
    parent_ids = set(dfs["departments"]["dept_id"])
    child_ids = set(dfs["managers"]["dept_id"])

    assert child_ids.issubset(parent_ids), \
        "All child FK values must exist in parent PK values"


def test_unique_fk_exhaustion_raises():
    """When child row_count > parent row_count, is_unique should raise an error."""
    cfg = {
        "version": 1,
        "config": {"locale": "en_US", "seed": 99},
        "tables": [
            {
                "table_name": "items",
                "row_count": 5,
                "columns": [
                    {"column_name": "item_id", "data": "row_id", "is_primary_key": True},
                ],
            },
            {
                "table_name": "assignments",
                "row_count": 10,
                "columns": [
                    {"column_name": "assign_id", "data": "row_id", "is_primary_key": True},
                    {"column_name": "item_id", "data": 'foreign_key("items", "item_id", is_unique=True)'},
                ],
            },
        ],
    }
    tf = TableFaker()
    with pytest.raises(Exception, match="All primary key values"):
        tf.to_pandas(cfg)


def test_unique_fk_deterministic_with_seed():
    """With a fixed seed, is_unique should produce the same output across runs."""
    cfg = "tests/test_yaml_configs/unique_fk.yaml"
    tf1 = TableFaker()
    dfs1 = tf1.to_pandas(cfg)
    tf2 = TableFaker()
    dfs2 = tf2.to_pandas(cfg)

    csv1 = dfs1["managers"].to_csv(index=False)
    csv2 = dfs2["managers"].to_csv(index=False)
    assert csv1 == csv2, "is_unique FK should be deterministic with a fixed seed"


def test_unique_fk_independent_per_child_table():
    """Two child tables using is_unique on the same parent should each get their own pool."""
    cfg = {
        "version": 1,
        "config": {"locale": "en_US", "seed": 7},
        "tables": [
            {
                "table_name": "colors",
                "row_count": 5,
                "columns": [
                    {"column_name": "color_id", "data": "row_id", "is_primary_key": True},
                ],
            },
            {
                "table_name": "shirts",
                "row_count": 5,
                "columns": [
                    {"column_name": "shirt_id", "data": "row_id", "is_primary_key": True},
                    {"column_name": "color_id", "data": 'foreign_key("colors", "color_id", is_unique=True)'},
                ],
            },
            {
                "table_name": "pants",
                "row_count": 5,
                "columns": [
                    {"column_name": "pant_id", "data": "row_id", "is_primary_key": True},
                    {"column_name": "color_id", "data": 'foreign_key("colors", "color_id", is_unique=True)'},
                ],
            },
        ],
    }
    tf = TableFaker()
    dfs = tf.to_pandas(cfg)

    # Both child tables should independently have unique FK values
    assert dfs["shirts"]["color_id"].nunique() == 5
    assert dfs["pants"]["color_id"].nunique() == 5
