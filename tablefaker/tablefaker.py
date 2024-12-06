from . import config
from . import util
import pandas as pd
from faker import Faker
import random
from os import path
from datetime import date, datetime

def to_target(file_type, config_file_path, target_file_path, table_name=None, **kwargs) :
    if file_type not in ["csv", "json", "excel", "parquet", "sql"]:
        raise Exception(f"Wrong file_type = {file_type}")
    
    result = {}
    df_dict = to_pandas(config_file_path, **kwargs)
    
    if path.isdir(target_file_path):
        for key_table_name in df_dict.keys():
            if table_name != None and key_table_name != table_name:
                continue #skip other tables

            df = df_dict[key_table_name]
            temp_file_path = path.join(target_file_path, util.get_temp_filename(key_table_name) + util.get_file_extension(file_type))
            call_export_function(df, file_type, temp_file_path)
            util.log(f"data is exported to {temp_file_path} as {file_type}")
            result[key_table_name] = temp_file_path 
    else:
        if table_name is None:
            table_name = list(df_dict.keys())[0]
        df = df_dict[table_name]
        call_export_function(df, file_type, target_file_path)
        util.log(f"data is exported to {target_file_path} as {file_type}")
        result[table_name] = target_file_path
    
    return result

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
    else:
        raise Exception(f"Wrong file_type = {file_type}")

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

def to_sql(config_file_path, target_file_path=None, table_name=None, **kwargs) :
    if target_file_path is None:
        target_file_path = "."
    return to_target("sql", config_file_path, target_file_path, table_name, **kwargs)

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

def to_pandas(config_file_path:str, **kwargs) -> pd.DataFrame:
    configurator = config.Config(config_file_path)
    tables = configurator.config["tables"]
    util.log(f"table count={len(tables)}")

    result = {}
    for table in tables:
        df = generate_table(table, configurator, **kwargs)
        df.Name = table['table_name']
        result[table['table_name']] = df
    
    util.log(f"{len(result)} pandas dataframe(s) created")
    return result

def generate_table(table, configurator, **kwargs) -> pd.DataFrame:
    locale = None
    if "config" in configurator.config and "locale" in configurator.config["config"]:
        locale = configurator.config["config"]["locale"]

    faker = Faker(locale)

    if "fake_provider" in kwargs:
        if not isinstance(kwargs["fake_provider"], list):
            faker.add_provider(kwargs["fake_provider"])
        else:
            for provider in kwargs["fake_provider"]:
                faker.add_provider(provider)

    table_name = table['table_name']
    row_count = table['row_count']
    columns = table['columns']

    table_data = {}
    iteration = 1
    for column in columns:
        column_name = column['column_name']
        data_command = column['data']
        util.progress_bar(iteration, len(columns), f"Generating {table_name}/{column_name}")
        fake_data = generate_fake_data(configurator, faker, data_command, row_count, column, **kwargs)
        table_data[column_name] = fake_data
        iteration += 1

    df = pd.DataFrame(table_data)
    df.convert_dtypes() # auto set best fitting type
    for column in columns:
        column_name = column['column_name']
        if "type" in column:
            df[column_name] = df[column_name].astype(column['type'])

    util.log(f"{table_name} pandas dataframe created")
    return df

def generate_fake_data(configurator, fake: Faker, command, row_count, column_config, **kwargs) :
    result = None
    
    python_import = configurator.get_python_import()

    null_percentge = 0
    null_indexies = []
    if "null_percentage" in column_config:
        null_percentge = util.parse_null_percentge(column_config["null_percentage"])
        for _ in range(1, int(row_count * null_percentge)+1):
            random_num = random.randint(1, row_count)
            null_indexies.append(random_num)


    fake_data = []
    for row_id in range(1, row_count+1):
        if row_id in null_indexies:
            fake_data.append(None) #add null data
            continue

        variables = {
            "random": random,
            "fake": fake,
            "result": result,
            "command": command,
            "row_id": row_id
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
                variables[library_name] = __import__(library_name)

        try:
            exec(f"result = {command}", variables)
        except AttributeError as error:
            raise RuntimeError(f"Custom Faker Provider can not be found. {command} \n {error}")
        except NameError as error:
            raise RuntimeError(f"Custom function can not be found. {command} \n {error}")
        except Exception as error:
            raise error
        
        result = variables["result"]
        fake_data.append(result)

    return fake_data
