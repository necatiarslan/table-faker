# Table Faker
tablefaker is a versatile Python package that empowers you to effortlessly create realistic but synthetic table data for a wide range of applications. If you need to generate test data for software development, this tool simplifies the process with an intuitive schema definition in YAML format.

### Key Features
**Schema Definition:** Define your target schema using a simple YAML file. Specify the structure of your tables, column names, fake data generation function, and relationships.

**Faker and Randomization:** Leverage the power of the Faker library and random data generation to create authentic-looking fake data that mimics real-world scenarios.

**Multiple Output Formats:** Generate fake data in various formats to suit your needs

- Pandas Dataframe
- CSV File
- Parquet File
- JSON File
- Excel File

### Installation
```bash 
pip install tablefaker
```

### Sample Yaml File
```
version: 1
tables:
  - table_name: person
    row_count: 10
    columns:
      - column_name: id
        data: row_id
      - column_name: first_name
        data: fake.first_name()
      - column_name: last_name
        data: fake.last_name()
      - column_name: age
        data: fake.random_int(18, 90)
      - column_name: dob
        data: fake.date_of_birth()
        null_percentage: 0.20
  - table_name: employee
    row_count: 5
    columns:
      - column_name: id
        data: row_id
      - column_name: person_id
        data: fake.random_int(1, 10)
      - column_name: hire_date
        data: fake.date_between()
```
[full yml example](tests/test_table.yaml)

### Sample Code
```python
import tablefaker

tablefaker.to_csv("test_table.yaml") # exports to current folder in csv format
tablefaker.to_json("test_table.yaml", "./target_folder") # exports all tables in json format
tablefaker.to_parquet("test_table.yaml", "./target_folder") # exports all tables in parquet format
tablefaker.to_excel("test_table.yaml", "./target_folder/target_file.csv") # exports only the first table in excel format
```

### Sample CLI Command
```bash
tablefaker --config test_table.yaml # exports to current folder in csv format
tablefaker --config test_table.yaml --file_type excel # exports to current folder in excel format
tablefaker --config test_table.yaml --file_type json --target ./target_folder # exports all tables in json format
tablefaker --config test_table.yaml --file_type parquet --target ./target_folder/target_file.parquet # exports only the first table
```

### Sample CSV Output
```
id,first_name,last_name,age,dob
1,John,Smith,35,1992-01-11
2,Charles,Shepherd,27,1987-01-02
3,Troy,Johnson,42,
4,Joshua,Hill,86,1985-07-11
5,Matthew,Johnson,31,1940-03-31
```

### Faker Functions List
https://faker.readthedocs.io/en/master/providers.html#

### Bug Report & New Feature Request
https://github.com/necatiarslan/table-faker/issues/new 


### TODO
- Custom fake data creation function
- Exception Management
- Foreign key
- Custom Faker Provider support
- Parquet Column Types


### Nice To Have
- Export To PostgreSQL
- Inline schema definition
- Json schema file
- Pyarrow table
- Use Logging package

Follow me on linkedin to get latest news \
https://www.linkedin.com/in/necati-arslan/

Thanks, \
Necati ARSLAN \
necatia@gmail.com


