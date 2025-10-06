import sys, os, shutil
sys.path.append(os.path.abspath("."))
from tablefaker import cli
import importlib
import inspect
import pytest

def test_cli_importable():
    """Module should import without syntax/runtime errors."""
    assert cli is not None
    assert inspect.ismodule(cli)
    assert hasattr(cli, "main")
    assert callable(cli.main)

def test_cli():
    """Calling cli.main() with no args should exit with code 2 (argparse error)."""
    with pytest.raises(SystemExit) as excinfo:
        cli.main()
    assert excinfo.value.code == 2