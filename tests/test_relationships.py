import sys
import os
import yaml

sys.path.append(os.path.abspath("."))

from tablefaker import relationships


def _write_config(path_obj):
    path_obj.write_text(
        yaml.safe_dump(
            {
                "tables": [
                    {
                        "table_name": "customers",
                        "columns": [
                            {"column_name": "id", "is_primary_key": True, "data": "1"},
                            {"column_name": "code", "data": "fake.word()"},
                        ],
                    },
                    {
                        "table_name": "orders",
                        "columns": [
                            {"column_name": "id", "is_primary_key": True, "data": "1"},
                            {
                                "column_name": "customer_id",
                                "data": 'foreign_key("customers", "id")',
                            },
                            {
                                "column_name": "billing_customer_id",
                                "data": 'foreign_key("customers", "id")',
                            },
                            {
                                "column_name": "customer_code",
                                "data": 'foreign_key("customers", "code")',
                            },
                        ],
                    },
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_generate_relationships_includes_only_fk_to_pk(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    _write_config(cfg)

    out_path = relationships.generate_relationships(str(cfg))
    result = yaml.safe_load((tmp_path / "cfg_table_relationships.yml").read_text(encoding="utf-8"))

    assert out_path.endswith("cfg_table_relationships.yml")
    assert len(result["relationships"]) == 1

    rel = result["relationships"][0]
    assert rel["name"] == "orders_to_customers"
    assert rel["left_table"] == "orders"
    assert rel["right_table"] == "customers"
    assert rel["join_type"] == "left_outer"
    assert rel["relationship_type"] == "many_to_one"

    assert rel["relationship_columns"] == [
        {"left_column": "billing_customer_id", "right_column": "id"},
        {"left_column": "customer_id", "right_column": "id"},
    ]


def test_generate_relationships_target_directory_and_file(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    _write_config(cfg)

    target_dir = tmp_path / "exports"
    target_dir.mkdir()
    out1 = relationships.generate_relationships(str(cfg), str(target_dir))
    assert out1 == str(target_dir / "cfg_table_relationships.yml")
    assert (target_dir / "cfg_table_relationships.yml").exists()

    target_file = tmp_path / "custom_relationships.yml"
    out2 = relationships.generate_relationships(str(cfg), str(target_file))
    assert out2 == str(target_file)
    assert target_file.exists()