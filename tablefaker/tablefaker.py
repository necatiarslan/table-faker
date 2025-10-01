from . import config
from . import util
import pandas as pd
import numpy as np
from faker import Faker
import random
from os import path
from datetime import date, datetime, timedelta, time, timezone, tzinfo, UTC, MINYEAR, MAXYEAR
import importlib.util
import sys, math, gc, psutil, string
import hashlib
import yaml


class TableFaker:
    def __init__(self):
        self.reset_start_time()
        self.primary_key_cache = {}
        self.primary_key_seed = None
        self.parent_rows = {}          # table -> {pk_value: full_row_dict}
        self.fake_by_locale = {}       # locale -> Faker
        self._current_row = None       # for copy_from_fk access during phase B
    
    def reset_start_time(self):
        self.start_time = datetime.now()
    
    def _apply_seed(self, seed):
        """Apply seed to random, numpy, and Faker for determinism."""
        if seed is None:
            return
        random.seed(seed)
        np.random.seed(seed)
        Faker.seed(seed)
    
    def _get_fake(self, locale):
        """Get or create cached Faker instance for a locale."""
        if locale not in self.fake_by_locale:
            self.fake_by_locale[locale] = Faker(locale)
        return self.fake_by_locale[locale]
    
    def _stable_seed(self, *parts):
        """Generate deterministic seed from parts using MD5."""
        key = "|".join(map(str, parts)).encode("utf-8")
        return int.from_bytes(hashlib.md5(key).digest()[:4], "little")
    
    def _copy_from_fk(self, fk_col, parent_table, parent_attr):
        """Copy attribute from parent row via foreign key."""
        fk_val = self._current_row[fk_col]
        try:
            return self.parent_rows[parent_table][fk_val][parent_attr]
        except KeyError:
            raise RuntimeError(f"Missing parent row for {parent_table}.{parent_attr} with key={fk_val}")

    def print_sys_stats(self):
        end_time = datetime.now()
        elapsed_time = end_time - self.start_time
        minutes, seconds = divmod(elapsed_time.seconds, 60)
        seconds = f"{seconds:02}"
        milliseconds = f"{elapsed_time.microseconds // 1000:03}"

        memory_usage = psutil.Process().memory_info().rss / (1024 * 1024)
        memory_usage = f"{memory_usage:.2f} MB"

        cpu_usage = psutil.cpu_percent(interval=1)  # Measure over 1 second
        cpu_usage = f"{cpu_usage:.2f}%"

        util.log(f"Elapsed:{minutes}:{seconds}:{milliseconds}, Memory:{memory_usage}, CPU:{cpu_usage}", util.FOREGROUND_COLOR.GREEN)

    def to_target(self, file_type, config_source, target_file_path, table_name=None, seed=None, infer_attrs=None, **kwargs) :
        if target_file_path is None:
            target_file_path = "."
        
        if file_type not in ["csv", "json", "excel", "parquet", "deltalake", "sql"]:
            raise Exception(f"Wrong file_type = {file_type}")
        
        result = {}
        configurator = config.Config(config_source)
        
        # Use CLI-provided seed if available, otherwise use config seed
        if seed is None:
            seed = configurator.config.get("config", {}).get("seed")
        self._apply_seed(seed)
        
        # Override infer_entity_attrs_by_name if provided via CLI
        if infer_attrs is not None:
            # Convert string 'true'/'false' to boolean
            infer_bool = infer_attrs.lower() == 'true' if isinstance(infer_attrs, str) else infer_attrs
            if "config" not in configurator.config:
                configurator.config["config"] = {}
            configurator.config["config"]["infer_entity_attrs_by_name"] = infer_bool
        
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

                self.to_target_file(file_type, temp_file_path, table_name, kwargs, result, configurator, table, export_file_row_count, row_count)
                result[table_name] = temp_file_path
            else:
                self.to_target_file(file_type, target_file_path, table_name, kwargs, result, configurator, table, export_file_row_count, row_count)
                break # if single table is requested
        
        return result

    def to_pandas(self, config_source:str, table_name=None, **kwargs):
        result = {}
        configurator = config.Config(config_source)
        seed = configurator.config.get("config", {}).get("seed")
        self._apply_seed(seed)
        tables = configurator.config["tables"]
        for table in tables:
            if table_name != None and table["table_name"] != table_name:
                continue #skip other tables
            self.reset_start_time()
            df = self.generate_table(table, configurator, **kwargs)
            self.print_sys_stats()
            result[table["table_name"]] = df
        return result

    def to_target_file(self, file_type, target_file_path, table_name, kwargs, result, configurator, table, export_file_row_count, row_count):
        internal_row_id = 0
        internal_row_count = min(export_file_row_count, sys.maxsize)
        file_count = math.ceil(row_count / export_file_row_count)
        total_exported_row_count = 0
        for i in range(file_count):
                    #internal_row_count = export_file_row_count
            internal_row_count = min(export_file_row_count, row_count - total_exported_row_count)
            self.reset_start_time()
            df = self.generate_table(table, configurator, internal_row_id, internal_row_count, **kwargs)
            if file_count > 1:
                file_name, file_extension = path.splitext(target_file_path)
                temp_file_path = file_name + "_" + str(i+1) + file_extension
            else:
                temp_file_path = target_file_path
            self.call_export_function(df, file_type, temp_file_path)
            del df
            gc.collect()
            util.log(f"data is exported to {temp_file_path}", util.FOREGROUND_COLOR.GREEN)
            self.print_sys_stats()
            result[table_name] = temp_file_path
            internal_row_id = internal_row_id + internal_row_count
            total_exported_row_count = total_exported_row_count + internal_row_count

    def call_export_function(self, data_frame: pd.DataFrame, file_type, target_file_path):
        if file_type == "csv":
            data_frame.to_csv(target_file_path, index=False)
        elif file_type == "json":
            data_frame.to_json(target_file_path, index=False, indent=4, orient='records', date_format='iso')
        elif file_type == "excel":
            data_frame.to_excel(target_file_path, index=False)
        elif file_type == "parquet":
            data_frame.to_parquet(target_file_path, index=False)
        elif file_type == "sql":
            self.to_sql_internal(data_frame, target_file_path)
        elif file_type == "deltalake":
            self.to_deltalake_internal(data_frame, target_file_path)
        else:
            raise Exception(f"Wrong file_type = {file_type}")

    def to_deltalake_internal(self, data_frame: pd.DataFrame, target_file_path):
        if importlib.util.find_spec("deltalake"):
            deltalake = __import__("deltalake")
            deltalake.writer.write_deltalake(target_file_path, data_frame, mode="overwrite")
        else:
            raise Exception("deltalake package is not installed. install it with pip install deltalake")

    def to_sql_internal(self, data_frame: pd.DataFrame, target_file_path):

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

    def generate_table(self,table, configurator, internal_start_row_id=0, internal_row_count=sys.maxsize, **kwargs) -> pd.DataFrame:
        locale = None
        if "config" in configurator.config and "locale" in configurator.config["config"]:
            locale = configurator.config["config"]["locale"]

        fake = self._get_fake(locale)
        python_import = configurator.get_python_import()
        
        # Add community providers from config
        community_providers = configurator.get_community_providers()
        for module_name, class_name in community_providers:
            try:
                import importlib
                module = importlib.import_module(module_name)
                provider_class = getattr(module, class_name)
                fake.add_provider(provider_class)
            except (ImportError, AttributeError) as e:
                raise RuntimeError(f"Failed to load community provider {module_name}.{class_name}: {e}")
        
        # Add providers passed via kwargs (for programmatic use)
        if "fake_provider" in kwargs:
            if not isinstance(kwargs["fake_provider"], list):
                fake.add_provider(kwargs["fake_provider"])
            else:
                for provider in kwargs["fake_provider"]:
                    fake.add_provider(provider)

        variables = {
            "random": random,
            "datetime": datetime,
            "date": date,
            "timedelta": timedelta,
            "time": time,
            "timezone": timezone,
            "tzinfo": tzinfo,
            "UTC": UTC,
            "MINYEAR": MINYEAR,
            "MAXYEAR": MAXYEAR,
            "math": math,
            "string": string,
            "fake": fake,
            "result": [],
            "foreign_key": self.foreign_key,
            "copy_from_fk": self._copy_from_fk
            }

        if "custom_function" in kwargs:
            if isinstance(kwargs["custom_function"], list):
                for func in kwargs["custom_function"]:
                    variables[func.__name__] = func
            else:
                func = kwargs["custom_function"]
                variables[func.__name__] = func

        if python_import and isinstance(python_import, list):
            import importlib
            for library_name in python_import:
                if library_name not in variables:
                    # Use importlib to properly handle modules and submodules
                    try:
                        module = importlib.import_module(library_name)
                        variables[library_name] = module
                        # For packages like 'dateutil', also import commonly used submodules
                        if library_name == 'dateutil':
                            # Import submodules to make dateutil.easter accessible
                            try:
                                importlib.import_module('dateutil.easter')
                            except ImportError:
                                pass
                    except ImportError:
                        # Fallback to __import__ for backward compatibility
                        variables[library_name] = __import__(library_name)

        table_name = table['table_name']
        row_count = table['row_count'] if "row_count" in table else 10
        row_count = min(row_count, internal_row_count)
        start_row_id = table['start_row_id'] if "start_row_id" in table else 1
        start_row_id = start_row_id + internal_start_row_id
        columns = table['columns']
 
        # PK null_percentage guard: primary key columns must not specify null_percentage
        for col in columns:
            if col.get("is_primary_key") and "null_percentage" in col:
                raise Exception(f"Primary key column {col['column_name']} cannot have null_percentage")
 
        # Optional name-based inference for copy_from_fk
        infer = configurator.config.get("config", {}).get("infer_entity_attrs_by_name", False)
        if infer:
            col_names = {c["column_name"] for c in columns}
            fk_sources = {}  # "customer_id" -> ("customers","id")
            for c in columns:
                cmd = str(c["data"])
                if 'foreign_key(' in cmd:
                    # Parse foreign_key call to extract table and column safely
                    try:
                        idx = cmd.find('foreign_key(')
                        end_idx = cmd.find(')', idx)
                        if end_idx != -1:
                            # Extract the arguments from foreign_key("table", "column")
                            args_str = cmd[idx+len('foreign_key('):end_idx]
                            # Evaluate as a tuple: ("table", "column")
                            fk_sources[c["column_name"]] = eval(f"({args_str})")
                    except:
                        pass  # Skip if parsing fails
 
            for c in columns:
                if c.get("data") in (None, "auto"):
                    name = c["column_name"]
                    if "_" in name:
                        prefix, attr = name.split("_", 1)
                        fk_col = f"{prefix}_id"
                        if fk_col in fk_sources:
                            parent_table, _ = fk_sources[fk_col]
                            c["data"] = f'copy_from_fk("{fk_col}","{parent_table}","{attr}")'
 
        compiled_commands = {}
        for column in columns:
            command = column["data"]
            column_name = column["column_name"]
            
            # Handle 'auto' that wasn't resolved by inference
            if command == "auto":
                raise RuntimeError(f"Column '{column_name}' has data='auto' but could not be automatically inferred. "
                                   f"Ensure infer_entity_attrs_by_name is enabled and the column follows naming conventions.")
            
            if command and isinstance(command, str) and "return " in command:
                func_inner_code = "\n".join(["    " + line for line in command.split("\n")])
                func_name = f"func_" + ''.join(random.choices(string.ascii_lowercase, k=5))
                func_code = f"def {func_name}():\n{func_inner_code}"
                namespace = {}
                exec(func_code, variables, namespace)
                func = namespace[func_name]
                variables[func_name] = func
                command = f"{func_name}()"
            
            compiled_commands[column_name] = compile(f"result = {command}", "<string>", "exec")


        rows = []
        pk_cols = [c["column_name"] for c in columns if c.get("is_primary_key")]
        for row_id in range(start_row_id, start_row_id+row_count):
            util.progress_bar(row_id-start_row_id+1, row_count, f"Table:{table_name}")
            variables["row_id"] = row_id
            self.primary_key_seed = row_id
            new_row = self.generate_fake_row(table_name, columns, variables, compiled_commands)
            rows.append(new_row)
            # Cache full parent row indexed by all PK columns
            if pk_cols:
                self.parent_rows.setdefault(table_name, {})
                for pk_col in pk_cols:
                    self.parent_rows[table_name][new_row[pk_col]] = new_row

        df = pd.DataFrame(rows)
        df.Name = table['table_name']
        df.convert_dtypes() # auto set best fitting type
        for column in columns:
            column_name = column['column_name']
            if "type" in column:
                util.log(f"Converting Column {column_name} to {column['type']}", util.FOREGROUND_COLOR.MAGENTA)
                df[column_name] = df[column_name].astype(column['type'])
            if "null_percentage" in column:
                null_percentage = util.parse_null_percentge(column["null_percentage"])
                num_nulls = int(row_count * null_percentage)
                null_indices = np.random.choice(df.index, size=num_nulls, replace=False)
                df.loc[null_indices, column_name] = None

        util.log(f"{table_name} pandas dataframe created", util.FOREGROUND_COLOR.GREEN)
        return df

    def foreign_key(self, table_name, column_name, distribution="uniform",
                    param=None, parent_attr=None, weights=None):
        """
        Select a foreign key value with configurable distribution.
        
        Args:
            table_name: Parent table name
            column_name: Parent column name (must be a primary key)
            distribution: "uniform" (default), "zipf", or "weighted_parent"
            param: Parameter for zipf distribution (default 1.2)
            parent_attr: Parent attribute for weighted_parent distribution
            weights: Weight mapping for weighted_parent distribution
        """
        if table_name not in self.primary_key_cache:
            raise Exception(f"Table {table_name} not found while looking for primary key")
        if column_name not in self.primary_key_cache[table_name]:
            raise Exception(f"Column {column_name} not found in table {table_name} while looking for primary key")
        
        pk_values = self.primary_key_cache[table_name][column_name]
        n = len(pk_values)
        if n == 0:
            raise Exception(f"No keys in {table_name}.{column_name}")
        
        # Create independent RNG per FK call for determinism
        seed = self._stable_seed(self.primary_key_seed, table_name, column_name, distribution, param, parent_attr)
        rnd = random.Random(seed)
        
        if distribution == "uniform":
            idx = rnd.randrange(n)
            return pk_values[idx]
        
        if distribution == "zipf":
            a = float(param) if param is not None else 1.2
            # weights proportional to 1/(i+1)^a over existing order
            w = [1.0 / ((i + 1) ** a) for i in range(n)]
            total = sum(w)
            r = rnd.random() * total
            cum = 0.0
            for i, wi in enumerate(w):
                cum += wi
                if r <= cum:
                    return pk_values[i]
            return pk_values[-1]
        
        if distribution == "weighted_parent":
            if parent_attr is None or weights is None:
                raise Exception("weighted_parent requires parent_attr and weights")
            parent_map = self.parent_rows.get(table_name, {})
            # map index -> weight via parent attribute
            mapped = []
            for i, pk in enumerate(pk_values):
                row = parent_map.get(pk)
                val = None if row is None else row.get(parent_attr)
                mapped.append(float(weights.get(str(val), 1.0)))
            total = sum(mapped)
            r = rnd.random() * total
            cum = 0.0
            for i, wi in enumerate(mapped):
                cum += wi
                if r <= cum:
                    return pk_values[i]
            return pk_values[-1]
        
        raise Exception(f"Unknown distribution {distribution}")

    def generate_fake_row(self, table_name:str, columns:dict, variables:dict, compiled_commands:dict=None):
        """
        Generate a fake row using two-phase evaluation.
        Phase A: PK columns and foreign_key columns
        Phase B: remaining columns (including copy_from_fk)
        """
        result = {}
        
        def _exec_col(col):
            """Execute a single column's data expression."""
            column_name = col["column_name"]
            code = compiled_commands[column_name]
            command = col["data"]
            variables["command"] = command
            is_primary_key = col.get("is_primary_key", False)
            
            try:
                exec(code, variables)
            except AttributeError as error:
                raise RuntimeError(f"Attribute can not be found. {command} \n {error}")
            except NameError as error:
                raise RuntimeError(f"Function can not be found. {command} \n {error}")
            except Exception as error:
                raise error
            
            generated_value = variables["result"]
            variables[column_name] = generated_value
            result[column_name] = generated_value
            
            if is_primary_key:
                if table_name not in self.primary_key_cache:
                    self.primary_key_cache[table_name] = {}
                if column_name not in self.primary_key_cache[table_name]:
                    self.primary_key_cache[table_name][column_name] = []
                self.primary_key_cache[table_name][column_name].append(generated_value)
        
        # Phase A: PK columns without dependencies and columns with foreign_key
        # Phase B: columns that depend on other columns (including PKs with dependencies)
        phase_a = []
        phase_b = []
        col_names = {c["column_name"] for c in columns}
        
        for col in columns:
            expr = str(col["data"])
            has_fk = "foreign_key(" in expr
            is_pk = col.get("is_primary_key", False)
            
            # Check if expression references other column names
            has_dependencies = False
            if not has_fk and expr:
                # Check if any column name appears in the expression
                for col_name in col_names:
                    if col_name != col["column_name"] and col_name in expr:
                        has_dependencies = True
                        break
            
            # Phase A: independent PKs, foreign keys, and expressions with no column dependencies
            # Phase B: expressions that reference other columns
            if (is_pk or has_fk or not has_dependencies):
                phase_a.append(col)
            else:
                phase_b.append(col)
        
        for col in phase_a:
            _exec_col(col)
        
        # Make current row visible to copy_from_fk during phase B
        self._current_row = result
        try:
            for col in phase_b:
                _exec_col(col)
        finally:
            self._current_row = None
        
        return result


def to_pandas(config_source:str, table_name=None, **kwargs):
    table_faker = TableFaker()
    return table_faker.to_pandas(config_source, table_name, **kwargs)

def to_csv(config_source, target_file_path=None, table_name=None, **kwargs) :
    table_faker = TableFaker()
    return table_faker.to_target("csv", config_source, target_file_path, table_name, **kwargs)

def to_json(config_source, target_file_path=None, table_name=None, **kwargs) :
    table_faker = TableFaker()
    return table_faker.to_target("json", config_source, target_file_path, table_name, **kwargs)

def to_excel(config_source, target_file_path=None, table_name=None, **kwargs) :
    table_faker = TableFaker()
    return table_faker.to_target("excel", config_source, target_file_path, table_name, **kwargs)

def to_parquet(config_source, target_file_path=None, table_name=None, **kwargs) :
    table_faker = TableFaker()
    return table_faker.to_target("parquet", config_source, target_file_path, table_name, **kwargs)

def to_deltalake(config_source, target_file_path=None, table_name=None, **kwargs) :
    table_faker = TableFaker()
    return table_faker.to_target("deltalake", config_source, target_file_path, table_name, **kwargs)

def to_sql(config_source, target_file_path=None, table_name=None, **kwargs) :
    table_faker = TableFaker()
    return table_faker.to_target("sql", config_source, target_file_path, table_name, **kwargs)

def to_target(file_type, config_source, target_file_path, table_name=None, **kwargs) :
    table_faker = TableFaker()
    return table_faker.to_target(file_type, config_source, target_file_path, table_name, **kwargs)

def yaml_to_json(config_source, target_file_path=None):
    conf = config.Config(config_source)
    conf.to_json(target_file_path)

def avro_to_yaml(avro_file_path, target_file_path=None):
    config.Config.avro_to_yaml(avro_file_path, target_file_path)

def csv_to_yaml(csv_file_path, target_file_path=None):
    config.Config.csv_to_yaml(csv_file_path, target_file_path)