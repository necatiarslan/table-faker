import sys
import os

sys.path.append(os.path.abspath("."))

import pytest

from tablefaker import llm_client as llm


def _write_yaml(path_obj, content):
    path_obj.write_text(content, encoding="utf-8")


def test_load_default_config_when_file_missing(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    client = llm.LLMClient()

    assert client.is_enabled() is False
    assert client.base_url == "https://api.openai.com/v1"
    assert client.model == "gpt-4"


def test_load_config_missing_path_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        llm.LLMClient(str(tmp_path / "missing.yaml"))


def test_base_url_normalization_and_enabled(tmp_path):
    cfg = tmp_path / "llm.config"
    _write_yaml(
        cfg,
        """
enabled: true
api_key: abc
base_url: http://localhost:4000/openai/v1/chat/completions
model: test-model
""".strip(),
    )

    client = llm.LLMClient(str(cfg))

    assert client.is_enabled() is True
    assert client.base_url == "http://localhost:4000/openai/v1"
    assert client.model == "test-model"


def test_generate_rejects_when_disabled(tmp_path):
    cfg = tmp_path / "llm.config"
    _write_yaml(
        cfg,
        """
enabled: false
api_key: abc
base_url: https://api.openai.com/v1
model: gpt-4
""".strip(),
    )
    client = llm.LLMClient(str(cfg))

    with pytest.raises(RuntimeError, match="not enabled"):
        client.generate("hello")


def test_generate_builds_request_without_none_optionals(tmp_path):
    cfg = tmp_path / "llm.config"
    _write_yaml(
        cfg,
        """
enabled: true
api_key: abc
base_url: https://api.openai.com/v1
model: my-model
temperature:
max_tokens:
""".strip(),
    )
    client = llm.LLMClient(str(cfg))

    captured = {}

    class FakeMessage:
        content = " ok  "

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        @staticmethod
        def create(**kwargs):
            captured["kwargs"] = kwargs
            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    client._client = FakeClient()
    out = client.generate("prompt", "sys")

    assert out == "ok"
    assert captured["kwargs"]["model"] == "my-model"
    assert captured["kwargs"]["messages"] == [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "prompt"},
    ]
    assert "temperature" not in captured["kwargs"]
    assert "max_tokens" not in captured["kwargs"]


def test_generate_column_description_shortcuts_id_fields(tmp_path):
    cfg = tmp_path / "llm.config"
    _write_yaml(cfg, "enabled: false")
    client = llm.LLMClient(str(cfg))

    assert client.generate_column_description("orders", "id", "int64", "", "dimension") == (
        "Unique identifier for orders"
    )
    assert client.generate_column_description(
        "orders", "customer_id", "int64", "", "dimension"
    ) == "Foreign key reference to customer"


def test_create_sample_config_copies_example(tmp_path):
    out_path = tmp_path / "llm.config"

    returned = llm.create_sample_config(str(out_path))

    assert returned == str(out_path)
    content = out_path.read_text(encoding="utf-8")
    assert "enabled:" in content
    assert "base_url:" in content