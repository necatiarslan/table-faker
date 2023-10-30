import yaml
from os import path
from .util import log

class ConfigParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.load_config_file()
        self.validate_config()
    
    def load_config_file(self):
        if path.isfile(self.file_path):
            with open(self.file_path, "f") as file:
                self.config = yaml.safe_load(file)
        else:
            raise Exception(f"{self.file_path} file not found")
    
    def validate_config():
        pass