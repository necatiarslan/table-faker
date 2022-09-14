import json
import string
import faker
from enum import Enum
from pandas import DataFrame
import avro.schema

class ExportFormat(Enum):
    CSV = 1,
    Parquet = 2,
    Avro = 3,
    JSON = 4,
    HTML = 5,
    XML = 6,
    Excel = 7,
    AnsiSqlInsertStatement = 8
    SqlServerInsertStatement = 9,
    OracleInsertStatement = 10,
    MySqlInsertStatement = 11,
    PostgreInsertStatement = 12,


class TableFaker:
    
    def SetSchema(path:string):
        schema = avro.schema.parse(open(path, "rb").read())
        

    def SaveFakeData(format: ExportFormat, path:string):
        pass

    def GetFakePandasDataFrame():
        pass

