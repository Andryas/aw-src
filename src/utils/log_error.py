from src.utils.lubridate import today

def log_error(error_message, filename=""):
    with open("~/log/" + filename + today(False) + ".txt", "a+") as error_file:  # "a" means append mode
        error_file.write(f"{error_message}\n")