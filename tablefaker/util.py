import inspect
import datetime
import sys
import shutil
import re

class FOREGROUND_COLOR:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    RESET = '\033[0m'


class BACKGROUND_COLOR:
    BLACK = '\033[40m'
    RED = '\033[41m'
    GREEN = '\033[42m'
    YELLOW = '\033[43m'
    BLUE = '\033[44m'
    MAGENTA = '\033[45m'
    CYAN = '\033[46m'
    WHITE = '\033[47m'
    BRIGHT_BLACK = '\033[100m'
    BRIGHT_RED = '\033[101m'
    BRIGHT_GREEN = '\033[102m'
    BRIGHT_YELLOW = '\033[103m'
    BRIGHT_BLUE = '\033[104m'
    BRIGHT_MAGENTA = '\033[105m'
    BRIGHT_CYAN = '\033[106m'
    BRIGHT_WHITE = '\033[107m'
    RESET = '\033[0m'


class TEXT_ATTRIBUTES:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    INVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    RESET = '\033[0m'


def log(message, message_color=FOREGROUND_COLOR.RESET):
    caller_function = ""
    for func in reversed(inspect.stack()):
        if func.function != "log":
            caller_function = func.function

    print(f"[tablefaker][{caller_function}] - {message_color}{message}{FOREGROUND_COLOR.RESET}")

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
    elif file_type == "sql":
        return ".sql"
    elif file_type == "deltalake":
        return ""
    else:
        return ".txt"

def progress_bar(iteration=1, lenght=1, suffix = "Complete", bar_color=FOREGROUND_COLOR.BRIGHT_GREEN, row_count_color=FOREGROUND_COLOR.BLUE, percent_color=FOREGROUND_COLOR.CYAN, suffix_color=FOREGROUND_COLOR.YELLOW):
    prefix = "Progress:"
    length=50
    fill="█"
    print_end="\n"

    percent = ("{0:.1f}").format(100 * (iteration / float(lenght)))
    percent = percent_color + str(percent) + "%" + FOREGROUND_COLOR.RESET

    filled_length = int(length * iteration // lenght)
    bar = bar_color + fill * filled_length + '-' * (length - filled_length) + FOREGROUND_COLOR.RESET
    
    row_count = row_count_color + f"{iteration}/{lenght}" + FOREGROUND_COLOR.RESET
    suffix = suffix_color + suffix + FOREGROUND_COLOR.RESET

    progress_bar_text = f"\r{prefix} |{bar}| {row_count} | {percent} {suffix}"
    line_lenght = shutil.get_terminal_size((80, 20)).columns
    if get_length_without_color_codes(progress_bar_text) > line_lenght:
        progress_bar_text = progress_bar_text[:line_lenght]
    else:
        progress_bar_text += " " * (line_lenght - len(progress_bar_text))

    sys.stdout.write(progress_bar_text)
    sys.stdout.flush()

    if iteration >= lenght:
        sys.stdout.write(print_end)
        sys.stdout.flush()

def get_length_without_color_codes(text):
    # Remove ANSI escape codes using regular expression
    cleaned_text = re.sub(r'\x1b\[([0-9;]*)m', '', text)
    return len(cleaned_text)
