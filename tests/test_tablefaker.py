import sys
sys.path.append("/Users/necatiarslan/GitHub/table-faker")

from tablefaker import tablefaker
from faker_education import SchoolProvider

tablefaker.to_csv("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider)
#tablefaker.to_json("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider)
#tablefaker.to_excel("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider)
#tablefaker.to_parquet("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider)

