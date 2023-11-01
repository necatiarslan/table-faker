import sys
sys.path.append("/Users/necatiarslan/GitHub/table-faker")

from tablefaker import tablefaker

result = tablefaker.to_csv("tests/test_table.yaml", "tests")

