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


#tablefaker.to_csv("tests/test_table.yaml", "./tests/exports", fake_provider=[SchoolProvider], custom_function=get_level)
#tablefaker.to_json("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider, custom_function=get_level)
#tablefaker.to_excel("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider, custom_function=get_level)
#tablefaker.to_parquet("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider, custom_function=get_level)
#tablefaker.to_sql("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider, custom_function=get_level)
tablefaker.to_deltalake("tests/test_table.yaml", "./tests/exports/", fake_provider=[SchoolProvider], custom_function=get_level)
#tablefaker.to_deltalake("tests/test_table.yaml", "./tests/exports/person/", table_name="person", fake_provider=[SchoolProvider], custom_function=get_level)

#df_dict = tablefaker.to_pandas("tests/test_table.yaml", fake_provider=SchoolProvider, custom_function=get_level)

#person_df = df_dict["person"]
#print(person_df.dtypes)
#print(person_df.head(5))

# employee_df = df_dict["employee"]
# print(employee_df.head(5))