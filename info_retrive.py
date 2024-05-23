from Computers import  Computers
from Data import  Data
from requests import get
import json
from enums import Countries
def get_connected_and_signed(connected_count:int):
    signed_count = Computers.get_connected_count()
    return {
        "signed": signed_count,
        "connected": connected_count
        }

def get_data_stats():
    recoverd_count = Data.get_recoverd_data_sum()
    not_recoverd = Data.get_actual_data_sum()-recoverd_count
    return {"real": not_recoverd,
            "recoverd": recoverd_count
            }

def get_client_location():
    ip = get('https://api.ipify.org').text
    location_info =  json.loads(get(f'http://ip-api.com/json/{ip}').text)
    return Countries[location_info['country']]

print(get_client_location())