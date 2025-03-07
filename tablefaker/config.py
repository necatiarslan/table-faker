import yaml
from os import path
from . import util

class Config:
    def __init__(self, file_path):
        if not path.isabs(file_path):
            file_path = path.abspath(file_path)

        util.log(f"received config is {file_path}", util.FOREGROUND_COLOR.GREEN)
        self.file_path = file_path
        self.load_config_file()
        self.validate_config()
    
    def load_config_file(self):
        if path.isfile(self.file_path):
            with open(self.file_path, "r") as file:
                self.config = yaml.safe_load(file)
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

            if "row_count" not in table:
                raise Exception(f"{table_name} table should have a row_count attribute")

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
        
        util.log(f"config file is validated")

    def get_python_import(self):
        if "config" in self.config and "python_import" in self.config["config"]:
            return self.config["config"]["python_import"]

        return []