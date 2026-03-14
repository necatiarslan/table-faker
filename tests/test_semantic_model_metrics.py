import sys
import os
import yaml

sys.path.append(os.path.abspath("."))

import pytest

from tablefaker import semantic_model_metrics as smm


def test_analyze_semantic_model_extracts_structure_and_infers_hospitality():
    semantic_view = {
        "name": "hotel_analytics",
        "description": "Reservation and room occupancy tracking",
        "tables": [
            {
                "name": "reservation",
                "description": "Hotel bookings",
                "dimensions": [{"name": "reservation_id", "data_type": "NUMBER"}],
                "time_dimensions": [{"name": "checkin_date", "data_type": "DATE"}],
                "facts": [{"name": "room_revenue", "data_type": "NUMBER", "expr": "room_revenue"}],
                "metrics": [{"name": "booking_count", "expr": "COUNT(*)"}],
            }
        ],
        "relationships": [
            {
                "name": "reservation_to_room",
                "left_table": "reservation",
                "right_table": "room",
                "relationship_type": "many_to_one",
            }
        ],
    }

    summary = smm._analyze_semantic_model(semantic_view)

    assert summary["model_name"] == "hotel_analytics"
    assert "reservation" in summary["tables"]
    assert summary["tables"]["reservation"]["facts"][0]["name"] == "room_revenue"
    assert summary["relationships"][0]["left_table"] == "reservation"
    assert summary["industry"] == "Hospitality"


def test_parse_metrics_from_response_sanitizer_fallback_quotes_description():
    response = """
```yaml
- name: occupancy_rate
  description: Occupancy ratio: sold / available
  expr: SUM(reservation.rooms_sold) / NULLIF(SUM(reservation.rooms_available), 0)
```
""".strip()

    parsed = smm._parse_metrics_from_response(response)

    assert len(parsed) == 1
    assert parsed[0]["name"] == "occupancy_rate"
    assert "Occupancy ratio" in parsed[0]["description"]
    assert parsed[0]["expr"].startswith("SUM(")


def test_validate_and_enhance_metrics_adds_defaults_and_filters_invalid():
    metrics = [
        {"name": "total_revenue", "expr": "SUM(invoice.amount)"},
        {"name": "invalid_missing_expr"},
        "not_a_dict",
        {
            "name": "adr",
            "description": "Average daily rate",
            "expr": "SUM(res.revenue)/NULLIF(SUM(res.nights),0)",
            "access_modifier": "private_access",
            "synonyms": ["average daily rate"],
        },
    ]

    out = smm._validate_and_enhance_metrics(metrics, {"tables": {}})

    assert len(out) == 2
    assert out[0]["name"] == "total_revenue"
    assert out[0]["description"] == "Business metric: total_revenue"
    assert out[0]["access_modifier"] == "public_access"
    assert out[0]["synonyms"] == ["revenue total"]
    assert out[1]["name"] == "adr"
    assert "access_modifier" not in out[1]
    assert "synonyms" not in out[1]


def test_generate_model_metrics_raises_when_llm_disabled(monkeypatch, tmp_path):
    semantic_view_path = tmp_path / "semantic.yml"
    semantic_view_path.write_text("name: x\ntables: []\n", encoding="utf-8")

    class DisabledClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def is_enabled(self):
            return False

    monkeypatch.setattr(smm, "LLMClient", DisabledClient)

    with pytest.raises(RuntimeError, match="LLM is not enabled"):
        smm.generate_model_metrics(str(semantic_view_path))


def test_generate_model_metrics_writes_yaml_with_mocked_pipeline(monkeypatch, tmp_path):
    semantic_view = {
        "name": "sales_model",
        "description": "Sales analytics",
        "tables": [
            {
                "name": "invoice",
                "facts": [{"name": "amount", "data_type": "NUMBER", "expr": "amount"}],
            }
        ],
    }
    semantic_view_path = tmp_path / "semantic.yml"
    semantic_view_path.write_text(yaml.safe_dump(semantic_view), encoding="utf-8")

    class EnabledClient:
        def __init__(self, *_args, **_kwargs):
            pass

        def is_enabled(self):
            return True

    def fake_generate_metrics_with_llm(model_summary, llm_client, num_metrics):
        assert model_summary["model_name"] == "sales_model"
        assert llm_client.is_enabled() is True
        assert num_metrics == 2
        return [{"name": "total_amount", "description": "Total amount", "expr": "SUM(invoice.amount)"}]

    monkeypatch.setattr(smm, "LLMClient", EnabledClient)
    monkeypatch.setattr(smm, "_generate_metrics_with_llm", fake_generate_metrics_with_llm)

    out_dir = tmp_path / "exports"
    out_dir.mkdir()

    out_path = smm.generate_model_metrics(
        str(semantic_view_path),
        llm_config_path="ignored.yaml",
        num_metrics=2,
        target_file_path=str(out_dir),
    )

    assert out_path == str(out_dir / "semantic_generated_metrics.yml")
    written = yaml.safe_load((out_dir / "semantic_generated_metrics.yml").read_text(encoding="utf-8"))
    assert written["metrics"][0]["name"] == "total_amount"
    assert "Generated 1 business metrics" in written["comments"]