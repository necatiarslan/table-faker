import inspect
import datetime
import sys
import shutil

def log(message):
    caller_function = ""
    for func in reversed(inspect.stack()):
        if func.function != "log":
            caller_function = func.function

    print(f"[tablefaker][{caller_function}] - {message}")

def get_temp_filename(file_name=None):
    if file_name == None:
        file_name = "exported_file"
    
    now = datetime.datetime.now()
    file_name_date_ext = now.strftime("%Y-%m-%d_%H-%M-%S-%f")

    return f"{file_name}_{file_name_date_ext}"

def parse_null_percentge(null_percentage):
    if isinstance(null_percentage, str) and null_percentage[-1] == "%":
        null_percentage = float(null_percentage[0:-1])
    
    if isinstance(null_percentage, str) and null_percentage[0] == "%":
        null_percentage = float(null_percentage[1:])

    if isinstance(null_percentage, int) or isinstance(null_percentage, float):
        if null_percentage >= 0 and null_percentage <= 1:
            return float(null_percentage)
        elif null_percentage >= 0 and null_percentage<= 100:
            return float(null_percentage / 100)

    return float(0)

def get_file_extension(file_type):
    if file_type == "csv":
        return ".csv"
    elif file_type == "json":
        return ".json"
    elif file_type == "parquet":
        return ".parquet"
    elif file_type == "excel":
        return ".xlsx"
    else:
        return ".txt"

def progress_bar(iteration=1, lenght=1, suffix = "Complete"):
    prefix = "Progress:"
    length=50
    fill="█"
    print_end="\n"

    percent = ("{0:.1f}").format(100 * (iteration / float(lenght)))
    filled_length = int(length * iteration // lenght)
    bar = fill * filled_length + '-' * (length - filled_length)
    line_lenght = shutil.get_terminal_size((80, 20)).columns
    
    progress_bar_text = f"\r{prefix} |{bar}| {iteration}/{lenght} | {percent}% {suffix}"
    if len(progress_bar_text) > line_lenght:
        progress_bar_text = progress_bar_text[:line_lenght]
    else:
        progress_bar_text += " " * (line_lenght - len(progress_bar_text))

    sys.stdout.write(progress_bar_text)
    sys.stdout.flush()

    if iteration >= lenght:
        sys.stdout.write(print_end)
        sys.stdout.flush()