# Table Faker
![screenshoot](https://raw.githubusercontent.com/necatiarslan/table-faker/main/media/terminal.png)
**tablefaker** is a versatile Python package that enables effortless generation of realistic yet synthetic table data for various applications. Whether you need test data for software development, this tool simplifies the process with an intuitive schema definition in YAML format.

## Key Features
- **Schema Definition**: Define your table schema using a simple YAML file, specifying column names, data types, fake data generation logic, and relationships.
- **Faker & Randomization**: Utilize the **Faker** library and random data generation to create authentic-looking synthetic data.
- **Multiple Output Formats**:
  - Pandas DataFrame
  - SQL insert script
  - CSV
  - Parquet
  - JSON
  - Excel
  - Delta Lake

## Installation
```bash
pip install tablefaker
```

## Example Yaml File
```yaml
version: 1
config:
  locale: en_US
  python_import:
    - dateutil
tables:
  - table_name: person
    row_count: 10
    start_row_id: 101                               # you can set row_id starting point
    columns:
      - column_name: id
        data: row_id                                # row_id is a built-in function
      - column_name: first_name
        data: fake.first_name()                     # faker function
        type: string
      - column_name: last_name
        data: fake.last_name()
        type: string
      - column_name: full_name
        data: first_name + " " + last_name           # use a column to generate a new column
      - column_name: age
        data: fake.random_int(18, 90)
        type: int32
      - column_name: street_address
        data: fake.street_address()
      - column_name: city
        data: fake.city()
      - column_name: state_abbr
        data: fake.state_abbr()
      - column_name: postcode
        data: fake.postcode()
      - column_name: gender
        data: random.choice(["male", "female"])     # random.choice is a built-in function
        null_percentage: 0.5                        # null_percentage is a built-in function
      - column_name: left_handed
        data: fake.pybool()
      - column_name: today
        data: datetime.today().strftime('%Y-%m-%d') # datetime package is available by default
      - column_name: easter_date
        data: dateutil.easter.easter(2025).strftime('%Y-%m-%d') # python package you need to import in python_import
  - table_name: employee
    row_count: 10
    columns:
      - column_name: id
        data: row_id
      - column_name: person_id
        data: fake.random_int(1, 10)
      - column_name: hire_date
        data: fake.date_between()
        type: string
      - column_name: title
        data: random.choice(["engineer", "senior engineer", "principal engineer", "director", "senior director", "manager", "vice president", "president"])
      - column_name: salary
        data: None #NULL
        type: float
      - column_name: height
        data: r"170 cm" #string
      - column_name: weight
        data: 150 #number
      - column_name: school
        data: fake.school_name() # custom provider
      - column_name: level
        data: get_level() # custom function
```
[full yml example](tests/test_table.yaml)

## Data Generation
You can define your dummy data generation logic in a Python function. The Faker, random and datetime packages are pre-imported and ready to use.

- Use the Faker package for realistic data, e.g., `fake.first_name()` or `fake.random_int(1, 10)`.
- Use the random package for basic randomness, e.g., `random.choice(["male", "female"])`.
- Use the datetime package for current date and time, e.g., `datetime.today().strftime('%Y-%m-%d')`.
- You can use a column to generate a new column, e.g., `first_name + " " + last_name`.

You can write your logic in a single line or multiple lines, depending on your preference. A built-in function, `row_id`, provides a unique integer for each row. You can specify row_id starting point using the `start_row_id` keyword.

Columns will automatically have the best-fitting data type. However, if you'd like to specify a data type, use the `type` keyword. You can assign data types using NumPy dtypes, Pandas Extension Dtypes, or Python native types.

Here are some examples:
```
fake.first_name()
fake.random_int(1, 10)
random.choice(["male", "female"])
datetime.today()
911 # number
r"170 cm" # string

```
## Example Code
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

# exports all tables in deltalake format
tablefaker.to_deltalake("test_table.yaml", "./target_folder")

# export single table to the provided folder
tablefaker.to_deltalake("test_table.yaml", "./target_folder/person/", table_name="person")

# exports only the first table in excel format
tablefaker.to_excel("test_table.yaml", "./target_folder/target_file.xlsx")

# get as pandas dataframes
df_dict = tablefaker.to_pandas("test_table.yaml")
person_df = df_dict["person"]
print(person_df.head(5))
```

## Sample CLI Command
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

# exports to current folder in deltalake format
tablefaker --config test_table.yaml --file_type deltalake
```

## Sample CSV Output
```
id,first_name,last_name,age,dob,salary,height,weight
1,John,Smith,35,1992-01-11,,170 cm,150
2,Charles,Shepherd,27,1987-01-02,,170 cm,150
3,Troy,Johnson,42,,170 cm,150
4,Joshua,Hill,86,1985-07-11,,170 cm,150
5,Matthew,Johnson,31,1940-03-31,,170 cm,150
```

## Sample Sql Output
```sql
INSERT INTO employee
(id,person_id,hire_date,title,salary,height,weight,school,level)
VALUES
(1, 4, '2020-10-09', 'principal engineer', NULL, '170 cm', 150, 'ISLIP HIGH SCHOOL', 'level 2'),
(2, 9, '2002-12-20', 'principal engineer', NULL, '170 cm', 150, 'GUY-PERKINS HIGH SCHOOL', 'level 1'),
(3, 2, '1996-01-06', 'principal engineer', NULL, '170 cm', 150, 'SPRINGLAKE-EARTH ELEM/MIDDLE SCHOOL', 'level 3');
```
## Custom Faker Providers
You can add and use custom / community faker providers with table faker.\
Here is a list of these community providers.\
https://faker.readthedocs.io/en/master/communityproviders.html#

```yaml
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
      - column_name: school
        data: fake.school_name()  # custom provider
```

```python
import tablefaker

# import the custom faker provider
from faker_education import SchoolProvider

# provide the faker provider class to the tablefaker using fake_provider
# you can add a single provider or a list of providers
tablefaker.to_csv("test_table.yaml", "./target_folder", fake_provider=SchoolProvider)
# this works with all other to_ methods as well.
```

## Custom Functions
With Table Faker, you have the flexibility to provide your own custom functions to generate column data. This advanced feature empowers developers to create custom fake data generation logic that can pull data from a database, API, file, or any other source as needed.\
You can also supply multiple functions in a list, allowing for even more versatility. \
The custom function you provide should return a single value, giving you full control over your synthetic data generation.

```python
from tablefaker import tablefaker
from faker import Faker

fake = Faker()
def get_level():
    return f"level {fake.random_int(1, 5)}"

tablefaker.to_csv("test_table.yaml", "./target_folder", custom_function=get_level)
```
Add get_level function to your yaml file
```yaml
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

## Support & Donation
If you find Table Faker useful and would like to support its development, consider making a [donation](https://github.com/sponsors/necatiarslan).

## Additional Resources
- **Faker Functions**: [Faker Providers](https://faker.readthedocs.io/en/master/providers.html#)
- **Bug Reports & Feature Requests**: [GitHub Issues](https://github.com/necatiarslan/table-faker/issues/new)


## Roadmap
### TODO
- Add target file name to YAML
- Variables
- Export to multiple files
- Generate template yaml file from sample data
- use an ai service to generate data generation logic

### Future Enhancements
- PyArrow table support
- Primary Key / Foreign Key Support

---
**Follow for Updates**: [LinkedIn](https://www.linkedin.com/in/necati-arslan/)  
**Author**: Necati Arslan | [Email](mailto:necatia@gmail.com)


