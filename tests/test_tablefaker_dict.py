import pytest
from tablefaker import tablefaker
from faker_education import SchoolProvider
from faker import Faker

fake = Faker()
def get_level():
    return f"level {fake.random_int(1, 5)}"

def test_dict_config_to_csv(tmp_path):
    """Test CSV export using dictionary configuration."""
    config = {
        "version": 1,
        "config": { "locale": "en_US" },
        "tables": [
            {
                "table_name": "person",
                "row_count": 100,
                "columns": [
                    { "column_name": "id", "data": "row_id" },
                    { "column_name": "first_name", "data": "fake.first_name()", "type": "string"},
                    { "column_name": "last_name", "data": "fake.last_name()", "type": "string" },
                    { "column_name": "full_name", "data": "first_name + last_name" },
                    { "column_name": "age", "data": "fake.random_int(18, 90)", "type": "int32" }
                ]
            }
        ]
    }
    
    result = tablefaker.to_csv(config, str(tmp_path), fake_provider=[SchoolProvider], custom_function=get_level)
    assert result is not None
    # When no table_name is specified, the result dict uses None as key or table_name
    # Just verify files were created
    files = list(tmp_path.glob("*.csv"))
    assert len(files) > 0
    # Verify the CSV file contains data
    import pandas as pd
    df = pd.read_csv(files[0])
    assert len(df) == 100

def test_dict_config_to_pandas():
    """Test pandas DataFrame generation using dictionary configuration."""
    config = {
        "version": 1,
        "config": { "locale": "en_US" },
        "tables": [
            {
                "table_name": "person",
                "row_count": 50,
                "columns": [
                    { "column_name": "id", "data": "row_id" },
                    { "column_name": "first_name", "data": "fake.first_name()", "type": "string"},
                    { "column_name": "last_name", "data": "fake.last_name()", "type": "string" },
                    { "column_name": "age", "data": "fake.random_int(18, 90)", "type": "int32" }
                ]
            }
        ]
    }
    
    df_dict = tablefaker.to_pandas(config, fake_provider=[SchoolProvider], custom_function=get_level)
    assert df_dict is not None
    assert "person" in df_dict
    person_df = df_dict["person"]
    assert len(person_df) == 50
    assert "id" in person_df.columns
    assert "first_name" in person_df.columns
    assert "last_name" in person_df.columns
    assert "age" in person_df.columns

def test_yaml_to_json(tmp_path):
    """Test YAML to JSON conversion."""
    output_file = tmp_path / "test_table.json"
    tablefaker.yaml_to_json("tests/test_table.yaml", str(output_file))
    assert output_file.exists()
