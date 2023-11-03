import sys
sys.path.append("/Users/necatiarslan/GitHub/table-faker")

from tablefaker import tablefaker

tablefaker.to_csv("tests/test_table.yaml", "./tests/exports")
#tablefaker.to_json("tests/test_table.yaml", "./tests/exports")
#tablefaker.to_excel("tests/test_table.yaml", "./tests/exports")
#tablefaker.to_parquet("tests/test_table.yaml", "./tests/exports")

