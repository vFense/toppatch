from json import loads, dumps

def verifyJsonIsValid(data):
    verified = True
    try:
        json_data = loads(data)
    except ValueError as e:
        verified = False
    return(verified)
