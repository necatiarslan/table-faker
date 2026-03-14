import sys
import os

sys.path.append(os.path.abspath("."))

from tablefaker import cli


def test_main_missing_config_prints_hint(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["tablefaker"])

    cli.main()

    out = capsys.readouterr().out
    assert "Missing --config parameter" in out
    assert "--generate-metrics does not require --config" in out


def test_main_generate_metrics_dispatch(monkeypatch, capsys):
    calls = {}

    def fake_generate_model_metrics(view_path, llm_config, num_metrics, target):
        calls["args"] = (view_path, llm_config, num_metrics, target)
        return "metrics.yml"

    monkeypatch.setattr(
        cli.semantic_model_metrics,
        "generate_model_metrics",
        fake_generate_model_metrics,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tablefaker",
            "--generate-metrics",
            "semantic.yml",
            "--llm-config",
            "llm.yaml",
            "--num-metrics",
            "7",
            "--target",
            "out",
        ],
    )

    cli.main()

    assert calls["args"] == ("semantic.yml", "llm.yaml", 7, "out")
    assert "Generated 7 business metrics written to metrics.yml" in capsys.readouterr().out


def test_main_relationships_dispatch(monkeypatch, capsys):
    calls = {}

    def fake_generate_relationships(config_source, target):
        calls["args"] = (config_source, target)
        return "rels.yml"

    monkeypatch.setattr(cli.relationships, "generate_relationships", fake_generate_relationships)
    monkeypatch.setattr(
        sys,
        "argv",
        ["tablefaker", "--config", "cfg.yaml", "--relationships", "--target", "out"],
    )

    cli.main()

    assert calls["args"] == ("cfg.yaml", "out")
    assert "Relationships written to rels.yml" in capsys.readouterr().out


def test_main_semantic_view_dispatch(monkeypatch, capsys):
    calls = {}

    def fake_generate_semantic_view(config_source, target, llm_config):
        calls["args"] = (config_source, target, llm_config)
        return "sv.yml"

    monkeypatch.setattr(cli.semantic_view, "generate_semantic_view", fake_generate_semantic_view)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tablefaker",
            "--config",
            "cfg.yaml",
            "--semantic-view",
            "--llm-config",
            "llm.yaml",
        ],
    )

    cli.main()

    assert calls["args"] == ("cfg.yaml", ".", "llm.yaml")
    assert "Semantic view written to sv.yml" in capsys.readouterr().out


def test_main_defaults_to_data_generation(monkeypatch):
    calls = {}

    def fake_to_target(file_type, config_source, target_file_path, **kwargs):
        calls["args"] = (file_type, config_source, target_file_path, kwargs)

    monkeypatch.setattr(cli.tablefaker, "to_target", fake_to_target)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tablefaker",
            "--config",
            "cfg.yaml",
            "--seed",
            "123",
            "--infer-attrs",
            "true",
        ],
    )

    cli.main()

    assert calls["args"][0] == "csv"
    assert calls["args"][1] == "cfg.yaml"
    assert calls["args"][2] == "."
    assert calls["args"][3] == {"seed": 123, "infer_attrs": "true"}