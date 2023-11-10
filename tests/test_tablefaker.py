import sys, os
sys.path.append(os.path.abspath("."))

from tablefaker import tablefaker
from faker_education import SchoolProvider
from faker import Faker

fake = Faker()
def get_level():
    return f"level {fake.random_int(1, 5)}"

directory_path = 'tests/exports'
[os.remove(os.path.join(directory_path, file)) for file in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, file))]

tablefaker.to_csv("tests/test_table.yaml", "./tests/exports", fake_provider=[SchoolProvider], custom_function=get_level)
#tablefaker.to_json("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider, custom_function=get_level)
#tablefaker.to_excel("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider, custom_function=get_level)
#tablefaker.to_parquet("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider, custom_function=get_level)

#tablefaker.to_csv("tests/test_cli.yaml", "./tests/exports")
