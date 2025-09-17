import yaml, json
from os import path
from . import util

class Config:
    def __init__(self, source):
        if isinstance(source, str):
            if not path.isabs(source):
                source = path.abspath(source)
            util.log(f"received config {source}", util.FOREGROUND_COLOR.GREEN)
            self.file_path = source
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
            if "doc" in field:
                col["description"] = field["doc"]

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

            yaml_struct["tables"][0]["columns"].append(col)

        yaml_text = yaml.safe_dump(yaml_struct, sort_keys=False)

        if target_file_path:
            with open(target_file_path, "w", encoding="utf-8") as out_f:
                out_f.write(yaml_text)
            return target_file_path

        return target_file_path