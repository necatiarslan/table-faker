import sys, os, shutil
sys.path.append(os.path.abspath("."))
import pytest
from tablefaker import tablefaker
from faker_education import SchoolProvider
from faker import Faker

fake = Faker()
def get_level():
    return f"level {fake.random_int(1, 5)}"

def test_to_csv_basic_table(tmp_path):
    """Test basic CSV export functionality."""
    result = tablefaker.to_csv("tests/test_basic_table.yaml", str(tmp_path), fake_provider=[SchoolProvider], custom_function=get_level)
    assert result is not None
    # Verify at least one file was created
    files = list(tmp_path.glob("*.csv"))
    assert len(files) > 0

def test_to_csv_from_json(tmp_path):
    """Test CSV export from JSON config."""
    result = tablefaker.to_csv("tests/test_table.json", str(tmp_path), fake_provider=[SchoolProvider], custom_function=get_level)
    assert result is not None
    files = list(tmp_path.glob("*.csv"))
    assert len(files) > 0

def test_to_csv_from_yaml(tmp_path):
    """Test CSV export from YAML config."""
    result = tablefaker.to_csv("tests/test_table.yaml", str(tmp_path), fake_provider=[SchoolProvider], custom_function=get_level)
    assert result is not None
    files = list(tmp_path.glob("*.csv"))
    assert len(files) > 0

def test_to_csv_single_table(tmp_path):
    """Test CSV export of a specific table."""
    result = tablefaker.to_csv("tests/test_table.yaml", str(tmp_path), table_name="person", fake_provider=[SchoolProvider], custom_function=get_level)
    assert result is not None
    assert "person" in result

def test_to_json(tmp_path):
    """Test JSON export functionality."""
    result = tablefaker.to_json("tests/test_table.yaml", str(tmp_path), fake_provider=SchoolProvider, custom_function=get_level)
    assert result is not None
    files = list(tmp_path.glob("*.json"))
    assert len(files) > 0

def test_to_sql(tmp_path):
    """Test SQL export functionality."""
    result = tablefaker.to_sql("tests/test_table.yaml", str(tmp_path), fake_provider=SchoolProvider, custom_function=get_level)
    assert result is not None
    files = list(tmp_path.glob("*.sql"))
    assert len(files) > 0

def test_to_parquet(tmp_path):
    """Test Parquet export functionality."""
    result = tablefaker.to_parquet("tests/test_table.yaml", str(tmp_path), fake_provider=SchoolProvider, custom_function=get_level)
    assert result is not None
    files = list(tmp_path.glob("*.parquet"))
    assert len(files) > 0

def test_to_pandas():
    """Test pandas DataFrame generation."""
    df_dict = tablefaker.to_pandas("tests/test_table.yaml", fake_provider=SchoolProvider, custom_function=get_level)
    assert df_dict is not None
    assert "person" in df_dict
    person_df = df_dict["person"]
    assert len(person_df) > 0
    assert "employee" in df_dict
    employee_df = df_dict["employee"]
    assert len(employee_df) > 0

def test_avro_to_yaml(tmp_path):
    """Test AVRO to YAML conversion."""
    output_file = tmp_path / "person.yaml"
    tablefaker.avro_to_yaml("tests/test_person.avsc", str(output_file))
    assert output_file.exists()

def test_csv_to_yaml(tmp_path):
    """Test CSV to YAML conversion."""
    output_file = tmp_path / "person.yaml"
    tablefaker.csv_to_yaml("tests/test_person.csv", str(output_file))
    assert output_file.exists()
