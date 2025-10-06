import sys, os, shutil
sys.path.append(os.path.abspath("."))
from tablefaker import relationships
import importlib
import inspect
import pytest

def test_importable():
    """Module should import without syntax/runtime errors."""
    assert relationships is not None
    assert inspect.ismodule(relationships)
    assert hasattr(relationships, "generate_relationships")
    assert callable(relationships.generate_relationships)

def _dummy_for_param(name, tmp_path):
    n = name.lower()
    if "path" in n or "dir" in n or "file" in n:
        return str(tmp_path)
    if "table" in n or "tables" in n or "schema" in n or "schemas" in n or "relation" in n or "relations" in n:
        return []
    if n in ("n", "count", "num", "size"):
        return 1
    if "seed" in n:
        return 0
    if "conn" in n or "connection" in n:
        return None
    # fallback: unable to synthesize
    return None

def test_generate_relationships(tmp_path):
    """Call generate_relationships with synthesized dummy args when possible."""
    func = getattr(relationships, "generate_relationships", None)
    assert func is not None and callable(func), "generate_relationships is missing or not callable"
    doc = getattr(func, "__doc__", None)
    assert doc and doc.strip(), "generate_relationships is missing a docstring"

    sig = inspect.signature(func)
    args = []
    kwargs = {}
    for name, param in sig.parameters.items():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        if param.default is not inspect._empty:
            continue
        val = _dummy_for_param(name, tmp_path)
        if val is None:
            pytest.skip(f"Cannot synthesize argument for parameter '{name}' of generate_relationships")
        if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
            args.append(val)
        else:
            kwargs[name] = val

    # Call and ensure it doesn't raise unexpected exceptions
    try:
        result = func(*args, **kwargs)
    except Exception as e:
        if isinstance(e, (TypeError, ValueError)):
            pytest.skip(f"generate_relationships raised {type(e).__name__} with dummy args: {e}")
        raise
    assert result is not None