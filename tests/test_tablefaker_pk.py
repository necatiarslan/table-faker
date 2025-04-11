import sys, os, shutil
sys.path.append(os.path.abspath("."))

from tablefaker import tablefaker

directory_path = 'tests/exports'
if os.path.isdir(directory_path):
    shutil.rmtree(directory_path)
    os.mkdir(directory_path)

os.system('clear')

tablefaker.to_csv("tests/test_table_pk.yaml", "./tests/exports")
