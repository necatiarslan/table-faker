from . import config
from . import util
import pandas as pd
from faker import Faker
import random
from os import path
from datetime import date, datetime
import importlib.util
import sys, math, gc

def to_target(file_type, config_file_path, target_file_path, table_name=None, **kwargs) :
    if file_type not in ["csv", "json", "excel", "parquet", "deltalake", "sql"]:
        raise Exception(f"Wrong file_type = {file_type}")
    
    result = {}
    configurator = config.Config(config_file_path)
    tables = configurator.config["tables"]
    
    for table in tables:
        if table_name != None and table["table_name"] != table_name:
            continue #skip other tables
    
        row_count = table['row_count'] if "row_count" in table else 10
        export_file_count = table["export_file_count"] if "export_file_count" in table else 1
        export_file_row_count = table["export_file_row_count"] if "export_file_row_count" in table else sys.maxsize
        if export_file_count > 1:
            export_file_row_count = math.ceil(row_count / export_file_count)
        

        if path.isdir(target_file_path) or file_type == "deltalake":

            if file_type == "deltalake" and table["table_name"] == table_name and not path.exists(target_file_path) and path.exists(path.dirname(path.normpath(target_file_path)) + "/"):
                # in delta lake format, if the latest folder does not exists, assume it is requested delta lake folder
                temp_file_path = target_file_path.rstrip('/')
            else:
                file_name = util.get_temp_filename(table["table_name"]) + util.get_file_extension(file_type)
                temp_file_path = path.join(target_file_path, file_name)

            to_target_file(file_type, temp_file_path, table_name, kwargs, result, configurator, table, export_file_row_count, row_count)
            result[table_name] = temp_file_path
        else:
            to_target_file(file_type, target_file_path, table_name, kwargs, result, configurator, table, export_file_row_count, row_count)
            break # if single table is requested
    
    return result

def to_target_file(file_type, target_file_path, table_name, kwargs, result, configurator, table, export_file_row_count, row_count):
    internal_row_id = 0
    internal_row_count = min(export_file_row_count, sys.maxsize)
    file_count = math.ceil(row_count / export_file_row_count)
    total_exported_row_count = 0
    for i in range(file_count):
                #internal_row_count = export_file_row_count
        internal_row_count = min(export_file_row_count, row_count - total_exported_row_count)
        df = generate_table(table, configurator, internal_row_id, internal_row_count, **kwargs)
        if file_count > 1:
            file_name, file_extension = path.splitext(target_file_path)
            temp_file_path = file_name + "_" + str(i+1) + file_extension
        else:
            temp_file_path = target_file_path
        call_export_function(df, file_type, temp_file_path)
        del df
        gc.collect()
        util.log(f"data is exported to {temp_file_path}", util.FOREGROUND_COLOR.GREEN)
        result[table_name] = temp_file_path
        internal_row_id = internal_row_id + internal_row_count
        total_exported_row_count = total_exported_row_count + internal_row_count

def call_export_function(data_frame: pd.DataFrame, file_type, target_file_path):
    if file_type == "csv":
        data_frame.to_csv(target_file_path, index=False)
    elif file_type == "json":
        data_frame.to_json(target_file_path, index=False, indent=4, orient='records', date_format='iso')
    elif file_type == "excel":
        data_frame.to_excel(target_file_path, index=False)
    elif file_type == "parquet":
        data_frame.to_parquet(target_file_path, index=False)
    elif file_type == "sql":
        to_sql_internal(data_frame, target_file_path)
    elif file_type == "deltalake":
        to_deltalake_internal(data_frame, target_file_path)
    else:
        raise Exception(f"Wrong file_type = {file_type}")

def to_pandas(config_file_path:str, table_name=None, **kwargs):
    result = {}
    configurator = config.Config(config_file_path)
    tables = configurator.config["tables"]
    for table in tables:
        if table_name != None and table["table_name"] != table_name:
            continue #skip other tables

        df = generate_table(table, configurator, **kwargs)
        result[table["table_name"]] = df
    return result

def to_csv(config_file_path, target_file_path=None, table_name=None, **kwargs) :
    if target_file_path is None:
        target_file_path = "."
    return to_target("csv", config_file_path, target_file_path, table_name, **kwargs)

def to_json(config_file_path, target_file_path=None, table_name=None, **kwargs) :
    if target_file_path is None:
        target_file_path = "."
    return to_target("json", config_file_path, target_file_path, table_name, **kwargs)

def to_excel(config_file_path, target_file_path=None, table_name=None, **kwargs) :
    if target_file_path is None:
        target_file_path = "."
    return to_target("excel", config_file_path, target_file_path, table_name, **kwargs)

def to_parquet(config_file_path, target_file_path=None, table_name=None, **kwargs) :
    if target_file_path is None:
        target_file_path = "."
    return to_target("parquet", config_file_path, target_file_path, table_name, **kwargs)

def to_deltalake(config_file_path, target_file_path=None, table_name=None, **kwargs) :
    if target_file_path is None:
        target_file_path = "."
    return to_target("deltalake", config_file_path, target_file_path, table_name, **kwargs)


def to_sql(config_file_path, target_file_path=None, table_name=None, **kwargs) :
    if target_file_path is None:
        target_file_path = "."
    return to_target("sql", config_file_path, target_file_path, table_name, **kwargs)

def to_deltalake_internal(data_frame: pd.DataFrame, target_file_path):
    if importlib.util.find_spec("deltalake"):
        deltalake = __import__("deltalake")
        deltalake.writer.write_deltalake(target_file_path, data_frame, mode="overwrite")
    else:
        raise Exception("deltalake package is not installed. install it with pip install deltalake")
def to_sql_internal(data_frame: pd.DataFrame, target_file_path):

    table_name = data_frame.Name
    # Generate insert script file
    column_names = ','.join(data_frame.columns)
    insert_script = f"INSERT INTO {table_name}\n({column_names})\nVALUES\n"

    # Iterate over DataFrame rows and create insert statements
    for _, row in data_frame.iterrows():
        value_list = []
        for value in row:
            if isinstance(value, (str, date, datetime)):
                value_list.append(f"'{value}'")
            elif value == None:
                value_list.append("NULL")
            else:
                value_list.append(str(value))

        values = ', '.join(value_list)
        insert_script += f"({values}),\n"

    # Remove the trailing comma and newline
    insert_script = insert_script.rstrip(',\n')

    # Write the insert script to the target file
    with open(target_file_path, 'w') as file:
        file.write(insert_script + ';')

def generate_table(table, configurator, internal_start_row_id=0, internal_row_count=sys.maxsize, **kwargs) -> pd.DataFrame:
    locale = None
    if "config" in configurator.config and "locale" in configurator.config["config"]:
        locale = configurator.config["config"]["locale"]

    fake = Faker(locale)
    python_import = configurator.get_python_import()
    if "fake_provider" in kwargs:
        if not isinstance(kwargs["fake_provider"], list):
            fake.add_provider(kwargs["fake_provider"])
        else:
            for provider in kwargs["fake_provider"]:
                fake.add_provider(provider)

    variables = {
        "random": random,
        "datetime": datetime,
        "fake": fake,
        "result": [],
        }

    if "custom_function" in kwargs:
        if isinstance(kwargs["custom_function"], list):
            for func in kwargs["custom_function"]:
                variables[func.__name__] = func
        else:
            func = kwargs["custom_function"]
            variables[func.__name__] = func

    if python_import and isinstance(python_import, list):
        for library_name in python_import:
            if library_name not in variables:
                variables[library_name] = __import__(library_name)

    table_name = table['table_name']
    row_count = table['row_count'] if "row_count" in table else 10
    row_count = min(row_count, internal_row_count)
    start_row_id = table['start_row_id'] if "start_row_id" in table else 1
    start_row_id = start_row_id + internal_start_row_id
    columns = table['columns']

    rows = []
    for row_id in range(start_row_id, start_row_id+row_count):
        util.progress_bar(row_id-start_row_id+1, row_count, f"Table:{table_name}")
        variables["row_id"] = row_id
        new_row = generate_fake_row(columns, variables)
        rows.append(new_row)
        row_id += 1

    df = pd.DataFrame(rows)
    df.Name = table['table_name']
    df.convert_dtypes() # auto set best fitting type
    for column in columns:
        column_name = column['column_name']
        if "type" in column:
            util.log(f"Converting Column {column_name} to {column['type']}", util.FOREGROUND_COLOR.MAGENTA)
            df[column_name] = df[column_name].astype(column['type'])
        if "null_percentage" in column:
            null_percentge = util.parse_null_percentge(column["null_percentage"])
            for _ in range(1, int(row_count * null_percentge)+1):
                random_num = random.randint(1, row_count)
                df.at[random_num-1, column_name] = None

    util.log(f"{table_name} pandas dataframe created", util.FOREGROUND_COLOR.GREEN)
    return df

def generate_fake_row(columns:dict, variables:dict) :
    result = {}
    for column in columns:
        command = column["data"]
        column_name = column["column_name"]
        variables["command"] = command
        
        try:
            exec(f"result = {command}", variables)
        except AttributeError as error:
            raise RuntimeError(f"Custom Faker Provider can not be found. {command} \n {error}")
        except NameError as error:
            raise RuntimeError(f"Custom function can not be found. {command} \n {error}")
        except Exception as error:
            raise error
        
        variables[column_name] = variables["result"]
        result[column_name] = variables["result"]

    return result

