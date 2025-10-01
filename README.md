# ![icon](https://raw.githubusercontent.com/necatiarslan/table-faker/main/media/tablefaker-icon-32.png) Table Faker
![screenshoot](https://raw.githubusercontent.com/necatiarslan/table-faker/main/media/terminal.png)
**tablefaker** is a versatile Python package that enables effortless generation of realistic yet synthetic table data for various applications. Whether you need test data for software development, this tool simplifies the process with an intuitive schema definition in YAML format.

## Key Features
- **Schema Definition**: Define your table schema using a simple YAML file, specifying column names, data types, fake data generation logic, and relationships.
- **Faker & Randomization**: Utilize the **Faker** library and random data generation to create authentic-looking synthetic data.
- **Multiple Table Support**: Create multiple tables with different schemas and data generation logic in a single YAML file. Define relationships between tables for foreign keys and primary keys.
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
## Sample Yaml File Minimal
```yaml
tables:
  - table_name: person
    columns:
      - column_name: id
        data: row_id
      - column_name: first_name
        data: fake.first_name()
      - column_name: last_name
        data: fake.last_name()
```
## Sample Yaml File Advanced
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
    export_file_count: 3                           # you can set export file count (dominant to export_file_row_count)
    columns:
      - column_name: id
        data: row_id                                # row_id is a built-in function
        is_primary_key: true                        # define primary key to use as a foreign key
      - column_name: first_name
        data: fake.first_name()                     # faker function
        type: string
      - column_name: last_name
        data: fake.last_name()
        type: string
      - column_name: full_name
        data: first_name + " " + last_name           # use a column to generate a new column
        is_primary_key: true
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
      - column_name: discount_eligibility           # custom python function
        data: |
          if age < 25 or age > 60:
            return True
          else:
            return False
  - table_name: employee
    row_count: 10
    export_file_row_count: 60                      # you can set export file row count
    columns:
      - column_name: id
        data: row_id
      - column_name: person_id
        data: foreign_key("person", "id")          # get primary key from another table
      - column_name: full_name
        data: foreign_key("person", "full_name")
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

## Configuration: Determinism & Attribute Inference

### Seed (deterministic)
[`yaml.declaration()`](table-faker/README.md:114)
```yaml
config:
  locale: en_US
  seed: 42  # Optional: for reproducible datasets
```
- Setting `config.seed` makes runs deterministic: the same seed and same YAML produce identical outputs.
- The seed is applied to Python's `random`, NumPy (when available), and the `Faker` instance used by tablefaker.
- Use cases: repeatable tests, CI snapshots, and reproducible examples.

### Attribute name inference
[`yaml.declaration()`](table-faker/README.md:114)
```yaml
config:
  infer_entity_attrs_by_name: true  # Optional: auto-infer FK attributes
```
- When enabled, columns named with the pattern `<fkprefix>_<attr>` will be automatically bound to the referenced parent row if a sibling `<fkprefix>_id` exists and is a foreign key.
- Example: `customer_email` will be auto-resolved from the row referenced by `customer_id` (if `customer_id` is a FK to `customers.customer_id`).

## Cross-Table Relationships

### Using copy_from_fk()
[`yaml.declaration()`](table-faker/README.md:114)
```yaml
- column_name: customer_email
  data: copy_from_fk("customer_id", "customers", "email")
```
- `copy_from_fk(fk_column, parent_table, parent_attr)` copies an attribute from the parent row referenced by the foreign key.
- Useful when you need to duplicate a value from the parent instead of generating it again.
- Parent tables must be defined before child tables in the YAML (no automatic backfilling).

Full parent/child example:
[`yaml.declaration()`](table-faker/README.md:114)
```yaml
tables:
  - table_name: customers
    row_count: 10
    columns:
      - column_name: customer_id
        is_primary_key: true
        data: row_id
      - column_name: email
        data: fake.email()

  - table_name: orders
    row_count: 50
    columns:
      - column_name: order_id
        data: row_id
        is_primary_key: true
      - column_name: customer_id
        data: foreign_key("customers", "customer_id")
      - column_name: customer_email
        data: copy_from_fk("customer_id", "customers", "email")
```

### Automatic attribute inference in action
[`yaml.declaration()`](table-faker/README.md:114)
```yaml
config:
  infer_entity_attrs_by_name: true
tables:
  - table_name: customers
    columns:
      - column_name: customer_id
        is_primary_key: true
        data: row_id
      - column_name: email
        data: fake.email()
  - table_name: orders
    columns:
      - column_name: customer_id
        data: foreign_key("customers", "customer_id")
      - column_name: customer_email
        data: auto  # Automatically resolved from the customer_id FK
```
- `data: auto` indicates that the value will be inferred by name from the referenced parent row when `infer_entity_attrs_by_name` is true.

## Foreign Key Distributions
Foreign keys support different sampling distributions to model realistic parent usage patterns.

### Uniform distribution (default)
[`yaml.declaration()`](table-faker/README.md:114)
```yaml
data: foreign_key("customers", "customer_id")
```
- Backward compatible: selects parent keys uniformly at random.

### Zipf (power-law) distribution
[`yaml.declaration()`](table-faker/README.md:114)
```yaml
data: foreign_key("customers", "customer_id", distribution="zipf", param=1.2)
```
- Produces head-heavy (long-tail) distributions where a few parents appear much more frequently.
- `param` controls concentration: higher values concentrate more on top-ranked parents.
- Useful for modeling popular customers, trending products, or social-systems with power-law behavior.

### Weighted parent distribution (attribute-based)
[`yaml.declaration()`](table-faker/README.md:114)
```yaml
data: foreign_key(
  "customers",
  "customer_id",
  distribution="weighted_parent",
  parent_attr="rating",
  weights={"5": 3, "4": 2, "3": 1}
)
```
- Weights are applied based on a parent attribute (here `rating`) so parents with certain attribute values are preferred.
- Any parent attribute value not listed in `weights` defaults to weight `1.0`.
- Useful to prefer high-rated customers, VIP tiers, or any attribute-driven bias.

## Complete example (seed, inference, weighted FK)
[`yaml.declaration()`](table-faker/README.md:114)
```yaml
version: 1
config:
  locale: en_US
  seed: 4242
  infer_entity_attrs_by_name: true

tables:
  - table_name: customers
    row_count: 100
    columns:
      - column_name: customer_id
        data: row_id
        is_primary_key: true
      - column_name: email
        data: fake.unique.email()
      - column_name: rating
        data: random.choice([3, 4, 5])

  - table_name: orders
    row_count: 500
    columns:
      - column_name: order_id
        data: row_id
        is_primary_key: true
      - column_name: customer_id
        data: foreign_key(
          "customers",
          "customer_id",
          distribution="weighted_parent",
          parent_attr="rating",
          weights={"5": 3, "4": 2, "3": 1}
        )
      - column_name: customer_email
        data: auto  # Inferred from customer_id FK
```

## Notes
- Parent tables must be defined before child tables (no automatic backfilling/topological sort yet).
- Two-phase row evaluation ensures column order within a table does not affect correctness (you can reference other columns freely).
- `fake.unique` behavior is deterministic only when the same `Faker` instance is reused and `config.seed` is fixed.
- All sampling distributions are deterministic given a fixed seed.
 
## Data Generation
You can define your dummy data generation logic in a Python function. The Faker, random and datetime packages are pre-imported and ready to use.

- Use the Faker package for realistic data, e.g., `fake.first_name()` or `fake.random_int(1, 10)`.
- Use the random package for basic randomness, e.g., `random.choice(["male", "female"])`.
- Use the datetime package for current date and time, e.g., `datetime.today().strftime('%Y-%m-%d')`.
- You can use a column to generate a new column, e.g., `first_name + " " + last_name`.
- Use is_primary_key to define a primary key, e.g., `is_primary_key: true`.
- Use foreign_key to get a primary key from another table, e.g., `foreign_key("person", "id")`. If you use multiple foreign key functions, you will get the primary key values from the same row.

You can write your logic in a single line or multiple lines, depending on your preference. A built-in function, `row_id`, provides a unique integer for each row. You can specify row_id starting point using the `start_row_id` keyword.

In addition, you have control over how your data is exported:

- **`export_file_count`**: This keyword lets you specify the total number of output files to generate. It's especially useful when you need to split a large dataset into multiple, more manageable files.
- **`export_file_row_count`**: Use this keyword to set the maximum number of rows that each exported file should contain. This ensures that each file remains within a desired size limit and is easier to handle.


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
You can use tablefaker in your terminal for ad-hoc needs or in shell scripts to automate fake data generation. The CLI reads the YAML config and supports importing Python modules via `config.python_import` and adding Faker community providers declared under `config.community_providers` (see "Custom Faker Providers" below). Custom Python functions (passed via the `custom_function` parameter) are only supported when using the Python API programmatically.

Supported CLI flags:
- --config : path to YAML or JSON config
- --file_type : csv,json,parquet,excel,sql,deltalake (default: csv)
- --target : target folder or file path
- --seed : integer seed to make generation deterministic
- --infer-attrs : "true" or "false" to override infer_entity_attrs_by_name

```bash
# exports to current folder in csv format (reads community_providers from config)
tablefaker --config tests/test_table.yaml

# exports as sql insert script files
tablefaker --config tests/test_table.yaml --file_type sql --target ./out

# exports to current folder in excel format
tablefaker --config tests/test_table.yaml --file_type excel

# exports all tables in json format to a folder
tablefaker --config tests/test_table.yaml --file_type json --target ./target_folder

# exports a single table to a parquet file
tablefaker --config tests/test_table.yaml --file_type parquet --target ./target_folder/target_file.parquet

# pass an explicit seed and enable attribute inference
tablefaker --config tests/test_table.yaml --seed 42 --infer-attrs true
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
## Generate Yaml File From Avro Schema or Csv
If you have an [avro schema](https://avro.apache.org/docs/++version++/specification/), you can generate a yaml file using avro_to_yaml function.

```python
from tablefaker import tablefaker
tablefaker.avro_to_yaml("tests/test_person.avsc", "tests/exports/person.yaml")
```

And also you can use csv to define your columns and generate the yaml file.

```python
from tablefaker import tablefaker
tablefaker.csv_to_yaml("tests/test_person.csv", "tests/exports/person.yaml")
```

Sample Csv file
```
column_name,description,data,type,null_percentage
id,Unique identifier for the person,row_id,,
first_name,First name of the person,fake.first_name(),string,
last_name,Last name of the person,fake.last_name(),string,
age,Age of the person,fake.random_int(),int32,0.1
email,Email address of the person,fake.email(),string,0.1
is_active,Indicates if the person is active,fake.pybool(),boolean,0.2
signup_date,Date when the person signed up,fake.date(),,0.3
```

## Support & Donation
If you find Table Faker useful and would like to support its development, consider making a [donation](https://github.com/sponsors/necatiarslan).

## Additional Resources
- **Faker Functions**: [Faker Providers](https://faker.readthedocs.io/en/master/providers.html#)
- **Bug Reports & Feature Requests**: [GitHub Issues](https://github.com/necatiarslan/table-faker/issues/new)


## Roadmap
### TODO
- Provide foreign keys (dictionary, array etc) as an external source
- Variables
- Generate template yaml file from sample data
- use an ai service to generate data generation logic
- make openpyxl package optional to export to excel
- look for need of psutils package

### Future Enhancements
- PyArrow table support
- Avro file support
- Add target file name to YAML

---
**Follow for Updates**: [LinkedIn](https://www.linkedin.com/in/necati-arslan/)  
**Author**: Necati Arslan | [Email](mailto:necatia@gmail.com)


