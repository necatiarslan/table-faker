---
name: tablefaker
description: Generate YAML configs for Tablefaker to create synthetic datasets with tables, relationships, and faker data.
---

# Skill: Tablefaker YAML Generator

## Purpose
Help an agent generate valid Tablefaker YAML configurations that follow the actual runtime behavior and schema constraints.

## Inputs
- User intent and domain (tables, relationships, volumes, locales)
- Optional constraints: determinism, distributions, plugin usage, LLM options

## Outputs
- YAML config (version 1) suitable for Tablefaker
- Short usage notes if requested

## Core Constraints
- Parent tables must be defined before child tables.
- Each table needs `table_name` and `columns`. Each column needs `column_name` and `data`.
- `is_primary_key: true` columns cannot use `null_percentage`.
- `data: auto` only works when `config.infer_entity_attrs_by_name` is true.
- Community providers use the format `module(ClassName)`.

## Schema Cheat Sheet
```yaml
version: 1
config:
  locale: en_US
  seed: 123
  infer_entity_attrs_by_name: true
  python_import:
    - some_module
  community_providers:
    - faker_education(SchoolProvider)

tables:
  - table_name: example
    row_count: 100
    start_row_id: 1
    export_file_count: 1
    export_file_row_count: 100
    columns:
      - column_name: id
        data: row_id
        is_primary_key: true
      - column_name: name
        data: fake.name()
        type: string
      - column_name: created_at
        data: datetime.today().strftime('%Y-%m-%d')
```

## Patterns and Examples

### Basic table with faker fields
```yaml
tables:
  - table_name: person
    row_count: 10
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
```

### Foreign key relationship
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

### Foreign key distributions
```yaml
  - table_name: orders_zipf
    row_count: 1000
    columns:
      - column_name: order_id
        data: row_id
        is_primary_key: true
      - column_name: customer_id
        data: foreign_key("customers", "customer_id", distribution="zipf", param=1.1)

  - table_name: orders_weighted
    row_count: 3000
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
```

### Automatic attribute inference (data: auto)
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

### Plugins and python_import
If you need custom logic, expose functions in a module and import it.

```yaml
config:
  python_import:
    - my_plugin

tables:
  - table_name: child
    row_count: 5
    columns:
      - column_name: parent_count
        data: my_plugin.get_parent_count(get_table)
```

## Agent Guidance
- Prefer short, readable `data` expressions; use a block (`|`) only when needed.
- Keep naming consistent to enable `data: auto` inference.
- Validate that FK parent tables appear earlier in the YAML.
- For reproducibility, set `config.seed`.
