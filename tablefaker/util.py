import inspect
import datetime

def log(message):
    caller_function = ""
    for func in reversed(inspect.stack()):
        if func.function is not "log":
            caller_function = func.function

    print(f"[table-faker][{caller_function}] - {message}")

def get_temp_filename(file_name=None):
    if file_name == None:
        file_name = "exported_file"
    
    now = datetime.datetime.now()
    file_name_date_ext = now.strftime("%Y-%m-%d_%H-%M-%S-%f")

    return f"{file_name}_{file_name_date_ext}"
    