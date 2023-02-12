from datetime import datetime

def now():
    """ time without miliseconds """
    return datetime.strptime(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")