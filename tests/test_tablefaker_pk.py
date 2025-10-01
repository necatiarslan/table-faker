import pytest
from tablefaker import tablefaker

def test_primary_key_table_to_csv(tmp_path):
    """Test CSV export with primary key configuration."""
    result = tablefaker.to_csv("tests/test_table_pk.yaml", str(tmp_path))
    assert result is not None
    files = list(tmp_path.glob("*.csv"))
    assert len(files) > 0

def test_primary_key_table_to_pandas():
    """Test pandas DataFrame generation with primary key configuration."""
    df_dict = tablefaker.to_pandas("tests/test_table_pk.yaml")
    assert df_dict is not None
    # Verify that at least one table was generated
    assert len(df_dict) > 0
    # Check that each table has data
    for table_name, df in df_dict.items():
        assert len(df) > 0
