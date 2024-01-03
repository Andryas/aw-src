from datetime import datetime, date, timedelta

def now(as_date=True, days=0):
    """ time without miliseconds """
    x = datetime.now()
    x = x - timedelta(days=days)
    x = str(x.strftime("%Y-%m-%d %H:%M:%S"))
    if as_date == True:
        return datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    else:
        return x
    
def today(as_date=True):
    if as_date == True:
        return date.today()
    else:
        return str(date.today().strftime("%Y-%m-%d"))
