from datetime import datetime, date

def now(as_date=True):
    """ time without miliseconds """
    x = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if as_date == True:
        return datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    else:
        return x
    
def today(as_date=True):
    if as_date == True:
        return date.today()
    else:
        return str(date.today().strftime("%Y-%m-%d"))
