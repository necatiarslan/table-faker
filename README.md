[![PyPI Downloads](https://static.pepy.tech/personalized-badge/tablefaker?period=month&units=international_system&left_color=black&right_color=orange&left_text=PyPI%20downloads)](https://pypi.org/project/tablefaker/)

# Table Faker
tablefaker is a versatile Python package that empowers you to effortlessly create realistic but synthetic table data for a wide range of applications. If you need to generate test data for software development, this tool simplifies the process with an intuitive schema definition in YAML format.

### Key Features
**Schema Definition:** Define your target schema using a simple YAML file. Specify the structure of your tables, column names, fake data generation code, and relationships. You can define multiple tables in a yaml file.

**Faker and Randomization:** Leverage the power of the Faker library and random data generation to create authentic-looking fake data that mimics real-world scenarios.

**Multiple Output Formats:** Generate fake data in various formats to suit your needs

- Pandas Dataframe
- Sql insert script
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
config:
  locale: en_US
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
      - column_name: salary
        data: None                # NULL
      - column_name: height
        data: "\"170 cm\""        # string
      - column_name: weight
        data: 150                 # number
  - table_name: employee
    row_count: 5
    columns:
      - column_name: id
        data: row_id
      - column_name: person_id
        data: fake.random_int(1, 10)
      - column_name: hire_date
        data: fake.date_between()
      - column_name: school
        data: fake.school_name()  # custom provider
```
[full yml example](tests/test_table.yaml)

### Sample Code
```python
import tablefaker

# exports to current folder in csv format
tablefaker.to_csv("test_table.yaml")

# exports to sql insert into scripts to insert to your database
tablefaker.to_sql("test_table.yaml")

# exports all tables in json format
tablefaker.to_json("test_table.yaml", "./target_folder")

# exports all tables in parquet format
tablefaker.to_parquet("test_table.yaml", "./target_folder")

# exports only the first table in excel format
tablefaker.to_excel("test_table.yaml", "./target_folder/target_file.xlsx")

# you can use customer faker provider
from faker_education import SchoolProvider

tablefaker.to_csv("test_table.yaml", "./target_folder", fake_provider=SchoolProvider)
# multiple custom provider in list also works

# get as pandas dataframes
df_dict = tablefaker.to_pandas("test_table.yaml")
person_df = df_dict["person"]
print(person_df.head(5))
```

### Sample CLI Command
You can use tablefaker in your terminal for adhoc needs or shell script to automate fake data generation. \
Faker custom providers and custom functions are not supported in CLI.
```bash
# exports to current folder in csv format
tablefaker --config test_table.yaml

# exports as sql insert into script files
tablefaker --config test_table.yaml --file_type sql

# exports to current folder in excel format
tablefaker --config test_table.yaml --file_type excel

# exports all tables in json format
tablefaker --config test_table.yaml --file_type json --target ./target_folder 

# exports only the first table
tablefaker --config test_table.yaml --file_type parquet --target ./target_folder/target_file.parquet
```

### Sample CSV Output
```
id,first_name,last_name,age,dob,salary,height,weight
1,John,Smith,35,1992-01-11,,170 cm,150
2,Charles,Shepherd,27,1987-01-02,,170 cm,150
3,Troy,Johnson,42,,170 cm,150
4,Joshua,Hill,86,1985-07-11,,170 cm,150
5,Matthew,Johnson,31,1940-03-31,,170 cm,150
```

### Sample Sql Output
```sql
INSERT INTO employee
(id,person_id,hire_date,title,salary,height,weight,school,level)
VALUES
(1, 4, '2020-10-09', 'principal engineer', NULL, '170 cm', 150, 'ISLIP HIGH SCHOOL', 'level 2'),
(2, 9, '2002-12-20', 'principal engineer', NULL, '170 cm', 150, 'GUY-PERKINS HIGH SCHOOL', 'level 1'),
(3, 2, '1996-01-06', 'principal engineer', NULL, '170 cm', 150, 'SPRINGLAKE-EARTH ELEM/MIDDLE SCHOOL', 'level 3');
```

### Custom Functions
With Table Faker, you have the flexibility to provide your own custom functions to generate column data. This advanced feature empowers developers to create custom fake data generation logic that can pull data from a database, API, file, or any other source as needed. You can also supply multiple functions in a list, allowing for even more versatility. The custom function you provide should return a single value, giving you full control over your synthetic data generation.

```python
from tablefaker import tablefaker
from faker import Faker

fake = Faker()
def get_level():
    return f"level {fake.random_int(1, 5)}"

tablefaker.to_csv("test_table.yaml", "./target_folder", custom_function=get_level)
```
Add get_level function to your yaml file
```
version: 1
config:
  locale: en_US
tables:
  - table_name: employee
    row_count: 5
    columns:
      - column_name: id
        data: row_id
      - column_name: person_id
        data: fake.random_int(1, 10)
      - column_name: hire_date
        data: fake.date_between()
      - column_name: level
        data: get_level() # custom function
```


### Faker Functions List
https://faker.readthedocs.io/en/master/providers.html#

### Bug Report & New Feature Request
https://github.com/necatiarslan/table-faker/issues/new 


### TODO
- Foreign key
- Parquet Column Types

### Nice To Have
- AI
- Inline schema definition
- Json schema file
- Pyarrow table
- Use Logging package
- Exception Management

Follow me on linkedin to get latest news \
https://www.linkedin.com/in/necati-arslan/

Thanks, \
Necati ARSLAN \
necatia@gmail.com


