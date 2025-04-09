import requests
from dotenv import load_dotenv
import os
import json
from time import sleep
import datetime as dt
import pytz
from time import time


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

    write_json_data_to_file("data.json", data, "w")
    return data["access_token"]


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

    write_json_data_to_file("airport_information.json", data, "w")

    if len(data["data"]) != 0:
        return data["data"][0]["iataCode"]
    else:
        return "Empty"


def column_items_from_sheet(column_name: str) -> list:
    secret_header = {
        "Authorization": f"Bearer {SHEETY_BEARER_TOKEN}"
    }

    response = requests.get(url=SHEETY_GET_URL, headers=secret_header)
    response.raise_for_status()
    sheet_data = response.json()["prices"]

    write_json_data_to_file("sheet_data.json", sheet_data, "w")

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


def update_minimum_prices_on_sheet(min_price_dict: dict) -> None:
    for row_id, new_price in min_price_dict.items():
        url = f"https://api.sheety.co/cb9b634eadcc48cd4882c8d300e63f7c/flightDealsData/prices/{row_id}"
        headers = {
            "Authorization": f"Bearer {SHEETY_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        body = {
            "price": {
                "lowestPrice": new_price
            }
        }
        response = requests.put(url=url, headers=headers, json=body)
        response.raise_for_status()
        print(f"Updated Row {row_id} with new lowest price: ${new_price}")


def search_flight() -> None:
    message = "Cheap Flights From London Available!"
    today = dt.datetime.now().astimezone(pytz.UTC)
    one_week_later = today + dt.timedelta(days=1*7)
    tomorrow = today + dt.timedelta(days=1)

    open("flight_offers.ndjson", "w").close()

    iata_codes = column_items_from_sheet("iataCode")
    cities = column_items_from_sheet("city")
    lowest_prices = column_items_from_sheet("lowestPrice")

    cheep_flights_found = False
    new_min_prices = {}

    for i in range(len(iata_codes)):
        current_lowest = float(lowest_prices[i])
        city = cities[i]
        iata = iata_codes[i]
        row_id = i + 2

        date_cursor = tomorrow

        while date_cursor < one_week_later:
            url = f"{AMADEUS_FLIGHT_OFFERS_URL}?originLocationCode=LON&destinationLocationCode={iata}&departureDate={date_cursor.strftime('%Y-%m-%d')}&adults=1&nonStop=true&currencyCode=USD&max=250"
            headers = {
                "Authorization": f"Bearer {AMADEUS_ACCESS_TOKEN}"
            }

            response = requests.get(url=url, headers=headers)
            response.raise_for_status()
            data = response.json()

            with open("flight_offers.ndjson", "a") as file:
                for offer in data.get("data", []):
                    json.dump(offer, file)
                    file.write("\n")

            offers = data.get("data", [])

            for offer in offers:
                net_price = float(offer["price"]["total"])
                if net_price < current_lowest:
                    departure = offer["itineraries"][0]["segments"][0]["departure"]
                    arrival = offer["itineraries"][0]["segments"][0]["arrival"]

                    dep_date, dep_time = departure["at"].split("T")
                    arr_date, arr_time = arrival["at"].split("T")

                    message += f"""\n\nTo {city}:\n\tTotal Price: ${net_price}
                                \tFrom: {departure["iataCode"]} at {dep_time} UTC on {dep_date}
                                \tTo: {arrival["iataCode"]} at {arr_time} UTC on {arr_date}"""
                    current_lowest = net_price
                    new_min_prices[row_id] = net_price
                    cheep_flights_found = True

            date_cursor += dt.timedelta(days=1)
            sleep(0.05)

    if cheep_flights_found:
        message_me(message)
        update_minimum_prices_on_sheet(new_min_prices)
    else:
        print("No cheap flight found!")


if __name__ == "__main__":
    tic = time()

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
    SHEETY_BEARER_TOKEN = os.getenv("SHEETY_BEARER_TOKEN")
    AMADEUS_ACCESS_TOKEN = amadeus_authorization_token()
    SHEETY_GET_URL = SHEETY_API
    object_id = 2

    search_flight()

    tac = time()
    print(f"Time during run: {tac - tic} seconds.")