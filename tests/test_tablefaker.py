import sys, os, shutil
sys.path.append(os.path.abspath("."))
import pytest
import yaml
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

    with open(output_file, "r", encoding="utf-8") as file:
        cfg = yaml.safe_load(file)

    assert "tables" in cfg and len(cfg["tables"]) == 1
    columns = cfg["tables"][0]["columns"]
    id_col = next(col for col in columns if col["column_name"] == "id")
    assert id_col["type"] == "Int64"
    assert id_col["parquet_type"] == "int64"

    first_name_col = next(col for col in columns if col["column_name"] == "first_name")
    assert first_name_col["type"] == "string"
    assert first_name_col["parquet_type"] == "string"
    assert first_name_col["data"] == "fake.first_name()"

    last_name_col = next(col for col in columns if col["column_name"] == "last_name")
    assert last_name_col["data"] == "fake.last_name()"

    age_col = next(col for col in columns if col["column_name"] == "age")
    assert age_col["data"] == "fake.random_int(18, 90)"

    street_col = next(col for col in columns if col["column_name"] == "street_address")
    assert street_col["data"] == "fake.street_address()"

    city_col = next(col for col in columns if col["column_name"] == "city")
    assert city_col["data"] == "fake.city()"

    state_col = next(col for col in columns if col["column_name"] == "state_abbr")
    assert state_col["data"] == "fake.state_abbr()"

    postcode_col = next(col for col in columns if col["column_name"] == "postcode")
    assert postcode_col["data"] == "fake.postcode()"

def test_csv_to_yaml(tmp_path):
    """Test CSV to YAML conversion."""
    output_file = tmp_path / "person.yaml"
    tablefaker.csv_to_yaml("tests/test_person.csv", str(output_file))
    assert output_file.exists()


def test_csv_to_yaml_infers_data_when_missing(tmp_path):
    """Test CSV to YAML infers data expressions when CSV rows omit data."""
    csv_file = tmp_path / "schema.csv"
    csv_file.write_text(
        "column_name,type,data\n"
        "first_name,string,\n"
        "age,int32,\n"
        "status,string,\n"
        "notes,,\n",
        encoding="utf-8",
    )

    output_file = tmp_path / "schema.yaml"
    tablefaker.csv_to_yaml(str(csv_file), str(output_file))
    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as file:
        cfg = yaml.safe_load(file)

    columns = cfg["tables"][0]["columns"]
    first_name_col = next(col for col in columns if col["column_name"] == "first_name")
    assert first_name_col["data"] == "fake.first_name()"

    age_col = next(col for col in columns if col["column_name"] == "age")
    assert age_col["data"] == "fake.random_int(18, 90)"

    status_col = next(col for col in columns if col["column_name"] == "status")
    assert status_col["data"] == "fake.word()"

    notes_col = next(col for col in columns if col["column_name"] == "notes")
    assert notes_col["data"] == "fake.word()"

def test_export_file_name_attribute_csv(tmp_path):
    """Test that export_file_name attribute is used in exported filename without timestamp."""
    result = tablefaker.to_csv("tests/test_yaml_configs/export_file_name.yaml", str(tmp_path), table_name="products")
    assert result is not None
    
    # Check that the file uses the custom export_file_name without timestamp
    expected_file = tmp_path / "product_catalog.csv"
    assert expected_file.exists(), f"Expected exact file 'product_catalog.csv', got: {[f.name for f in tmp_path.iterdir()]}"
    
    # Verify table_name is NOT used in filename
    wrong_files = list(tmp_path.glob("products*.csv"))
    assert len(wrong_files) == 0, "Should not use table_name when export_file_name is specified"

def test_export_file_name_with_chunked_export(tmp_path):
    """Test that export_file_name works correctly with chunked exports."""
    result = tablefaker.to_csv("tests/test_yaml_configs/export_file_name.yaml", str(tmp_path), table_name="customers")
    assert result is not None
    
    # With 100 rows, export_file_count: 3, we should get 3 files
    # File names should be: customer_list_1.csv, customer_list_2.csv, customer_list_3.csv
    chunk_files = list(tmp_path.glob("customer_list_*.csv"))
    assert len(chunk_files) == 3, f"Expected 3 chunk files, got {len(chunk_files)}"
    
    # Verify specific chunk names
    file_names = sorted([f.name for f in chunk_files])
    assert any("customer_list_1" in name for name in file_names), "Expected customer_list_1 file"
    assert any("customer_list_2" in name for name in file_names), "Expected customer_list_2 file"
    assert any("customer_list_3" in name for name in file_names), "Expected customer_list_3 file"

def test_export_file_name_with_json(tmp_path):
    """Test that export_file_name works with JSON exports without timestamp."""
    result = tablefaker.to_json("tests/test_yaml_configs/export_file_name.yaml", str(tmp_path), table_name="products")
    assert result is not None
    
    # Check that the JSON file uses the custom export_file_name without timestamp
    expected_file = tmp_path / "product_catalog.json"
    assert expected_file.exists(), f"Expected exact file 'product_catalog.json', got: {[f.name for f in tmp_path.iterdir()]}"

def test_export_file_name_with_parquet(tmp_path):
    """Test that export_file_name works with Parquet exports without timestamp."""
    result = tablefaker.to_parquet("tests/test_yaml_configs/export_file_name.yaml", str(tmp_path), table_name="products")
    assert result is not None
    
    # Check that the Parquet file uses the custom export_file_name without timestamp
    expected_file = tmp_path / "product_catalog.parquet"
    assert expected_file.exists(), f"Expected exact file 'product_catalog.parquet', got: {[f.name for f in tmp_path.iterdir()]}"

def test_backward_compatibility_no_export_file_name(tmp_path):
    """Test that tables without export_file_name still export with table_name (backward compatibility)."""
    # Use a config without export_file_name specified
    result = tablefaker.to_csv("tests/test_table.yaml", str(tmp_path), table_name="person")
    assert result is not None
    
    # Should use table_name 'person' in filename
    files = list(tmp_path.glob("person*.csv"))
    assert len(files) > 0, "Expected files with 'person' table_name in filename"
