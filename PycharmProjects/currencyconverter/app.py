from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    # Extract parameters from the incoming request (Dialogflow webhook)
    data = request.get_json()
    source_currency = data['queryResult']['parameters']['unit-currency']['currency']
    amount = data['queryResult']['parameters']['unit-currency']['amount']
    target_currency = data['queryResult']['parameters']['currency-name']

    # Print the extracted values (for debugging purposes)
    print(f"Source Currency: {source_currency}")
    print(f"Amount: {amount}")
    print(f"Target Currency: {target_currency}")

    # Fetch the conversion factor from an external API
    conversion_rate = fetch_conversion_factor(source_currency, target_currency)

    if conversion_rate is not None:
        # Perform the currency conversion
        converted_amount = round(amount * conversion_rate, 2)
        result_message = f"{amount} {source_currency} is equal to {converted_amount} {target_currency}"
    else:
        result_message = "Sorry, I couldn't fetch the conversion rate."

    # Return the result as a response to Dialogflow
    return jsonify({
        "fulfillmentText": result_message
    })


def fetch_conversion_factor(source, target):
    url = f"https://v6.exchangerate-api.com/v6/f52c25246947b0e30b461175/latest/{source}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        print(f"API Response: {data}")  # Print the full API response for debugging

        # Corrected to use 'conversion_rates' instead of 'rates'
        if "conversion_rates" in data and target in data["conversion_rates"]:
            return data["conversion_rates"][target]
        else:
            print(f"Error: Target currency {target} not found.")
            return None
    else:
        print(f"Error: Failed to fetch data from the API. Status code: {response.status_code}")
        return None


if __name__ == "__main__":
    app.run(debug=True)
