"""
Generate model-level business metrics from a semantic view YAML using LLM.
"""
import yaml
from os import path
from .llm_client import LLMClient
from typing import Dict, List, Any, Optional
import re


def generate_model_metrics(semantic_view_path: str, llm_config_path: Optional[str] = None,
                           num_metrics: int = 10, target_file_path: Optional[str] = None) -> str:
    """
    Generate model-level business metrics from a semantic view YAML.
    
    Args:
        semantic_view_path: Path to the semantic view YAML file
        llm_config_path: Optional path to llm.config file
        num_metrics: Number of metrics to generate (default: 10)
        target_file_path: Optional path to write metrics YAML (default: same dir as semantic view)
    
    Returns:
        Path to generated metrics YAML file
    """
    
    # Initialize LLM client
    llm_client = LLMClient(llm_config_path)
    
    if not llm_client.is_enabled():
        raise RuntimeError(
            "LLM is not enabled. Please configure llm.config with enabled: true "
            "and proper API credentials to generate metrics."
        )
    
    # Load semantic view
    with open(semantic_view_path, "r", encoding="utf-8") as f:
        semantic_view = yaml.safe_load(f)
    
    # Analyze the semantic model
    model_summary = _analyze_semantic_model(semantic_view)
    
    # Generate metrics using LLM
    metrics = _generate_metrics_with_llm(model_summary, llm_client, num_metrics)
    
    # Determine output path
    base = path.splitext(path.basename(semantic_view_path))[0]
    default_name = f"{base}_generated_metrics.yml"
    src_dir = path.dirname(semantic_view_path) or "."
    
    if target_file_path in (None, "", "."):
        out_path = path.join(src_dir, default_name)
    else:
        out_path = path.join(target_file_path, default_name) if path.isdir(target_file_path) else target_file_path
    
    # Write metrics YAML
    metrics_yaml = {
        "metrics": metrics,
        "comments": f"Generated {len(metrics)} business metrics using LLM analysis of the semantic model"
    }
    
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(metrics_yaml, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
    
    return out_path


def _analyze_semantic_model(semantic_view: Dict) -> Dict[str, Any]:
    """Analyze semantic model to extract key information for metric generation."""
    
    model_summary = {
        "model_name": semantic_view.get("name", "unknown"),
        "model_description": semantic_view.get("description", ""),
        "tables": {},
        "relationships": []
    }
    
    # Extract table information
    for table in semantic_view.get("tables", []):
        table_name = table.get("name")
        table_info = {
            "description": table.get("description", ""),
            "dimensions": [],
            "time_dimensions": [],
            "facts": [],
            "metrics": []
        }
        
        # Extract dimensions
        for dim in table.get("dimensions", []):
            table_info["dimensions"].append({
                "name": dim.get("name"),
                "description": dim.get("description", ""),
                "data_type": dim.get("data_type")
            })
        
        # Extract time dimensions
        for tdim in table.get("time_dimensions", []):
            table_info["time_dimensions"].append({
                "name": tdim.get("name"),
                "description": tdim.get("description", ""),
                "data_type": tdim.get("data_type")
            })
        
        # Extract facts
        for fact in table.get("facts", []):
            table_info["facts"].append({
                "name": fact.get("name"),
                "description": fact.get("description", ""),
                "data_type": fact.get("data_type"),
                "expr": fact.get("expr")
            })
        
        # Extract table-level metrics
        for metric in table.get("metrics", []):
            table_info["metrics"].append({
                "name": metric.get("name"),
                "description": metric.get("description", ""),
                "expr": metric.get("expr")
            })
        
        model_summary["tables"][table_name] = table_info
    
    # Extract relationships
    for rel in semantic_view.get("relationships", []):
        model_summary["relationships"].append({
            "name": rel.get("name"),
            "left_table": rel.get("left_table"),
            "right_table": rel.get("right_table"),
            "relationship_type": rel.get("relationship_type")
        })
    
    # Industry detection: prefer explicit key, otherwise infer from model/table names and descriptions
    industry = semantic_view.get("industry", "") or semantic_view.get("domain", "") or ""
    if not industry:
        combined_parts = [
            model_summary.get("model_name", ""),
            model_summary.get("model_description", "")
        ]
        for t in semantic_view.get("tables", []):
            combined_parts.append(t.get("name", ""))
            combined_parts.append(t.get("description", ""))
        combined_text = " ".join(combined_parts).lower()
        hotel_keywords = ["hotel", "reservation", "room", "booking", "occupancy", "adr", "revpar", "rooms_sold", "rooms_available"]
        if any(k in combined_text for k in hotel_keywords):
            industry = "Hospitality"
    
    model_summary["industry"] = industry
    
    return model_summary


def _generate_metrics_with_llm(model_summary: Dict, llm_client: LLMClient, num_metrics: int) -> List[Dict]:
    """Use LLM to generate business metrics based on model analysis in 4 steps."""
    
    all_metrics = []
    
    # Step 1: Deduce industry from model name and description
    industry = _detect_industry_with_llm(model_summary, llm_client)
    model_summary["industry"] = industry
    
    # Step 2: Generate key industry-standard KPIs (without model metadata)
    industry_kpis = _generate_industry_kpis_with_llm(model_summary, llm_client)
    all_metrics.extend(industry_kpis)
    
    # Step 3: Generate simple metrics from model metadata (sum, avg, count)
    simple_metrics = _generate_simple_metrics_with_llm(model_summary, llm_client, num_metrics // 2)
    all_metrics.extend(simple_metrics)
    
    # Step 4: Generate advanced metrics by combining the above
    advanced_metrics = _generate_advanced_metrics_with_llm(
        model_summary, llm_client, industry_kpis, simple_metrics, num_metrics - len(all_metrics)
    )
    all_metrics.extend(advanced_metrics)
    
    # Validate and enhance all metrics
    all_metrics = _validate_and_enhance_metrics(all_metrics, model_summary)
    
    return all_metrics[:num_metrics]


def _detect_industry_with_llm(model_summary: Dict, llm_client: LLMClient) -> str:
    """Step 1: Deduce industry using only model name and description."""
    
    model_name = model_summary.get("model_name", "")
    model_description = model_summary.get("model_description", "")
    
    system_prompt = """You are an industry classification expert. Based on a semantic model's name and description, identify the specific industry or business domain."""
    
    user_prompt = f"""Identify the industry/business domain for this semantic model:

Model Name: {model_name}
Model Description: {model_description}

Return ONLY the industry name (e.g., "Hospitality", "Retail", "Healthcare", "Finance", "E-commerce", etc.).
Be specific and use standard industry terminology. Return just the industry name, nothing else."""
    
    try:
        industry = llm_client.generate(user_prompt, system_prompt).strip()
        # Clean up any quotes or extra text
        industry = industry.strip('"\'').split('\n')[0].strip()
        return industry
    except Exception as e:
        print(f"Warning: Failed to detect industry: {e}")
        return ""


def _generate_industry_kpis_with_llm(model_summary: Dict, llm_client: LLMClient) -> List[Dict]:
    """Step 2: Generate key industry-standard KPIs without model metadata."""
    
    industry = model_summary.get("industry", "")
    if not industry:
        return []
    
    system_prompt = """You are a business metrics expert. Generate industry-standard KPIs that are universally recognized for the given industry.
These should be the TOP metrics that every professional in this industry would expect to see.

CRITICAL CONSTRAINTS:
- Return metrics in abstract form (metric name and description only)
- Do NOT include expressions yet (we'll map to actual data later)
- Use standard industry terminology
- Focus on the  most critical KPIs for this industry"""
    
    user_prompt = f"""List the key industry-standard metrics for the {industry} industry.
    
    Return ONLY a YAML list in this format (ensure all description strings are double-quoted):
    ```yaml
    - name: metric_name
      description: "Clear business description of what this metric measures"
    ```
    
    Ensure all description strings are double-quoted. Include only the most critical metrics that every {industry} business tracks."""
    
    try:
        response = llm_client.generate(user_prompt, system_prompt)
        kpis = _parse_metrics_from_response(response)
        return kpis
    except Exception as e:
        print(f"Warning: Failed to generate industry KPIs: {e}")
        return []


def _generate_simple_metrics_with_llm(model_summary: Dict, llm_client: LLMClient, count: int) -> List[Dict]:
    """Step 3: Generate simple metrics using model metadata (sum, avg, count)."""
    
    context = _build_simple_metrics_context(model_summary)
    
    system_prompt = """You are a data analyst. Generate simple aggregate metrics from available data.

CRITICAL CONSTRAINTS:
- Metric expressions can ONLY contain single aggregate functions (SUM, AVG, COUNT, MAX, MIN)
- Reference logical columns using qualified names: table_name.column_name
- NO complex calculations, ratios, or multiple aggregates
- NO SELECT, FROM, JOIN, or WHERE clauses

Valid Examples:
✓ SUM(invoice.total)
✓ AVG(reservation.stay_length)
✓ COUNT(DISTINCT customer.customer_id)

Invalid Examples:
✗ SUM(a.x) / SUM(b.y)  (too complex, multiple aggregates)
✗ SELECT SUM(x) FROM table"""
    
    user_prompt = f"""Generate {count} simple aggregate metrics from this data:
    
    {context}
    
    For each fact column, create appropriate simple metrics:
    - SUM for monetary amounts, quantities, counts
    - AVG for rates, durations, measurements
    - COUNT for record counts
    
    Return YAML in this format (ensure all description strings are double-quoted):
    ```yaml
    - name: metric_name
      description: "Description"
      expr: Single aggregate expression (e.g., SUM(table.column))
    ```
    
    Ensure all description strings are double-quoted."""
    
    try:
        response = llm_client.generate(user_prompt, system_prompt)
        metrics = _parse_metrics_from_response(response)
        return metrics
    except Exception as e:
        print(f"Warning: Failed to generate simple metrics: {e}")
        return []


def _generate_advanced_metrics_with_llm(
    model_summary: Dict, llm_client: LLMClient,
    industry_kpis: List[Dict], simple_metrics: List[Dict], count: int
) -> List[Dict]:
    """Step 4: Generate advanced metrics by combining industry KPIs with simple metrics."""
    
    context = _build_metrics_context(model_summary)
    
    # Build reference to available simple metrics
    simple_metrics_ref = "\n".join([
        f"- {m.get('name')}: {m.get('expr', '')}"
        for m in simple_metrics if m.get('expr')
    ])
    
    # Build reference to industry KPIs that need implementation
    industry_kpis_ref = "\n".join([
        f"- {kpi.get('name')}: {kpi.get('description', '')}"
        for kpi in industry_kpis
    ])
    
    system_prompt = """You are a business intelligence expert. Create advanced calculated metrics by:
1. Implementing industry-standard KPIs using available data
2. Combining simple metrics into ratios, percentages, and derived values

CRITICAL CONSTRAINTS:
- Use ONLY aggregate expressions (SUM, AVG, COUNT, etc.) - combine multiple aggregates if needed
- Reference logical columns using qualified names: table_name.column_name
- Use NULLIF for division to avoid divide-by-zero errors
- NO SELECT, FROM, JOIN, or WHERE clauses

Valid Examples:
✓ SUM(invoice.total) / NULLIF(COUNT(DISTINCT reservation.reservation_id), 0)
✓ SUM(reservation.room_rate * reservation.stay_length) / NULLIF(SUM(reservation.stay_length), 0)"""
    
    user_prompt = f"""Generate {count} advanced calculated metrics.
    
    PRIORITY 1: Implement these industry-standard KPIs using the available data:
    {industry_kpis_ref}
    
    PRIORITY 2: Create additional calculated metrics by combining data intelligently.
    
    Available data model:
    {context}
    
    Available simple metrics for reference:
    {simple_metrics_ref}
    
    Generate expressions that:
    1. Map industry KPIs to actual columns (e.g., ADR = room revenue / room nights)
    2. Create meaningful ratios and percentages
    3. Combine aggregates intelligently
    4. Use NULLIF to handle division safely
    
    Return YAML in this format (ensure all description strings are double-quoted):
    ```yaml
    - name: metric_name
      description: "Clear business description"
      expr: Aggregate expression using table.column references
    ```
    
    Ensure all description strings are double-quoted."""
    
    try:
        response = llm_client.generate(user_prompt, system_prompt)
        metrics = _parse_metrics_from_response(response)
        return metrics
    except Exception as e:
        print(f"Warning: Failed to generate advanced metrics: {e}")
        return []


def _build_simple_metrics_context(model_summary: Dict) -> str:
    """Build context focused on facts for simple metric generation."""
    
    context_parts = []
    
    for table_name, table_info in model_summary["tables"].items():
        if table_info.get("facts"):
            context_parts.append(f"\n{table_name}:")
            context_parts.append("  Facts:")
            for fact in table_info["facts"]:
                context_parts.append(
                    f"    - {fact.get('name')} ({fact.get('data_type')}): {fact.get('description', '')[:100]}"
                )
    
    return "\n".join(context_parts)


def _build_metrics_context(model_summary: Dict) -> str:
    """Build a concise context string for the LLM."""
    
    context_parts = []
    
    # Model description
    context_parts.append(f"Model: {model_summary.get('model_name', '')}")
    context_parts.append(f"Description: {model_summary.get('model_description', '')}")
    # Include detected industry if present
    if model_summary.get("industry"):
        context_parts.append(f"Industry: {model_summary.get('industry')}")
    context_parts.append("")
    
    # Tables with their facts
    context_parts.append("Available Tables and Facts:")
    for table_name, table_info in model_summary["tables"].items():
        context_parts.append(f"\n{table_name}:")
        context_parts.append(f"  Description: {table_info.get('description', '')[:200]}")
        
        if table_info.get("facts"):
            context_parts.append("  Facts:")
            for fact in table_info["facts"]:
                context_parts.append(f"    - {fact.get('name')} ({fact.get('data_type')}): {fact.get('description','')[:100]}")
        
        if table_info.get("time_dimensions"):
            context_parts.append("  Time Dimensions:")
            for tdim in table_info["time_dimensions"]:
                context_parts.append(f"    - {tdim.get('name')}")
    
    # Relationships
    if model_summary.get("relationships"):
        context_parts.append("\nRelationships:")
        for rel in model_summary["relationships"]:
            context_parts.append(f"  - {rel.get('left_table')} -> {rel.get('right_table')} ({rel.get('relationship_type')})")
    
    return "\n".join(context_parts)


def _parse_metrics_from_response(response: str) -> List[Dict]:
    """Parse metric definitions from LLM response. Includes sanitizer fallback for malformed YAML."""
    
    # Try to extract YAML block if present
    if "```yaml" in response:
        start = response.find("```yaml") + 7
        end = response.find("```", start)
        yaml_content = response[start:end].strip()
    elif "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        yaml_content = response[start:end].strip()
    else:
        yaml_content = response.strip()
    
    def try_load(content: str):
        try:
            metrics = yaml.safe_load(content)
            if isinstance(metrics, list):
                return metrics
            elif isinstance(metrics, dict) and "metrics" in metrics:
                return metrics["metrics"]
            else:
                return [metrics] if metrics else []
        except yaml.YAMLError:
            return None
    
    # First attempt: raw load
    parsed = try_load(yaml_content)
    if parsed is not None:
        return parsed
    
    print("Warning: Failed to parse LLM response as YAML, attempting sanitizer fallback.")
    
    # Sanitizer: quote unquoted description values to avoid colon/formatting issues
    lines = yaml_content.splitlines()
    sanitized_lines = []
    desc_pattern = re.compile(r'^(\s*description:\s*)(.+)$', flags=re.IGNORECASE)
    for line in lines:
        m = desc_pattern.match(line)
        if m:
            val = m.group(2).strip()
            # If already quoted, keep as is
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                new_line = line
            else:
                # Escape existing double quotes
                val_escaped = val.replace('"', '\\"')
                new_line = f"{m.group(1)}\"{val_escaped}\""
            sanitized_lines.append(new_line)
        else:
            sanitized_lines.append(line)
    
    sanitized_content = "\n".join(sanitized_lines)
    parsed = try_load(sanitized_content)
    if parsed is not None:
        return parsed
    
    # As a last resort, attempt to extract simple "- name: ..." blocks heuristically
    simple_metrics = []
    current = {}
    for line in sanitized_lines:
        stripped = line.strip()
        if stripped.startswith("- name:"):
            if current:
                simple_metrics.append(current)
            current = {"name": stripped[len("- name:"):].strip().strip('"').strip("'")}
        elif stripped.startswith("description:") and current is not None:
            desc_val = stripped[len("description:"):].strip()
            desc_val = desc_val.strip('"').strip("'")
            current["description"] = desc_val
        elif stripped.startswith("expr:") and current is not None:
            expr_val = stripped[len("expr:"):].strip()
            current["expr"] = expr_val
    if current:
        simple_metrics.append(current)
    
    return simple_metrics


def _validate_and_enhance_metrics(metrics: List[Dict], model_summary: Dict) -> List[Dict]:
    """Validate metric structure and add missing fields."""
    
    validated = []
    
    for i, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            continue
        
        # Ensure required fields
        if "name" not in metric or "expr" not in metric:
            continue
        
        validated_metric = {
            "name": metric["name"],
            "description": metric.get("description", f"Business metric: {metric['name']}"),
            "expr": metric["expr"]
        }
        
        # Add synonyms if not present
        if "synonyms" not in metric:
            # Generate simple synonym from name
            name_parts = metric["name"].replace("_", " ").split()
            if len(name_parts) > 1:
                validated_metric["synonyms"] = [" ".join(name_parts[1:] + [name_parts[0]])]
        
        # Add access modifier if not present
        if "access_modifier" not in metric:
            validated_metric["access_modifier"] = "public_access"
        
        validated.append(validated_metric)
    
    return validated


def _generate_fallback_metrics(model_summary: Dict) -> List[Dict]:
    """Generate basic fallback metrics if LLM fails."""
    
    metrics = []
    
    # Find tables with revenue-related facts
    for table_name, table_info in model_summary["tables"].items():
        for fact in table_info["facts"]:
            fact_name = fact["name"]
            
            # Generate sum metric
            if any(keyword in fact_name.lower() for keyword in ["amount", "total", "revenue", "cost", "price"]):
                metrics.append({
                    "name": f"total_{fact_name}",
                    "description": f"Sum of {fact_name} across all {table_name} records",
                    "expr": f"SUM({table_name}.{fact_name})"
                })
            
            # Generate count
            if len(metrics) < 3:
                metrics.append({
                    "name": f"{table_name}_count",
                    "description": f"Total number of {table_name} records",
                    "expr": f"COUNT({table_name}.*)"
                })
    
    return metrics[:5]  # Return max 5 fallback metrics