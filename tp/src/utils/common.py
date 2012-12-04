import re
from json import loads, dumps
from datetime import datetime
from datetime import time
from dateutil.tz import *

twentyfour_hour = {
                   '0' : 0, '1' : 13, '2' : 14, '3' : 15, '4' : 16,
                   '5' : 17, '6' : 18, '7' : 19, '8' : 20,
                   '9' : 21, '10' : 22, '11' : 23, '12' : 0,
                  }

twentyfour_hour_reversed = {
                   '13' : 1, '14' : 2, '15' : 3, '16' : 4,
                   '17' : 5, '18' : 6, '19' : 7, '20' : 8,
                   '21' : 9, '22' : 10, '23' : 11
                  }


days_of_the_week = {
                   '0' : 'Sunday', '1' : 'Monday',
                   '2' : 'Tuesday', '3' : 'Wednesday',
                   '4' : 'Thursday', '5' : 'Friday',
                   '6' : 'Saturday'
                   }

week_day = {
            'Monday' : '0',
            'Tuesday' : '1',
            'Wednesday' : '2',
            'Thursday' : '3',
            'Friday' : '4',
            'Saturday' : '5',
            'Sunday' : '6'
            }


GMT_BY_TIME = {
              '+10:30' : 'LHST', '+3:30' : 'IRST', '+12:45' : 'CHAST',
              '+5:45' : 'NPT', '+8:45' : 'ACWST', '+9:30' : 'ACST',
              '+8:00' : 'ACIT', '+6:30' : 'MMT', '+8:15' : 'APO',
              '+12' : 'WFT', '+13:45' : 'CHADT', '+5:30' :'IST',
              '+11:30' : 'NFT', '+13' : 'TOT', '+4:30' : 'IRDT',
              '+11' : 'VUT', '+10' : 'YAPT', '+14' : 'LINT',
              '+3' : 'SYST', '+2' : 'WAST', '+1' : 'WEST',
              '+7' : 'WIB', '+6' : 'YEKST', '+5' : 'YEKT',
              '+4' : 'SCT', '+9' : 'YAKT', '+8' : 'WITA'
              }

def verify_json_is_valid(data):
    verified = True
    json_data = None
    try:
        json_data = loads(data)
    except ValueError as e:
        verified = False
    return(verified, json_data)


def date_parser(unformatted_date):
    if unformatted_date != "":
        if type(unformatted_date) == unicode:
            unformatted_date.encode('utf-8')
        month, day, year = re.split(r'-|/', unformatted_date)
        month, day, year  = int(month), int(day), int(year)
        formatted_date = datetime(year, month, day)
    else:
        formatted_date = None
    return formatted_date


def date_time_parser(schedule):
    if type(schedule) == unicode:
        schedule.encode('utf-8')
    try:
        am_pm = re.search(r'(AM|PM)', schedule, re.IGNORECASE).group()
        schedule = re.sub(r'\s+(?i)AM|\s+(?i)PM', '', schedule, re.IGNORECASE)
        am_pm = am_pm.upper()
    except Exception as e:
        am_pm = "AM"
        if len(schedule.split(" ")) == 1:
            if int(schedule.split(":")[0]) > 12:
                new_hour = twentyfour_hour_reversed[str(int(schedule.split(":")[0]))]
                schedule = re.sub(r'([0-9]+)(:[0-9]+)', str(new_hour)+'\g<2>', schedule)
                am_pm = "PM"
        elif len(schedule.split(" ")) == 2:
            if int(schedule.split(" ")[1].split(":")[0]) > 12:
                new_hour = twentyfour_hour_reversed[str(int(schedule.split(" ")[1].split(":")[0]))]
                schedule = re.sub(r'([0-9]+)(:[0-9]+)', str(new_hour)+'\g<2>', schedule)
                am_pm = "PM"
        am_pm = am_pm.upper()
    pformatted = map(lambda x: int(x),re.split(r'\/|:|\s+', schedule))
    print pformatted
    if len(pformatted) == 5 and am_pm:
        month, day, year, hour, minute = pformatted
        if am_pm == 'PM' and str(hour) in twentyfour_hour or \
                am_pm == 'AM' and str(hour) == '0':
            hour = twentyfour_hour[str(hour)]
        formatted_date = datetime(year, month, day,
                int(hour), int(minute))
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


def return_bool(fake_bool):
    fake_bool = fake_bool.lower()
    real_bool = None
    if fake_bool == "true":
        real_bool = True
    elif fake_bool == "false":
        real_bool = False
    return real_bool


def get_expire_from_cert(cert):
    asn1_time = re.search(r'([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})', cert).group(1,2,3,4,5,6)
    t = map(lambda x: int(x), asn1_time)
    return datetime(t[0], t[1], t[2], t[3], t[4], t[5])


def return_datetime(timestamp):
    stamp_length = len(timestamp)
    timestamp = int(timestamp)
    valid_timestamp = False
    if stamp_length == 13:
        timestamp = timestamp / 1000
        valid_timestamp = True
    elif stamp_length == 10:
        valid_timestamp = True
    if valid_timestamp:
        parsed_time = datetime.fromtimestamp(timestamp).strftime('%m/%d/%Y %H:%M')
        return (parsed_time)
    else:
        return ("Invalid TimeStamp")


def return_days(days):
    if len(days) == 7:
        days_enabled = []
        days_not_enabled = []
        for day in range(len(days)):
            if days[day] == '1':
                days_enabled.append(days_of_the_week[str(day)])
            else:
                days_not_enabled.append(days_of_the_week[str(day)])
        return(days_enabled, days_not_enabled)


def return_utc(non_utc_time):
    utc_time = non_utc_time.replace(tzinfo=tzlocal())\
                             .astimezone(tzoffset('GMT', 0))
    return utc_time


