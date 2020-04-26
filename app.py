from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse


app = Flask(__name__)


@app.route('/bot', methods=['POST'])
def bot():
    incoming_values = request.values
    print(incoming_values)

    latitude = incoming_values.get('Latitude')
    longitude = incoming_values.get('Longitude')
    geo_location = (latitude, longitude)

    incoming_msg = incoming_values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False

    national_api = 'https://api.covid19india.org/data.json'
    response = get_response(national_api)
    statewise_data_list = response.get('statewise')
    state_names = [each["state"].lower() for each in statewise_data_list]

# TODO: Type *national* to get the latest country-wide Covid-19 stats.
    welcome_message = f'''
Hi there! I am a bot that gives you the latest information on Covid-19 from India.
-Type *Total* to get the latest country-wide Covid-19 stats.
-Type the exact name of a state to get it's latest Covid-19 stats.
-Send your location to get the latest stats from your district along with essential services available near your city.
-Type *help* anytime to to learn how to interact with me.
'''

    help_message = f'''
Say *hi* to begin an interaction with me anytime.
-Type *Total* to get the latest country-wide Covid-19 stats.
-Type the exact name of a state to get it's latest Covid-19 stats.
-Send your location to get the latest stats from your district along with essential services available near your city.
'''

    fallback_message = 'Sorry, I did not quite get that. Type *help* to learn how to interact with me.'

    greeting_tokens = ['hi', 'hello', 'hey']
    if incoming_msg in greeting_tokens:
        # return greeting message
        msg.body(welcome_message)
        responded = True

    if incoming_msg in state_names:
        # return stats
        state = incoming_msg
        i = state_names.index(state)
        statewise_data = statewise_data_list[i]
        data_message = get_data_message(state, statewise_data)
        msg.body(data_message)
        responded = True
        msg.body(data_message)
        responded = True


def get_response(url):
    response = requests.get(url)
    return response.json()


def get_data_message(state, data):
    active = data.get('active')
    confirmed = data.get('confirmed')
    recovered = data.get('recovered')
    deaths = data.get('deaths')
    delta_confirmed = data.get('deltaconfirmed')
    delta_deaths = data.get('deltadeaths')
    delta_recovered = data.get('deltarecovered')
    last_updated_timestamp = data.get('lastupdatedtime')
    data_message = f'''
*Latest Covid-19 data from {state.title()}*
Total cases:
Active: {active}
Confirmed: {confirmed}
Recovered: {recovered}
Deceased: {deaths}
New cases:
Confirmed: {delta_confirmed}
Recovered: {delta_recovered}
Deceased: {delta_deaths}

Last Updated: {last_updated_timestamp}

View more: https://www.covid19india.org/
'''
    return data_message


if __name__ == '__main__':
    app.run()
