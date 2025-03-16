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