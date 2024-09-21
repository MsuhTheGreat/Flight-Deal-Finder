import requests
from dotenv import load_dotenv
import os
import json
from time import sleep
import datetime as dt
import pytz

load_dotenv("secrets.env")

with open("sheet_url.txt", mode="r") as file:
    SHEETY_API = file.read()

ALERTZY_PASSWORD = os.getenv("ALERTZY_PASSWORD")
ALERTZY_ACCOUNT_KEY = os.getenv("ALERTZY_ACCOUNT_KEY")
ALERTZY_URL = "https://alertzy.app/send"
AMADEUS_BASE_URL = "https://test.api.amadeus.com"
AMADEUS_AIRPORT_FIND_URL = AMADEUS_BASE_URL + "/v1/reference-data/locations"
AMADEUS_ACCESS_TOKEN_URL = AMADEUS_BASE_URL + "/v1/security/oauth2/token"
AMADEUS_FLIGHT_OFFERS_URL = AMADEUS_BASE_URL + "/v2/shopping/flight-offers"
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
AMADEUS_ACCESS_TOKEN = ""
SHEETY_BEARER_TOKEN = os.getenv("SHEETY_BEARER_TOKEN")
SHEETY_GET_URL = SHEETY_API
object_id = 2
SHEETY_PUT_URL = SHEETY_API + f"/{object_id}"


def write_json_data_to_file(file_name, data, mode) -> None:
    with open(file_name, mode=mode) as file:
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
    write_json_data_to_file(file_name, data, "w")

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
    
    response = requests.get(url=AMADEUS_AIRPORT_FIND_URL, params=params, headers=secret_header)
    response.raise_for_status()
    data = response.json()

    file_name = "airport_information.json"
    write_json_data_to_file(file_name, data, "w")

    # with open(file_name, mode="r") as file:
    #     data = json.load(file)
    
    # print(response.text)
    if len(data["data"]) != 0:
        return data["data"][0]["iataCode"]
    else:
        return "Emtpy"


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
        write_json_data_to_file(file_name, sheet_data, "w")

        object_id += 1


def column_items_from_sheet(column_name: str) -> list:
    secret_header = {
        "Authorization": f"Bearer {SHEETY_BEARER_TOKEN}"
        }
    
    response = requests.get(url=SHEETY_GET_URL, headers=secret_header)
    response.raise_for_status()
    sheet_data = response.json()["prices"]
    
    file_name = "sheet_data.json"
    write_json_data_to_file(file_name, sheet_data, "w")

    return [row[column_name] for row in sheet_data]


def message_me(message: str) -> None:
    group = "API Involving Projects"
    params = {
        "accountKey": ALERTZY_ACCOUNT_KEY,
        "title": "Cheep Flights",
        "message": message,
        "group": group
    }

    response = requests.post(url=ALERTZY_URL, json=params)
    response.raise_for_status()
    print(response.text)
    print("Message Sent!")


def search_flight() -> None:
    message = "Cheep Flights From London Available!"
    today = dt.datetime.now()
    today = today.astimezone(pytz.UTC)
    six_month_later = today + dt.timedelta(days=6*30)
    tomorrow = today + dt.timedelta(days=1)

    iata_codes = column_items_from_sheet("iataCode")
    cities = column_items_from_sheet("city")
    lowest_prices = column_items_from_sheet("lowestPrice")

    cheep_flights_found = False
    i = 0
    while i < len(iata_codes):
        while tomorrow < six_month_later:
            secret_header = {
                "Authorization": f"Bearer {AMADEUS_ACCESS_TOKEN}"
            }
            # params = {
            #     "originLocationCode": "LON",
            #     "nonStop": True,
            #     "destinationLocationCode": iata_code,
            #     "departureDate": tomorrow.strftime("%Y-%m-%d"),
            #     "currencyCode": "GBP"
            # }

            url = f"https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode=LON&destinationLocationCode={iata_codes[i]}&departureDate={tomorrow.strftime('%Y-%m-%d')}&adults=1&nonStop=true&currencyCode=USD&max=250"
            response = requests.get(url=url, headers=secret_header)
            print(response.text)
            response.raise_for_status()
            data = response.json()

            # file_name = "flight_offers.json"
            # write_json_data_to_file(file_name, data, "a")

            offers = data["data"]

            for offer in offers:
                net_price = float(offer["price"]["total"])
                if net_price < float(lowest_prices[i]):
                    departure_iata_code = offer["itineraries"][0]["segments"][0]["departure"]["iataCode"]
                    departure_airport_terminal = offer["itineraries"][0]["segments"][0]["departure"]["terminal"]
                    departure_date_time = (offer["itineraries"][0]["segments"][0]["departure"]["at"]).split("T")
                    departure_date = departure_date_time[0]
                    departure_time = departure_date_time[1]

                    arrival_iata_code = offer["itineraries"][0]["segments"][0]["arrival"]["iataCode"]
                    arrival_airport_terminal = offer["itineraries"][0]["segments"][0]["arrival"]["terminal"]
                    arrival_date_time = (offer["itineraries"][0]["segments"][0]["arrival"]["at"]).split("T")
                    arrival_date = arrival_date_time[0]
                    arrival_time = arrival_date_time[1]
                    
                    message += f"\n\nTo {cities[i]}:-\n\tTotal Price: ${net_price} for both sides.\n\tIATA Code of Departure Airport: {departure_iata_code}\n\tDeparture Airport Terminal: {departure_airport_terminal}\n\tDeparture Date: {departure_date} UTC\n\tDeparture Time: {departure_time} UTC\n\tIATA Code of Arrival Airport: {arrival_iata_code}\n\tArrival Airport Terminal: {arrival_airport_terminal}\n\tArrival Date: {arrival_date} UTC\n\tArrival Time: {arrival_time} UTC"
                    cheep_flights_found = True

            tomorrow = tomorrow + dt.timedelta(days=1)
            sleep(0.05)
        
        i += 1
    
    if cheep_flights_found:
        message_me(message)
    else:
        print("No cheap flight found!")


# cities = column_items_from_sheet("city")
# iata_codes = [amadeus_city_code(message=city) for city in cities]
# upload_iata_codes_to_sheet(iata_codes=iata_codes, object_id=object_id)

# print("Successfull")
search_flight()