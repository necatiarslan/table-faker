import sys
sys.path.append("/Users/necatiarslan/GitHub/table-faker")

from tablefaker import tablefaker

tablefaker.to_csv("tests/test_table.yaml", "./tests/target.csv")

