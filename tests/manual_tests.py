import sys, os, shutil
sys.path.append(os.path.abspath("."))

from tablefaker import tablefaker
from faker_education import SchoolProvider
from faker import Faker

fake = Faker()
def get_level():
    return f"level {fake.random_int(1, 5)}"

directory_path = 'tests/exports'
if not os.path.exists(directory_path):
    os.makedirs(directory_path)
elif os.path.isdir(directory_path):
    shutil.rmtree(directory_path)
    os.makedirs(directory_path)

os.system('clear')

# tablefaker.to_csv("tests/test_basic_table.yaml", "./tests/exports", fake_provider=[SchoolProvider], custom_function=get_level)
# tablefaker.to_csv("tests/test_table.json", "./tests/exports", fake_provider=[SchoolProvider], custom_function=get_level)
tablefaker.to_csv("tests/manual_test.yaml", "./tests/exports", fake_provider=[SchoolProvider], custom_function=get_level)
# tablefaker.to_csv("tests/manual_test.yaml", "./tests/exports", table_name="person", fake_provider=[SchoolProvider], custom_function=get_level)
# tablefaker.to_csv("tests/manual_test.yaml", "./tests/exports/person.csv", table_name="person", fake_provider=[SchoolProvider], custom_function=get_level)
# tablefaker.to_json("tests/manual_test.yaml", "./tests/exports", fake_provider=SchoolProvider, custom_function=get_level)
# tablefaker.to_sql("tests/manual_test.yaml", "./tests/exports", fake_provider=SchoolProvider, custom_function=get_level)
# tablefaker.to_parquet("tests/manual_test.yaml", "./tests/exports", fake_provider=SchoolProvider, custom_function=get_level)
# tablefaker.to_deltalake("tests/manual_test.yaml", "./tests/exports/", fake_provider=[SchoolProvider], custom_function=get_level)
# tablefaker.to_deltalake("tests/manual_test.yaml", "./tests/exports/person/", table_name="person", fake_provider=[SchoolProvider], custom_function=get_level)

# df_dict = tablefaker.to_pandas("tests/manual_test.yaml", fake_provider=SchoolProvider, custom_function=get_level)
# person_df = df_dict["person"]
# print(person_df.dtypes)
# print(person_df.head(5))

# employee_df = df_dict["employee"]
# print(employee_df.head(5))

# tablefaker.avro_to_yaml("tests/test_person.avsc", "tests/exports/person.yaml")
# tablefaker.to_csv("tests/exports/person.yaml", "./tests/exports/")

# tablefaker.csv_to_yaml("tests/test_person.csv", "tests/exports/person.yaml")
# tablefaker.to_csv("tests/exports/person.yaml", "./tests/exports/")