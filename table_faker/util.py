import inspect

def log(message):
    caller_function = ""
    for func in reversed(inspect.stack()):
        if func.function is not "log":
            caller_function = func.function

    print(f"[table-faker][{caller_function} - {message}]")