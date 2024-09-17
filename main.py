import requests
from dotenv import load_dotenv
import os
import json
from time import sleep

load_dotenv("secrets.env")

with open("sheet_url.txt", mode="r") as file:
    SHEETY_API = file.read()

ALERTZY_PASSWORD = os.getenv("ALERTZY_PASSWORD")
ALERTZY_ACCOUNT_KEY = os.getenv("ALERTZY_ACCOUNT_KEY")
ALERTZY_URL = "https://alertzy.app/send"
AMADEUS_BASE_URL = "https://test.api.amadeus.com/v1"
AMADEUS_AIRPORT_FIND_URL = "/reference-data/locations"
AMADEUS_ACCESS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
AMADEUS_ACCESS_TOKEN = ""
SHEETY_BEARER_TOKEN = os.getenv("SHEETY_BEARER_TOKEN")
SHEETY_GET_URL = SHEETY_API
object_id = 2
SHEETY_PUT_URL = SHEETY_API + f"/{object_id}"


def write_json_data_to_file(file_name, data) -> None:
    with open(file_name, mode="w") as file:
        json.dump(data, file, indent=4)


def amadeus_authorization_token() -> str:
    content_header = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET
    }
    
    response = requests.post(url=AMADEUS_ACCESS_TOKEN_URL, data=params, headers=content_header)
    response.raise_for_status()
    data = response.json()
    
    file_name = "data.json"
    write_json_data_to_file(file_name, data)

    # with open(file_name, mode="r") as file:
    #     data = json.load(file)
    
    # print(response.text)
    return data["access_token"]


AMADEUS_ACCESS_TOKEN += amadeus_authorization_token()


def amadeus_city_code(message: str) -> str:
    sleep(0.2)
    secret_header = {
        "Authorization": f"Bearer {AMADEUS_ACCESS_TOKEN}"
    }
    params = {
        "subType": "CITY",
        "keyword": message
    }
    
    response = requests.get(url=AMADEUS_BASE_URL+AMADEUS_AIRPORT_FIND_URL, params=params, headers=secret_header)
    response.raise_for_status()
    data = response.json()

    file_name = "airport_information.json"
    write_json_data_to_file(file_name, data)

    # with open(file_name, mode="r") as file:
    #     data = json.load(file)
    
    # print(response.text)
    if len(data["data"]) != 0:
        return data["data"][0]["iataCode"]
    else:
        return "Emtpy"


def city_names() -> list:
    secret_header = {
        "Authorization": f"Bearer {SHEETY_BEARER_TOKEN}"
        }
    
    response = requests.get(url=SHEETY_GET_URL, headers=secret_header)
    response.raise_for_status()
    sheet_data = response.json()["prices"]
    
    file_name = "sheet_data.json"
    write_json_data_to_file(file_name, sheet_data)

    city_names = [row["city"] for row in sheet_data]

    # print(response.text)
    return city_names


def upload_iata_codes_to_sheet(iata_codes: list, object_id: int) -> None:
    while object_id <= len(iata_codes) + 1:
        secret_header = {
            "Authorization": f"Bearer {SHEETY_BEARER_TOKEN}",
            "Content-Type": "application/json"
            }
        data = {
            "price": {
                "iataCode": iata_codes[object_id - 2]
            }
        }
        SHEETY_PUT_URL = f"https://api.sheety.co/cb9b634eadcc48cd4882c8d300e63f7c/flightDealsData/prices/{object_id}"

        response = requests.put(url=SHEETY_PUT_URL, headers=secret_header, json=data)
        # print(response.text)
        response.raise_for_status()
        sheet_data = response.json()["price"]
        
        file_name = "sheet_data.json"
        write_json_data_to_file(file_name, sheet_data)

        object_id += 1


def search_flight() -> None:
    


# cities = city_names()
# iata_codes = [amadeus_city_code(message=city) for city in cities]
# upload_iata_codes_to_sheet(iata_codes=iata_codes, object_id=object_id)

# print("Successfull")