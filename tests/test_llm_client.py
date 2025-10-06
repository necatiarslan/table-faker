import sys, os, shutil
sys.path.append(os.path.abspath("."))
from tablefaker import llm_client as llm
import importlib
import inspect
import pytest

def test_importable():
    """Module should import without syntax/runtime errors."""
    assert llm is not None
    assert inspect.ismodule(llm)

def test_LLMClient():
    """Test LLMClient initialization and basic properties."""
    client = llm.LLMClient()
    assert client is not None
    assert hasattr(client, "config")
    assert isinstance(client.config, dict)
    assert hasattr(client, "api_key")
    assert hasattr(client, "base_url")
    assert hasattr(client, "model")
    # Check default values
    assert client.base_url.startswith("http")
    assert isinstance(client.model, str) and len(client.model) > 0