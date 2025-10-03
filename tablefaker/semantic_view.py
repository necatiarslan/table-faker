import yaml
from os import path, makedirs
from . import config
from .llm_client import LLMClient
from typing import Dict, List, Any, Optional
import re

def generate_semantic_view(config_source, target_file_path=None, llm_config_path=None):
    """
    Generate a semantic view YAML file from a tablefaker config.
    
    Args:
        config_source: Path to tablefaker config file or dict
        target_file_path: Optional path to write YAML (default: same dir as config)
        llm_config_path: Optional path to llm.config file (default: looks for llm.config in current dir)
    
    Returns:
        Path to generated semantic view YAML file
    """
    
    # Initialize LLM client
    llm_client = LLMClient(llm_config_path)
    
    # Load config
    if isinstance(config_source, str):
        conf = config.Config(config_source)
    elif isinstance(config_source, dict):
        conf = config.Config(config_source)
    else:
        raise Exception("Unsupported config source for semantic view generation")
    
    tables = conf.config.get("tables", [])
    
    # Build table metadata
    table_metadata = _extract_table_metadata(tables)
    
    # Build relationships from foreign keys
    relationships = _extract_relationships(tables)
    
    # Generate semantic model structure
    semantic_model = _build_semantic_model(table_metadata, relationships, llm_client)
    
    # Determine output path
    if isinstance(config_source, str):
        base = path.splitext(path.basename(config_source))[0]
        default_name = f"{base}_semantic_view.yml"
        src_dir = path.dirname(config_source) or "."
    else:
        default_name = "semantic_view.yml"
        src_dir = "."
    
    if target_file_path in (None, "", "."):
        out_path = path.join(src_dir, default_name)
    else:
        out_path = path.join(target_file_path, default_name) if path.isdir(target_file_path) else target_file_path
    
    # Ensure parent directory exists
    makedirs(path.dirname(out_path) or ".", exist_ok=True)
    
    # Write YAML
    with open(out_path, "w", encoding="utf-8") as outf:
        yaml.safe_dump(semantic_model, outf, sort_keys=False, default_flow_style=False, allow_unicode=True)
    
    return out_path


def _extract_table_metadata(tables: List[Dict]) -> Dict[str, Dict]:
    """Extract metadata for each table including columns and their types."""
    metadata = {}
    
    for table in tables:
        table_name = table.get("table_name")
        columns = table.get("columns", [])
        
        table_info = {
            "table_name": table_name,
            "row_count": table.get("row_count", 10),
            "primary_keys": [],
            "columns": []
        }
        
        for col in columns:
            col_name = col.get("column_name")
            col_type = col.get("type", "string")
            data_expr = str(col.get("data", ""))
            is_pk = col.get("is_primary_key", False)
            
            col_info = {
                "column_name": col_name,
                "type": col_type,
                "data_expression": data_expr,
                "is_primary_key": is_pk,
                "is_foreign_key": "foreign_key(" in data_expr,
                "references_column": "copy_from_fk(" in data_expr or any(c in data_expr for c in [col_name] if col_name != col.get("column_name")),
                "null_percentage": col.get("null_percentage", 0)
            }
            
            # Extract foreign key reference if present
            if col_info["is_foreign_key"]:
                fk_match = re.search(r'foreign_key\(["\'](\w+)["\']\s*,\s*["\'](\w+)["\']\)', data_expr)
                if fk_match:
                    col_info["fk_table"] = fk_match.group(1)
                    col_info["fk_column"] = fk_match.group(2)
            
            table_info["columns"].append(col_info)
            
            if is_pk:
                table_info["primary_keys"].append(col_name)
        
        metadata[table_name] = table_info
    
    return metadata


def _extract_relationships(tables: List[Dict]) -> List[Dict]:
    """Extract relationships based on foreign_key() calls."""
    relationships = []
    seen = set()
    
    # Build PK map
    table_pks = {}
    for table in tables:
        table_name = table.get("table_name")
        for col in table.get("columns", []):
            if col.get("is_primary_key"):
                table_pks[table_name] = col.get("column_name")
                break
    
    # Extract FK relationships
    for table in tables:
        left_table = table.get("table_name")
        
        for col in table.get("columns", []):
            col_name = col.get("column_name")
            cmd = str(col.get("data", ""))
            
            if "foreign_key(" in cmd:
                fk_match = re.search(r'foreign_key\(["\'](\w+)["\']\s*,\s*["\'](\w+)["\']\)', cmd)
                if fk_match:
                    right_table = fk_match.group(1)
                    right_col = fk_match.group(2)
                    
                    # Only add if right_col is the PK of right_table
                    if right_table in table_pks and table_pks[right_table] == right_col:
                        rel_key = (left_table, right_table, col_name, right_col)
                        if rel_key not in seen:
                            seen.add(rel_key)
                            relationships.append({
                                "name": f"{left_table}_to_{right_table}",
                                "left_table": left_table,
                                "right_table": right_table,
                                "left_column": col_name,
                                "right_column": right_col,
                                "join_type": "left_outer",
                                "relationship_type": "many_to_one"
                            })
    
    return relationships


def _classify_column(col_info: Dict, table_name: str, llm_client: LLMClient) -> str:
    """
    Classify a column as dimension, time_dimension, or fact.
    
    Rules:
    - Primary keys -> dimension (with unique=true)
    - Foreign keys -> dimension
    - Date/datetime types -> time_dimension
    - Numeric types (int, float) that look like measurements -> fact
    - Boolean, string, categorical -> dimension
    """
    col_name = col_info["column_name"]
    col_type = col_info.get("type", "string")
    data_expr = col_info.get("data_expression", "")
    
    # Primary keys are always dimensions
    if col_info.get("is_primary_key"):
        return "dimension"
    
    # Foreign keys are always dimensions
    if col_info.get("is_foreign_key"):
        return "dimension"
    
    # Date/time columns
    if col_type in ["date", "datetime", "timestamp", "time"]:
        return "time_dimension"
    
    # Check column name patterns for dates
    date_patterns = ["date", "time", "created", "updated", "modified", "datetime", "timestamp", "_at", "_on"]
    if any(pattern in col_name.lower() for pattern in date_patterns):
        return "time_dimension"
    
    # Numeric types - need to distinguish between facts and dimensions
    if col_type in ["int32", "int64", "float", "double", "decimal", "number"]:
        # Check if it's a count, amount, total, rate, score, or other measurement
        fact_patterns = [
            "amount", "total", "sum", "count", "price", "cost", "rate", "salary", 
            "revenue", "profit", "tax", "fee", "charge", "payment", "balance",
            "quantity", "points", "score", "rating", "capacity", "length", "nights",
            "adults", "children", "subtotal", "discount", "weight", "height"
        ]
        
        # Check if it's likely a dimension (ID-like, enum-like)
        dimension_patterns = ["_id", "number", "floor", "level", "type", "status", "year", "month", "day"]
        
        if any(pattern in col_name.lower() for pattern in fact_patterns):
            return "fact"
        elif any(pattern in col_name.lower() for pattern in dimension_patterns):
            return "dimension"
        
        # Default numeric to fact unless it looks like an identifier
        if "id" in col_name.lower() or "number" in col_name.lower():
            return "dimension"
        else:
            return "fact"
    
    # Boolean and string types are dimensions
    if col_type in ["boolean", "bool", "string", "text", "varchar", "char"]:
        return "dimension"
    
    # Default to dimension
    return "dimension"


def _infer_data_type(col_type: str) -> str:
    """Map tablefaker types to Snowflake SQL types."""
    type_mapping = {
        "string": "VARCHAR",
        "text": "VARCHAR",
        "int32": "NUMBER",
        "int64": "NUMBER",
        "float": "FLOAT",
        "double": "FLOAT",
        "decimal": "DECIMAL",
        "boolean": "BOOLEAN",
        "bool": "BOOLEAN",
        "date": "DATE",
        "datetime": "TIMESTAMP",
        "timestamp": "TIMESTAMP",
        "time": "TIME",
    }
    return type_mapping.get(col_type, "VARCHAR")


def _generate_description_with_llm(table_name: str, col_name: str, col_type: str,
                                    data_expr: str, classification: str,
                                    llm_client: LLMClient) -> str:
    """Generate a description using LLM if available and enabled."""
    if not llm_client.is_enabled():
        return f"The {col_name} column in {table_name}"
    
    try:
        description = llm_client.generate_column_description(
            table_name, col_name, col_type, data_expr, classification
        )
        return description
    except Exception as e:
        print(f"Warning: LLM call failed for {table_name}.{col_name}: {str(e)}")
        return f"The {col_name} column in {table_name}"


def _build_semantic_model(table_metadata: Dict, relationships: List[Dict],
                          llm_client: LLMClient) -> Dict:
    """Build the complete semantic model structure."""
    
    # Generate model name from first table
    first_table = list(table_metadata.keys())[0] if table_metadata else "model"
    model_name = f"{first_table}_semantic_model"
    
    # Generate model description with LLM
    if llm_client.is_enabled():
        try:
            model_description = llm_client.generate_model_description(list(table_metadata.keys()))
        except Exception as e:
            print(f"Warning: LLM call failed for model description: {str(e)}")
            model_description = f"Semantic model containing {len(table_metadata)} tables"
    else:
        model_description = f"Semantic model containing {len(table_metadata)} tables"
    
    semantic_model = {
        "name": model_name,
        "description": model_description,
        "tables": []
    }
    
    # Build logical tables
    for table_name, table_info in table_metadata.items():
        # Generate table description with LLM
        if llm_client.is_enabled():
            try:
                col_names = [col["column_name"] for col in table_info["columns"]]
                table_desc = llm_client.generate_table_description(table_name, col_names)
            except Exception as e:
                print(f"Warning: LLM call failed for table {table_name}: {str(e)}")
                table_desc = f"Logical table for {table_name}"
        else:
            table_desc = f"Logical table for {table_name}"
        
        logical_table = {
            "name": table_name,
            "description": table_desc,
            "base_table": {
                "database": "<database>",
                "schema": "<schema>",
                "table": table_name
            }
        }
        
        # Add primary key if exists
        if table_info["primary_keys"]:
            logical_table["primary_key"] = {
                "columns": table_info["primary_keys"]
            }
        
        # Classify and organize columns
        dimensions = []
        time_dimensions = []
        facts = []
        
        for col_info in table_info["columns"]:
            classification = _classify_column(col_info, table_name, llm_client)
            col_name = col_info["column_name"]
            col_type = col_info.get("type", "string")
            data_expr = col_info.get("data_expression", "")
            
            # Generate description
            description = _generate_description_with_llm(
                table_name, col_name, col_type, data_expr,
                classification, llm_client
            )
            
            col_def = {
                "name": col_name,
                "description": description,
                "expr": col_name,  # Simple column reference
                "data_type": _infer_data_type(col_type)
            }
            
            # Add unique flag for primary keys
            if col_info.get("is_primary_key"):
                col_def["unique"] = True
            
            # Add to appropriate list
            if classification == "dimension":
                dimensions.append(col_def)
            elif classification == "time_dimension":
                time_dimensions.append(col_def)
            elif classification == "fact":
                facts.append(col_def)
        
        # Add column sections to logical table
        if dimensions:
            logical_table["dimensions"] = dimensions
        
        if time_dimensions:
            logical_table["time_dimensions"] = time_dimensions
        
        if facts:
            logical_table["facts"] = facts
        
        semantic_model["tables"].append(logical_table)
    
    # Add relationships if any
    if relationships:
        rel_list = []
        for rel in relationships:
            rel_def = {
                "name": rel["name"],
                "left_table": rel["left_table"],
                "right_table": rel["right_table"],
                "relationship_columns": [
                    {
                        "left_column": rel["left_column"],
                        "right_column": rel["right_column"]
                    }
                ],
                "join_type": rel["join_type"],
                "relationship_type": rel["relationship_type"]
            }
            rel_list.append(rel_def)
        
        semantic_model["relationships"] = rel_list
    
    return semantic_model