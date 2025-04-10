# ✈️ Cheap Flights Finder

A program written in Python that tracks cheap flight deals from London to various cities using the Amadeus API, stores destination and pricing data in Google Sheets via Sheety, and notifies you using Alertzy if cheaper prices are found.

## 🚀 Features

- 🔍 Searches flight offers from London (LON) to destinations listed in a Google Sheet.

- 🧠 Compares the current prices with the lowest ones stored in the sheet.

- 💾 Updates the sheet if cheaper prices are found.

- 📩 Sends alerts via Alertzy with flight details if deals are detected.

- 📄 Logs data and responses into local .json and .ndjson files for transparency.

## 🧰 Technologies Used

- Python 3

- [Amadeus API](https://developers.amadeus.com/)

- [Sheety](https://sheety.co/)

- [Alertzy](https://alertzy.app/)

- .env for secure credential storage

- ndjson and json files for storing logs and offers

## 📋 Setup Instructions

### 1. Clone the Repository

``` Python
git clone https://github.com/MsuhTheGreat/Flight-Deal-Finder
cd Flight-Deal-Finder
```

### 2. Install Dependencies

``` Python
pip install -r requirements.txt
```

### 3. Environment Variables

Create a .env file in the root directory with the following:

``` Python
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_API_SECRET=your_amadeus_api_secret
SHEETY_BEARER_TOKEN=your_sheety_token
ALERTZY_ACCOUNT_KEY=your_alertzy_key
ALERTZY_PASSWORD=your_alertzy_password
```

### 4. Sheet URL

Create a sheet_url.txt file containing your Sheety API endpoint, like:

``` Python
https://api.sheety.co/your-project-id/flightDealsData/prices
```

## 🧠 How It Works

1. Retrieves destinations, IATA codes, and current lowest prices from the Google Sheet.

2. Queries Amadeus API for flight offers to those destinations for the next 7 days.

3. Compares current offers with the stored lowest price.

4. If a cheaper flight is found:

    - Adds flight details to a notification message.

    - Sends the message via Alertzy.

    - Updates the Google Sheet with the new lowest price.

5. Saves logs to:

    - data.json: Amadeus access token response.

    - sheet_data.json: Sheet contents.

    - flight_offers.ndjson: All retrieved offers.

    - airport_information.json: IATA info (if used).

## 📊 Sample Sheet Structure

| City        | IATA Code | Lowest Price |
|-------------|-----------|--------------|
| New York    | NYC       | $250         |
| Los Angeles | LAX       | $320         |
| Paris       | PAR       | $280         |

## 🕒 Execution

Just run the script:

``` Python
python main.py
```

You'll see updates in terminal and get a push notification if deals are found.

## 📌 Notes

- The script assumes the origin is London (LON).

- You can customize origin, filters (e.g., stops), currency, and date range as needed.

- Make sure to keep your .env file and tokens private and secure.

## 📬 Contact

Made by MsuhTheGreat  
For suggestions, bugs, or improvements, feel free to open an issue or contribute.
