import yaml, json
from os import path
from . import util
import sys  # NEW

class Config:
    def __init__(self, source):
        if isinstance(source, str):
            if not path.isabs(source):
                source = path.abspath(source)
            util.log(f"received config {source}", util.FOREGROUND_COLOR.GREEN)
            self.file_path = source

            # modules in the same folder as the YAML importable
            cfg_dir = path.dirname(self.file_path) or "."
            abs_cfg_dir = path.abspath(cfg_dir)
            # avoid duplicates comparing absolute paths
            if abs_cfg_dir not in [path.abspath(p) for p in sys.path if isinstance(p, str)]:
                sys.path.insert(0, abs_cfg_dir)

            self.load_config_file()
        elif isinstance(source, dict):
            self.config = source

        self.validate_config()

    def to_json(self, target_file_path=None):
        if target_file_path is None:
            target_file_path = "."

        if path.isdir(target_file_path):
            file_name = util.get_temp_filename("config") + ".json"
            target_file_path = path.join(target_file_path, file_name)

        with open(target_file_path, "w") as file:
            json.dump(self.config, file, indent=4)

    def load_config_file(self):
        if isinstance(self.file_path, str) and path.isfile(self.file_path):
            with open(self.file_path, "r") as file:
                if self.file_path.endswith(".yaml"):
                    self.config = yaml.safe_load(file)
                elif self.file_path.endswith(".json"):
                    self.config = json.load(file)
                else:
                    raise Exception(f"Unsupported config file type {self.file_path}")
        else:
            raise Exception(f"{self.file_path} file not found")
    
    def validate_config(self):
        if "tables" not in self.config:
            raise Exception(f"Config file should have tables node")
        
        if len(self.config["tables"]) == 0:
            raise Exception(f"Config file should contain at least 1 table")
        
        for table in self.config["tables"]:
            if "table_name" not in table:
                raise Exception(f"Table should have a table_name attribute")
            
            table_name = table["table_name"]

            # if "row_count" not in table:
            #     raise Exception(f"{table_name} table should have a row_count attribute")

            if "columns" not in table:
                raise Exception(f"{table_name} table should have a columns attribute")

            if len(table["columns"]) == 0:
                raise Exception(f"{table_name} table should have at least 1 table")
            
            for column in table["columns"]:
                if "column_name" not in column:
                    raise Exception(f"{table_name} table have a column without a column_name attribute")
            
                column_name = column["column_name"]
                
                if "data" not in column:
                    raise Exception(f"{table_name} table {column_name} column do not have a data attribute")
        
        #util.log(f"config file is validated")

    def get_python_import(self):
        if "config" in self.config and "python_import" in self.config["config"]:
            return self.config["config"]["python_import"]

        return []
    
    def get_community_providers(self):
        """
        Get community providers from config.
        Format: ['faker_education(SchoolProvider)', 'another_module(SomeProvider)']
        Returns: list of tuples [(module_name, provider_class_name), ...]
        """
        if "config" in self.config and "community_providers" in self.config["config"]:
            providers = self.config["config"]["community_providers"]
            parsed = []
            for provider_str in providers:
                # Parse format: module_name(ClassName)
                if '(' in provider_str and ')' in provider_str:
                    module_name = provider_str[:provider_str.index('(')].strip()
                    class_name = provider_str[provider_str.index('(')+1:provider_str.index(')')].strip()
                    parsed.append((module_name, class_name))
            return parsed
        return []
    

    def avro_type_to_tablefaker_type(avro_type):
        """Map Avro field type to a tablefaker column type hint."""
        # avro_type can be a string (e.g., "string") or a list (union) or dict for complex
        if isinstance(avro_type, list):
            # filter out null
            non_null = [t for t in avro_type if t != "null"]
            if len(non_null) == 1:
                return Config.avro_type_to_tablefaker_type(non_null[0])
            # fallback
            return "string"

        if isinstance(avro_type, dict):
            # logicalTypes etc.
            t = avro_type.get("type")
            if t == "int" and avro_type.get("logicalType") == "date":
                return "date"
            return Config.avro_type_to_tablefaker_type(t)

        # primitive strings
        if avro_type in ("string", "bytes"):
            return "string"
        if avro_type in ("int", "long"):
            return "int32" if avro_type == "int" else "int64"
        if avro_type == "float" or avro_type == "double":
            return "float"
        if avro_type == "boolean":
            return "bool"

        # default fallback
        return "string"


    def avro_to_yaml(avro_file_path, target_file_path=None):
        """Read an Avro schema JSON file and produce a tablefaker YAML config.

        avro_file_path: path to .avsc file (JSON)
        target_file_path: optional path to write YAML (if None, returns YAML string)
        returns: YAML string when target_file_path is None, else returns target_file_path
        """
        if not path.isfile(avro_file_path):
            raise Exception(f"{avro_file_path} file not found")

        if target_file_path is None:
            target_file_path = "."


        with open(avro_file_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        if "type" not in schema or schema["type"] != "record":
            raise Exception(f"Only Avro record type is supported")
        
        table_name = schema.get("name")

        if path.isdir(target_file_path):
            file_name = util.get_temp_filename(table_name) + ".yaml"
            target_file_path = path.join(target_file_path, file_name)

        yaml_struct = {
            "version": 1,
            "config": {
                "locale": "en_US"
            },
            "tables": [
                {
                    "table_name": table_name.lower(),
                    "row_count": 10,
                    "columns": []
                }
            ]
        }

        if "fields" not in schema:
            raise Exception(f"Avro schema does not have fields")
        
        fields = schema.get("fields", [])
        for field in fields:
            name = field.get("name")
            ftype = field.get("type")
            col = {"column_name": name}

            # map types
            mapped = Config.avro_type_to_tablefaker_type(ftype)
            if mapped:
                # tablefaker expects types like string, int32, float
                col_type = mapped
                # map bool to no explicit type (or boolean) - keep consistent with examples
                if col_type == "bool":
                    col["type"] = "boolean"
                else:
                    col["type"] = col_type

            # add a default data generator placeholder based on type
            if col.get("type") in ("string", "date"):
                col["data"] = "fake.word()"
            elif col.get("type") in ("int32", "int64"):
                col["data"] = "fake.random_int(0, 100)"
            elif col.get("type") == "float":
                col["data"] = "fake.pyfloat()"
            elif col.get("type") == "boolean":
                col["data"] = "fake.pybool()"
            else:
                # fallback
                col.setdefault("data", "None")

            if isinstance(ftype, list) and "null" in ftype:
                col["null_percentage"] = 0.1  # default 10% nulls for nullable fields

            if "doc" in field:
                col["description"] = field["doc"].replace('\n', ' ')

            yaml_struct["tables"][0]["columns"].append(col)

        yaml_text = yaml.safe_dump(yaml_struct, sort_keys=False)

        if target_file_path:
            with open(target_file_path, "w", encoding="utf-8") as out_f:
                out_f.write(yaml_text)
            return target_file_path

        util.log(f"yaml is generated at {target_file_path}", util.FOREGROUND_COLOR.GREEN)

        return target_file_path
    
    def csv_to_yaml(csv_file_path, target_file_path=None):
        """Read a CSV file and produce a tablefaker YAML config.

        csv_file_path: path to .csv file
        target_file_path: optional path to write YAML (if None, returns YAML string)
        returns: YAML string when target_file_path is None, else returns target_file_path
        """
        if not path.isfile(csv_file_path):
            raise Exception(f"{csv_file_path} file not found")

        if target_file_path is None:
            target_file_path = "."

        if path.isdir(target_file_path):
            file_name = util.get_temp_filename("config") + ".yaml"
            target_file_path = path.join(target_file_path, file_name)

        table_name = path.splitext(path.basename(csv_file_path))[0]

        yaml_struct = {
            "version": 1,
            "config": {
                "locale": "en_US"
            },
            "tables": [
                {
                    "table_name": table_name.lower(),
                    "row_count": 10,
                    "columns": []
                }
            ]
        }

        import pandas as pd
        df = pd.read_csv(csv_file_path)
        util.log("csv columns:" + ", ".join(df.columns), util.FOREGROUND_COLOR.GREEN)

        if "column_name" not in df.columns:
            raise Exception(f"'column_name' is not a column in the csv file")

        columns_allowed = ["column_name", "type", "data", "null_percentage", "description"]
        present_columns = [col for col in df.columns if col in columns_allowed]
        util.log("columns will be used in csv: " + ", ".join(present_columns), util.FOREGROUND_COLOR.GREEN)

        unused_columns = [col for col in df.columns if col not in columns_allowed]
        if unused_columns:
            util.log("columns will NOT be used in csv: " + ", ".join(unused_columns), util.FOREGROUND_COLOR.YELLOW)

        for row in df.itertuples(index=False):
            col_struct = {
                "column_name": getattr(row, "column_name")
            }
            if "type" in df.columns and isinstance(getattr(row, "type"), str):
                col_struct["type"] = getattr(row, "type")
            if "data" in df.columns and isinstance(getattr(row, "data"), str):
                col_struct["data"] = getattr(row, "data")
            if "null_percentage" in df.columns and isinstance(getattr(row, "null_percentage"), (float, int)):
                null_perc = getattr(row, "null_percentage")
                try:
                    null_perc = float(null_perc)
                    if 0.0 <= null_perc <= 1.0:
                        col_struct["null_percentage"] = null_perc
                except:
                    util.log(f"invalid null_percentage value {null_perc} for column {col_struct['column_name']}. 0.0 <= null_percentage <= 1.0", util.FOREGROUND_COLOR.YELLOW)
            if "description" in df.columns and isinstance(getattr(row, "description"), str):
                desc = getattr(row, "description")
                if isinstance(desc, str) and desc.strip():
                    col_struct["description"] = desc.strip()
            yaml_struct["tables"][0]["columns"].append(col_struct)

        yaml_text = yaml.safe_dump(yaml_struct, sort_keys=False)

        if target_file_path:
            with open(target_file_path, "w", encoding="utf-8") as out_f:
                out_f.write(yaml_text)
            return target_file_path

        util.log(f"yaml is generated at {target_file_path}", util.FOREGROUND_COLOR.GREEN)

        return target_file_path
