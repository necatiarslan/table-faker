import sys
import os
import yaml

sys.path.append(os.path.abspath("."))

from tablefaker import semantic_view as sv


class DisabledLLM:
    def is_enabled(self):
        return False


def _sample_tables():
    return [
        {
            "table_name": "customers",
            "columns": [
                {"column_name": "id", "type": "int64", "is_primary_key": True, "data": "1"},
                {"column_name": "name", "type": "string", "data": "fake.name()"},
            ],
        },
        {
            "table_name": "orders",
            "columns": [
                {"column_name": "id", "type": "int64", "is_primary_key": True, "data": "1"},
                {
                    "column_name": "customer_id",
                    "type": "int64",
                    "data": 'foreign_key("customers", "id")',
                },
                {"column_name": "total_amount", "type": "float", "data": "100.0"},
                {"column_name": "created_at", "type": "datetime", "data": "fake.date_time()"},
            ],
        },
    ]


def test_extract_table_metadata_includes_fk_details():
    metadata = sv._extract_table_metadata(_sample_tables())

    assert "orders" in metadata
    fk_col = [c for c in metadata["orders"]["columns"] if c["column_name"] == "customer_id"][0]
    assert fk_col["is_foreign_key"] is True
    assert fk_col["fk_table"] == "customers"
    assert fk_col["fk_column"] == "id"
    assert metadata["orders"]["primary_keys"] == ["id"]


def test_extract_relationships_only_uses_fk_to_pk():
    tables = _sample_tables()
    # Add FK to non-PK column; this one should be ignored.
    tables[1]["columns"].append(
        {"column_name": "customer_name", "type": "string", "data": 'foreign_key("customers", "name")'}
    )

    rels = sv._extract_relationships(tables)

    assert len(rels) == 1
    assert rels[0]["left_table"] == "orders"
    assert rels[0]["right_table"] == "customers"
    assert rels[0]["left_column"] == "customer_id"
    assert rels[0]["right_column"] == "id"


def test_classify_column_and_infer_data_type_branches():
    llm_client = DisabledLLM()

    assert sv._classify_column({"column_name": "id", "type": "int64", "is_primary_key": True}, "t", llm_client) == "dimension"
    assert sv._classify_column({"column_name": "customer_id", "type": "int64", "is_foreign_key": True}, "t", llm_client) == "dimension"
    assert sv._classify_column({"column_name": "created_at", "type": "datetime"}, "t", llm_client) == "time_dimension"
    assert sv._classify_column({"column_name": "total_amount", "type": "float"}, "t", llm_client) == "fact"
    assert sv._classify_column({"column_name": "status", "type": "string"}, "t", llm_client) == "dimension"

    assert sv._infer_data_type("int64") == "NUMBER"
    assert sv._infer_data_type("datetime") == "TIMESTAMP"
    assert sv._infer_data_type("string") == "VARCHAR"


def test_build_semantic_model_without_llm():
    metadata = sv._extract_table_metadata(_sample_tables())
    relationships = sv._extract_relationships(_sample_tables())
    model = sv._build_semantic_model(metadata, relationships, DisabledLLM())

    assert model["name"].endswith("_semantic_model")
    assert "Semantic model containing" in model["description"]
    assert len(model["tables"]) == 2

    customers = [t for t in model["tables"] if t["name"] == "customers"][0]
    pk_dimension = [d for d in customers.get("dimensions", []) if d["name"] == "id"][0]
    assert pk_dimension["unique"] is True

    assert "relationships" in model
    assert model["relationships"][0]["relationship_columns"][0] == {
        "left_column": "customer_id",
        "right_column": "id",
    }


def test_generate_semantic_view_writes_file_with_dict_source(monkeypatch, tmp_path):
    monkeypatch.setattr(sv, "LLMClient", lambda *_args, **_kwargs: DisabledLLM())

    config_dict = {"tables": _sample_tables()}
    out_path = sv.generate_semantic_view(config_dict, str(tmp_path), llm_config_path="ignored.yaml")

    assert out_path == str(tmp_path / "semantic_view.yml")
    written = yaml.safe_load((tmp_path / "semantic_view.yml").read_text(encoding="utf-8"))
    assert "tables" in written
    assert written["tables"][0]["base_table"]["database"] == "<database>"
