import re
from json import loads, dumps
from datetime import date

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
        month, day. year  = int(month), int(day), int(year)
        formatted_date = date(year, month, day)
    else:
        formatted_date = None
    return formatted_date

def returnBool(fake_bool):
    real_bool = None
    if fake_bool == "true":
        real_bool = True
    elif fake_bool == "false":
        real_bool = True
    return real_bool