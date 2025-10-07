import sys, os, shutil
sys.path.append(os.path.abspath("."))

from tablefaker import tablefaker

directory_path = './samples/bank/exports/'
if not os.path.exists(directory_path):
    os.makedirs(directory_path)
elif os.path.isdir(directory_path):
    shutil.rmtree(directory_path)
    os.makedirs(directory_path)

tablefaker.to_csv("./samples/bank/bank.yaml", "./samples/bank/exports/")