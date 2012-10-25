import re
from json import loads, dumps
from datetime import datetime

twentyfour_hour = {
                   '1' : 13, '2' : 14, '3' : 15, '4' : 16,
                   '5' : 17, '6' : 18, '7' : 19, '8' : 20,
                   '9' : 21, '10' : 22, '11' : 23, '12' : 0,
                  }

def verifyJsonIsValid(data):
    verified = True
    json_data = None
    try:
        json_data = loads(data)
    except ValueError as e:
        verified = False
    return(verified, json_data)

def dateParser(unformatted_date):
    if unformatted_date != "":
        month, day, year = re.split(r'-|/', unformatted_date)
        month, day, year  = int(month), int(day), int(year)
        formatted_date = datetime(year, month, day)
    else:
        formatted_date = None
    return formatted_date

def dateTimeParser(schedule):
    am_pm = re.search(r'(AM|PM)', schedule).group()
    schedule = re.sub(r'\s+AM|\s+PM', '', schedule)
    pformatted = map(lambda x: int(x),re.split(r'\/|:|\s+', schedule))
    if len(pformatted) == 5:
        month, day, year, hour, minute = pformatted
        if am_pm == 'PM' and str(hour) in twentyfour_hour or \
                am_pm == 'AM' and str(hour) == '0':
            hour = twentyfour_hour[str(hour)]
        formatted_date = datetime(year, month, day,
                hour, minute)
    elif len(pformatted) == 3:
        month, day, year = pformatted
        formatted_date = datetime(year, month, day)
    return formatted_date

def returnBool(fake_bool):
    real_bool = None
    if fake_bool == "true":
        real_bool = True
    elif fake_bool == "false":
        real_bool = False
    return real_bool

def getExpirefromCert(cert):
    asn1_time = re.search(r'([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})', cert).group(1,2,3,4,5,6)
    t = map(lambda x: int(x), asn1_time)
    return datetime(t[0], t[1], t[2], t[3], t[4], t[5])
