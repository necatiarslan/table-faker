import yaml
from os import path, makedirs
from . import config

def generate_relationships(config_source, target_file_path=None):

    """
    Generate a relationships YAML file derived from a tablefaker config.
    Only includes FK->PK relationships from foreign_key() calls.
    The output file is named <basename>_table_relationships.yml in the same dir
    as the input config unless target_file_path is provided.
    """
    # Load config (reuse existing Config class for validation/structure)
    if isinstance(config_source, str):
        conf = config.Config(config_source)
    elif isinstance(config_source, dict):
        conf = config.Config(config_source)
    else:
        raise Exception("Unsupported config source for relationships generation")

    tables = conf.config.get("tables", [])
    
    # Build a map of table -> primary_key_column for validation
    table_pks = {}
    for table in tables:
        table_name = table.get("table_name")
        for col in table.get("columns", []):
            if col.get("is_primary_key"):
                table_pks[table_name] = col.get("column_name")
                break
    
    # Collect FK relationships: (left_table, right_table) -> (left_fk_col, right_pk_col)
    fk_relationships = {}

    for table in tables:
        left_table = table.get("table_name")
        for col in table.get("columns", []):
            col_name = col.get("column_name")
            cmd = col.get("data")
            if isinstance(cmd, str) and "foreign_key(" in cmd:
                try:
                    idx = cmd.find('foreign_key(')
                    end_idx = cmd.find(')', idx)
                    if end_idx != -1:
                        args_str = cmd[idx + len('foreign_key('):end_idx]
                        parsed = eval(f"({args_str})")
                        # parsed: ("right_table", "right_col", ...)
                        if len(parsed) >= 2:
                            right_table = parsed[0]
                            right_col = parsed[1]
                            
                            # Only add if right_col is the PK of right_table
                            if right_table in table_pks and table_pks[right_table] == right_col:
                                key = (left_table, right_table)
                                # Store FK column -> PK column mapping
                                fk_relationships.setdefault(key, set()).add((col_name, right_col))
                except Exception:
                    pass

    # Build relationships output
    relationships = []
    for (left_table, right_table), col_pairs in fk_relationships.items():
        rel_name = f"{left_table}_to_{right_table}"
        rel = {
            "name": rel_name,
            "left_table": left_table,
            "right_table": right_table,
            "relationship_columns": [],
            "join_type": "left_outer",
            "relationship_type": "many_to_one"
        }
        # Add unique FK->PK mappings
        for left_col, right_col in sorted(col_pairs):
            rel["relationship_columns"].append({
                "left_column": left_col,
                "right_column": right_col
            })
        relationships.append(rel)

    out_struct = {"relationships": relationships}

    if isinstance(config_source, str):
        base = path.splitext(path.basename(config_source))[0]
        default_name = f"{base}_table_relationships.yml"
        src_dir = path.dirname(config_source) or "."
    else:
        default_name = "table_relationships.yml"
        src_dir = "."

    if target_file_path in (None, "", "."):
        out_path = path.join(src_dir, default_name)
    else:
        # if a directory was passed, write the derived filename inside it
        out_path = path.join(target_file_path, default_name) if path.isdir(target_file_path) else target_file_path

    # ensure parent directory exists
    makedirs(path.dirname(out_path) or ".", exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as outf:
        yaml.safe_dump(out_struct, outf, sort_keys=False)

    return out_path

