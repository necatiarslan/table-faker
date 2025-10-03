import sys, os, shutil
sys.path.append(os.path.abspath("."))
from tablefaker.plugin_loader import tf_expose

@tf_expose()
def get_parent_count(get_table):
    """Return the number of parent rows."""
    parents = get_table("parent")
    return len(parents)

@tf_expose()
def summarize(get_table):
    """Create a summary of parent data."""
    parents = get_table("parent")
    if not parents:
        return "No parents"
    total = sum(p["value"] for p in parents)
    return f"{len(parents)} parents, total={total}"