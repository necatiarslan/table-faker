import sys
sys.path.append("/Users/necatiarslan/GitHub/table-faker")

from table_faker import table_faker

result = table_faker.to_csv("tests/test_table.yaml", "tests/result_csv.csv")

