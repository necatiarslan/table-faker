import sys, os, shutil
sys.path.append(os.path.abspath("."))

from tablefaker import tablefaker
from faker_education import SchoolProvider
from faker import Faker

fake = Faker()
def get_level():
    return f"level {fake.random_int(1, 5)}"

directory_path = 'tests/exports'
if os.path.isdir(directory_path):
    shutil.rmtree(directory_path)
    os.mkdir(directory_path)

os.system('clear')

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

tablefaker.to_csv(config, "./tests/exports", fake_provider=[SchoolProvider], custom_function=get_level)

