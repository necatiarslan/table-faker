---
name: tablefaker
description: Generate valid Tablefaker YAML for synthetic datasets with tables, relationships, deterministic seeding, imports, and export formats.
---

# Skill: Tablefaker YAML Generator

## Purpose
Generate YAML that matches the actual Tablefaker runtime used in this repository: valid schemas for synthetic datasets, table-to-table relationships, deterministic generation, and export behavior.

## Inputs
- User intent: dataset shape, table names, row counts, relationships, domain
- Optional constraints: locale, seed, null percentages, custom providers, chunked exports, parquet schema
- Optional output target: pandas, CSV, SQL, JSON, Parquet, Excel, or Delta Lake

## Outputs
- A valid YAML config for Tablefaker (`version: 1`)
- The YAML should be concrete and executable, not speculative
- When requested, a short explanation of the pattern or export behavior

## Verified project behavior
This project supports the following runtime behaviors, based on the README and tests:

### Config keys
```yaml
version: 1
config:
  locale: en_US
  seed: 42
  infer_entity_attrs_by_name: true
  python_import:
    - dateutil
    - faker_education
  community_providers:
    - faker_education(SchoolProvider)
```

- `config.seed` makes repeated runs deterministic for the same YAML.
- `config.infer_entity_attrs_by_name: true` enables `data: auto` name-based inference.
- `python_import` imports modules available in `data` expressions.
- `community_providers` uses the format `module(ClassName)`.

### Table-level fields
```yaml
tables:
  - table_name: person
    row_count: 100
    start_row_id: 10
    export_file_count: 3
    export_file_row_count: 50
    export_file_name: person_export
```

- `row_count` defines generated rows.
- `start_row_id` sets the starting row identifier.
- `export_file_count` controls chunking when exporting to multiple files.
- `export_file_row_count` is an alternate chunking rule.
- `export_file_name` sets the output filename stem without the extension.

### Column-level fields
```yaml
columns:
  - column_name: id
    data: row_id
    is_primary_key: true
  - column_name: age
    data: fake.random_int(18, 90)
    type: int32
    null_percentage: 0.1
    parquet_type: int32
```

- Each column requires `column_name` and `data`.
- `data` may be a Faker call, random expression, literal, `row_id`, `None`, a column reference, or a multiline Python block.
- `is_primary_key: true` is valid for row IDs and foreign-key sources.
- `null_percentage` is allowed for non-primary-key columns.
- `type` controls pandas dtype casting.
- `parquet_type` sets the Arrow/Parquet schema when exporting parquet.
- `description` is also accepted by the schema.

## Data-expression rules
Use only values and functions available in the actual evaluation context:

- `fake`, `random`, `datetime`, `date`, `timedelta`, `time`, `timezone`, `tzinfo`, `UTC`, `MINYEAR`, `MAXYEAR`, `math`, `string`, `row_id`
- Special helper functions:
  - `foreign_key(parent_table, parent_column, distribution="uniform", param=None, parent_attr=None, weights=None, is_unique=False)`
  - `copy_from_fk(parent_table, foreign_key_column, parent_attr)`

Examples:
```yaml
- column_name: full_name
  data: first_name + " " + last_name
- column_name: today
  data: datetime.today().strftime('%Y-%m-%d')
- column_name: discount_eligibility
  data: |
    if age < 25 or age > 60:
      return True
    else:
      return False
```

## Relationship patterns that are supported

### Basic parent/child foreign key
```yaml
tables:
  - table_name: customers
    row_count: 10
    columns:
      - column_name: customer_id
        data: row_id
        is_primary_key: true
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
        data: copy_from_fk("customers", "customer_id", "email")
```

### Distribution-aware foreign keys
```yaml
- column_name: customer_id
  data: foreign_key("customers", "customer_id", distribution="zipf", param=1.1)
- column_name: customer_id
  data: foreign_key(
    "customers",
    "customer_id",
    distribution="weighted_parent",
    parent_attr="rating",
    weights={"5": 3, "4": 2, "3": 1}
  )
```

### Unique foreign key (one-to-one)
```yaml
- table_name: managers
  row_count: 20
  columns:
    - column_name: manager_id
      data: row_id
      is_primary_key: true
    - column_name: dept_id
      data: foreign_key("departments", "dept_id", is_unique=True)
```

Rules:
- Parent tables must appear before child tables in the YAML.
- `is_unique=True` means each parent key is used at most once by that child table.
- The child `row_count` cannot exceed the parent `row_count` for a one-to-one relationship.

### Auto attribute inference
```yaml
config:
  infer_entity_attrs_by_name: true

tables:
  - table_name: customers
    columns:
      - column_name: customer_id
        data: row_id
        is_primary_key: true
      - column_name: email
        data: fake.email()
  - table_name: orders
    columns:
      - column_name: customer_id
        data: foreign_key("customers", "customer_id")
      - column_name: customer_email
        data: auto
```

`data: auto` is only valid when `config.infer_entity_attrs_by_name` is true. It resolves to copy-from-parent logic based on matching attribute names.

## Export and schema details
Tablefaker supports multiple output formats:
- pandas DataFrame
- SQL insert script
- CSV
- Parquet
- JSON
- Excel
- Delta Lake

For parquet exports:
- `parquet_type` is applied at export time to the Arrow/Parquet schema.
- `type` still affects the pandas dtype and can differ from `parquet_type`.
- `parquet_type` is ignored for non-parquet exports.
- Supported values include `int8`, `int16`, `int32`, `int64`, `uint8`–`uint64`, `float16`, `float32`, `float64`, `double`, `string`, `utf8`, `large_string`, `binary`, `large_binary`, `bool`, `boolean`, `date32`, `date64`, `timestamp[s/ms/us/ns]`, `time32[s/ms]`, `time64[us/ns]`, and `decimal128(precision, scale)`.

## Additional constraints and pitfalls
- Parent tables must be defined before child tables.
- `is_primary_key: true` columns cannot have `null_percentage`.
- Do not reference a parent table that appears later in the YAML.
- Prefer short, readable `data` expressions; use a YAML block scalar only when necessary.
- For reproducibility, set `config.seed`.
- `fake.unique.*` and fixed seeds are supported; tests verify deterministic repeated generation.
- Two-phase evaluation is supported: dependent columns can resolve after earlier parent-generated values are available, even when the order in the YAML is not naturally topological.

## Reference example
```yaml
version: 1
config:
  locale: en_US
  seed: 123
  python_import:
    - dateutil
    - faker_education
  community_providers:
    - faker_education(SchoolProvider)

tables:
  - table_name: person
    row_count: 100
    start_row_id: 10
    columns:
      - column_name: id
        data: row_id
        is_primary_key: true
      - column_name: first_name
        data: fake.first_name()
      - column_name: last_name
        data: fake.last_name()
      - column_name: full_name
        data: first_name + " " + last_name
      - column_name: gender
        data: random.choice(["male", "female"])
        null_percentage: 0.5
      - column_name: today
        data: datetime.today().strftime('%Y-%m-%d')
      - column_name: discount_eligibility
        data: |
          if age < 25 or age > 60:
            return True
          else:
            return False

  - table_name: employee
    row_count: 10
    columns:
      - column_name: id
        data: row_id
      - column_name: person_id
        data: foreign_key("person", "id")
      - column_name: full_name
        data: foreign_key("person", "full_name")
      - column_name: salary
        data: None
        type: float
      - column_name: school
        data: fake.school_district()
```

This skill should favor YAML that matches the current project behavior and avoids unsupported patterns.

## Source grounding
The rules above were verified against the project README and the real tests under `tests/`, especially the determinism, foreign-key, two-phase, unique-FK, parquet, and CLI validations.
