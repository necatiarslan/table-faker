from . import config
from . import util
import pandas as pd
from faker import Faker
import random
from os import path

def to_target(target_type, config_file_path, target_file_path, table_name=None) -> {} :
    result = {}
    df_dict = to_pandas(config_file_path)
    
    if path.isdir(target_file_path):
        for key_table_name in df_dict.keys():
            if table_name != None and key_table_name != table_name:
                continue #skip other tables

            df = df_dict[key_table_name]
            temp_file_path = path.join(target_file_path, util.get_temp_filename(key_table_name)+".csv")
            call_export_function(df, target_type, temp_file_path)
            util.log(f"data is exported to {temp_file_path} as {target_type}")
            result[key_table_name] = temp_file_path 
    elif path.isfile(target_file_path):
        if table_name is None:
            table_name = list(df_dict.keys())[0]
        df = df_dict[table_name]
        df.to_csv(target_file_path)
        call_export_function(df, target_type, target_file_path)
        util.log(f"data is exported to {target_file_path} as {target_type}")
        result[table_name] = target_file_path
    else:
        raise Exception(f"target_file_path={target_file_path} is not valid")
    
    return result

def call_export_function(data_frame: pd.DataFrame, target_type, target_file_path):
    if target_type == "csv":
        data_frame.to_csv(target_file_path)
    elif target_type == "json":
        data_frame.to_json(target_file_path)
    elif target_type == "excel":
        data_frame.to_excel(target_file_path)
    elif target_type == "parquet":
        data_frame.to_parquet(target_file_path)
    else:
        raise Exception(f"Wrong target_type = {target_type}")

def to_csv(config_file_path, target_file_path, table_name=None) -> {} :
    return to_target("csv", config_file_path, target_file_path, table_name)

def to_json(config_file_path, target_file_path, table_name=None) -> {} :
    return to_target("json", config_file_path, target_file_path, table_name)

def to_excel(config_file_path, target_file_path, table_name=None) -> {} :
    return to_target("excel", config_file_path, target_file_path, table_name)

def to_parquet(config_file_path, target_file_path, table_name=None) -> {} :
    return to_target("parquet", config_file_path, target_file_path, table_name)

def to_pandas(config_file_path:str) -> pd.DataFrame:
    parser = config.Config(config_file_path)
    tables = parser.config["tables"]
    util.log(f"table count={len(tables)}")

    result = {}
    for table in tables:
        df = generate_table(table)
        result[table['table_name']] = df
    
    util.log(f"{len(result)} pandas dataframe(s) created")
    return result

def generate_table(table) -> pd.DataFrame:
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

def generate_fake_data(fake: Faker, command, row_count, **kwargs) -> []:
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
