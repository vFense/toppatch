import re
from json import loads, dumps
from datetime import datetime
from datetime import time

twentyfour_hour = {
                   '1' : 13, '2' : 14, '3' : 15, '4' : 16,
                   '5' : 17, '6' : 18, '7' : 19, '8' : 20,
                   '9' : 21, '10' : 22, '11' : 23, '12' : 0,
                  }

days_of_the_week = {
                   '0' : 'Sunday', '1' : 'Monday',
                   '2' : 'Tuesday', '3' : 'Wednesday',
                   '4' : 'Thursday', '5' : 'Friday',
                   '6' : 'Saturday'
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
        if type(unformatted_date) == unicode:
            unformatted_date.encode('utf-8')
        month, day, year = re.split(r'-|/', unformatted_date)
        month, day, year  = int(month), int(day), int(year)
        formatted_date = datetime(year, month, day)
    else:
        formatted_date = None
    return formatted_date

def dateTimeParser(schedule):
    if type(schedule) == unicode:
        schedule.encode('utf-8')
    try:
        am_pm = re.search(r'(AM|PM)', schedule).group()
        schedule = re.sub(r'\s+AM|\s+PM', '', schedule)
    except Exception as e:
        am_pm = None
    pformatted = map(lambda x: int(x),re.split(r'\/|:|\s+', schedule))
    if len(pformatted) == 5 and am_pm:
        month, day, year, hour, minute = pformatted
        if am_pm == 'PM' and str(hour) in twentyfour_hour or \
                am_pm == 'AM' and str(hour) == '0':
            hour = twentyfour_hour[str(hour)]
        formatted_date = datetime(year, month, day,
                hour, minute)
    elif len(pformatted) == 3:
        month, day, year = pformatted
        formatted_date = datetime(year, month, day)
    elif len(pformatted) == 2 and am_pm:
        hour, minute = pformatted
        if am_pm == 'PM' and str(hour) in twentyfour_hour or \
                am_pm == 'AM' and str(hour) == '0':
            hour = twentyfour_hour[str(hour)]
        formatted_date = time(hour, minute)
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

def returnDatetime(timestamp):
    stamp_length = len(timestamp)
    timestamp = int(timestamp)
    valid_timestamp = False
    if stamp_length == 13:
        timestamp = timestamp / 1000
        valid_timestamp = True
    elif stamp_length == 10:
        valid_timestamp = True
    if valid_timestamp:
        return (datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))
    else:
        return ("Invalid TimeStamp")

def returnDays(days):
    if len(days) == 7:
        days_enabled = []
        days_not_enabled = []
        for day in range(len(days)):
            if days[day] == '1':
                days_enabled.append(days_of_the_week[str(day)])
            else:
                days_not_enabled.append(days_of_the_week[str(day)])
        return(days_enabled, days_not_enabled)
