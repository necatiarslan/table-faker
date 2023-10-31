from . import config_parser
from . import util
import pandas as pd
from faker import Faker
import random

def to_csv(config_file_path, target_file_path, table_name=None):
    result = to_pandas(config_file_path)
    
    if table_name is None:
        table_name = list(result.keys())[0]

    df = result[table_name]
    df.to_csv(target_file_path)
    util.log(f"data is exported to {target_file_path} as csv")

def to_json(config_file_path, target_file_path, table_name=None):
    result = to_pandas(config_file_path)
    
    if table_name is None:
        table_name = list(result.keys())[0]

    df = result[table_name]
    df.to_json(target_file_path)
    util.log(f"data is exported to {target_file_path} as json")

def to_excel(config_file_path, target_file_path, table_name=None):
    result = to_pandas(config_file_path)
    
    if table_name is None:
        table_name = list(result.keys())[0]

    df = result[table_name]
    df.to_excel(target_file_path)
    util.log(f"data is exported to {target_file_path} as excel")

def to_parquet(config_file_path, target_file_path, table_name=None):
    result = to_pandas(config_file_path)
    
    if table_name is None:
        table_name = list(result.keys())[0]

    df = result[table_name]
    df.to_parquet(target_file_path)
    util.log(f"data is exported to {target_file_path} as parquet")

def to_pandas(config_file_path:str) -> pd.DataFrame:
    parser = config_parser.ConfigParser(config_file_path)
    tables = parser.config["tables"]
    util.log(f"table count={len(tables)}")

    result = {}
    for table in tables:
        df = generate_table(table)
        result[table['table_name']] = df
    
    util.log(f"{len(result)} pandas dataframe(s) created")
    return result

def generate_table(table):
    # Initialize the Faker generator
    faker = Faker()

    table_name = table['table_name']
    row_count = table['row_count']
    columns = table['columns']

    table_data = {}

    for column in columns:
        column_name = column['column_name']
        data_command = column['data']
        fake_data = generate_fake_data(faker, data_command, row_count)
        table_data[column_name] = fake_data
        #print(f"fake_data={fake_data}")

    df = pd.DataFrame(table_data)
    util.log(f"{table_name} pandas dataframe created")
    return df

def generate_fake_data(fake: Faker, command, row_count, **kwargs):
    result = None
    
    fake_data = []
    for row_id in range(1, row_count+1):
        variables = {
            "random": random,
            "fake": fake,
            "result": result,
            "command": command,
            "row_id": row_id
            }
        
        exec(f"result = {command}", variables)
        result = variables["result"]
        fake_data.append(result)

    return fake_data
