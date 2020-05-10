from flask import Flask, request
import requests
from geopy.geocoders import Nominatim
import constants
import json

from api.messaging import as_twilio_response

# TODO: Type *national* to get the latest country-wide Covid-19 stats.
# TODO: Get district-wise stats
# TODO: Get distance from your location to nearest active case in your city, district, or state
# TODO: Get category wise list of essential services near your location
# TODO: create a mapping of state, city, and district name aliases
# TODO: When incoming message is Resources or Cases send default message as:
#       Your location is set to <the last set location>. To change it, send your location again


app = Flask(__name__)

geolocator = Nominatim(user_agent="covid_bot", timeout=5)


@app.route('/bot', methods=['POST'])
def bot():
    incoming_values = request.values
    print(incoming_values)

    latitude = incoming_values.get('Latitude',  '')
    longitude = incoming_values.get('Longitude', '')
    # geolocator API expects coordinates as a single comma separated string of latitude and longitude
    geo_coordinates_string = " ,".join((latitude, longitude))

    incoming_msg = incoming_values.get('Body', '').lower()

    national_api = 'https://api.covid19india.org/data.json'
    response = get_response(national_api)
    statewise_data_list = response.get('statewise')
    state_names = [each["state"].lower() for each in statewise_data_list]

    district_api = 'https://api.covid19india.org/v2/state_district_wise.json'
    states_with_district_list = get_response(district_api)  # list with each element a dict with key "state"

    welcome_message = f'''
Hi there! I am a bot that gives you the latest information on Covid-19 from India.
-Type *Total* to get the latest country-wide Covid-19 stats.
-Type the exact name of a state to get it's latest Covid-19 stats.
-Send your location to get the latest stats from your district along with essential services available in your region.
-Type *help* anytime to to learn how to interact with me.
'''

    help_message = f'''
Say *hi* to begin an interaction with me anytime.
-Type *Total* to get the latest country-wide Covid-19 stats.
-Type the exact name of a state to get it's latest Covid-19 stats.
-Send your location to get the latest stats from your district along with essential services available in your region.
'''

    fallback_message = 'Sorry, I did not quite get that. Type *help* to learn how to interact with me.'

    greeting_tokens = ['hi', 'hello', 'hey']
    if incoming_msg in greeting_tokens:
        # return greeting message
        return as_twilio_response(welcome_message)

    if incoming_msg in state_names:
        # return stats
        state = incoming_msg
        i = state_names.index(state)
        statewise_data = statewise_data_list[i]
        statewise_data_message = get_statewise_data_message(state, statewise_data)
        return as_twilio_response(statewise_data_message)

    if 'help' in incoming_msg:
        # return help message
        return as_twilio_response(help_message)

    if latitude:
        # TODO: Replace temporary file operation with nosql DB like mongoDB
        geo_location_dict = get_reverse_geocode(geo_coordinates_string)  # tuple of city, state
        location_message = get_location_message(geo_location_dict)
        # save geo_location_dict with MessageSID on a temporary file
        with open('temp.json', 'w') as fp:
            json.dump({"address": geo_location_dict}, fp)
        return as_twilio_response(location_message)

    if 'cases' in incoming_msg:
        with open('temp.json') as json_data:
            geo_location_dict = json.load(json_data).get("address", {})
            print(geo_location_dict)
        district = geo_location_dict.get('state_district', '')  # district is not lowercase
        state = geo_location_dict.get('state', '')  # state is not lowercase
        district = district.replace(district, constants.districts.get(district, district))
        district_data = get_district_data(states_with_district_list, district, state)
        district_data_message = get_district_data_message(district_data)
        extra = f'''
\nType *Distance* to get the distance from the closest detected active case in your State from your location.
Type *Services* to see the essential services available in your region.
'''
        return as_twilio_response(district_data_message+extra)

    if 'services' in incoming_msg:
        # TODO: Get services from district or PAN State (All Districts) or PAN India
        # some cities are named differently in the resources.json API, eg Delhi
        # if a city is not found, set district city as the city in resources.json
        # if district city not found in resources.json, get nearest city from resources.json in the state
        # after getting a city show categories which includes pan country and pan state as category too?
        # PAN India is a state and PAN State is a city as filter in resources.json
        # if a city/district is not found as a city in resources.json, the city will be set as PAN State
        # if a state is not found in resources.json the state will be as PAN state
        with open('temp.json') as json_data:
            geo_location_dict = json.load(json_data).get("address", {})
            print(geo_location_dict)

        services_api = 'https://api.covid19india.org/resources/resources.json'
        services_list = get_response(services_api).get('resources', [])

        state = geo_location_dict.get('state', '')
        state_in_resources = state.replace(state, constants.states_from_resources.get(state, state))
        services_list_by_state = get_essential_services(services_list, "state", state_in_resources)
        # if services_list_by_state is [], it means state not found in resources.json. Use state="PAN India" in that case
        # pan india also has city as pan state, so no need to filter by city again

        city = geo_location_dict.get('city', '')
        if not city:  # city is not found in geo_location_dict, eg location is a village
            city = geo_location_dict.get('state_district', '')
        city_in_resources = city.replace(city, constants.districts.get(city, city))
        if services_list_by_state:  # non empty
            cities_in_state_in_resources = [each['city'] for each in services_list_by_state]
            if city_in_resources in cities_in_state_in_resources:
                services_list_by_city = get_essential_services(services_list_by_state, "city", city_in_resources)
                services_dict_by_category = get_services_by_category(services_list_by_city)
                services_keys = [each for each in services_dict_by_category.keys()]
                context = {
                    "services": services_dict_by_category,
                    "keys": services_keys,
                    "location": city_in_resources
                }
                with open('temp.json', 'w') as fp:
                    json.dump({"address": geo_location_dict, "context": context}, fp)
                services_menu = get_services_menu(services_keys, city_in_resources)
                return as_twilio_response(services_menu)
            elif "PAN State" in cities_in_state_in_resources:
                # city not found in essential services list for the given state use PAN state
                services_list_by_city = get_essential_services(services_list_by_state, "city", "PAN State")
                services_dict_by_category = get_services_by_category(services_list_by_city)
                services_keys = [each for each in services_dict_by_category.keys()]
                context = {
                    "services": services_dict_by_category,
                    "keys": services_keys,
                    "location": "PAN State"
                }
                with open('temp.json', 'w') as fp:
                    json.dump({"address": geo_location_dict, "context": context}, fp)
                services_menu = get_services_menu(services_keys, "PAN State")
                services_menu = "Sorry, we don't have any information about essential services in your location.\n" + services_menu
                return as_twilio_response(services_menu)
            elif "All Districts" in cities_in_state_in_resources:
                # city not found in essential services list for the given state use PAN state
                services_list_by_city = get_essential_services(services_list_by_state, "city", "All Districts")
                services_dict_by_category = get_services_by_category(services_list_by_city)
                services_keys = [each for each in services_dict_by_category.keys()]
                context = {
                    "services": services_dict_by_category,
                    "keys": services_keys,
                    "location": "All Districts"
                }
                with open('temp.json', 'w') as fp:
                    json.dump({"address": geo_location_dict, "context": context}, fp)
                services_menu = get_services_menu(services_keys, "All Districts")
                services_menu = "Sorry, we don't have any information about essential services in your location.\n" + services_menu
                return as_twilio_response(services_menu)
            else:  # if No PAN state service in state, show PAN India
                services_list_by_state = get_essential_services(services_list, "state", "PAN India")
                services_list_by_city = get_essential_services(services_list_by_state, "city", "PAN State")
                services_dict_by_category = get_services_by_category(
                    services_list_by_city)  # get services as a dictionary
                # with key as service and value as a list of services with that key
                services_keys = [each for each in services_dict_by_category.keys()]
                context = {
                    "services": services_dict_by_category,
                    "keys": services_keys,
                    "location": "PAN India",
                }
                with open('temp.json', 'w') as fp:
                    json.dump({"address": geo_location_dict, "context": context}, fp)
                services_menu = get_services_menu(services_keys, "PAN India")
                services_menu = "Sorry, we don't have any information about essential services in your location.\n" + services_menu
                return as_twilio_response(services_menu)

        else:  # if services_list_by_state is empty, meaning state isn't in resources, hence choose PAN India resources
            services_list_by_state = get_essential_services(services_list, "state", "PAN India")
            services_list_by_city = get_essential_services(services_list_by_state, "city", "PAN State")
            services_dict_by_category = get_services_by_category(services_list_by_city)  # get services as a dictionary
            # with key as service and value as a list of services with that key
            services_keys = [each for each in services_dict_by_category.keys()]
            context = {
                "services": services_dict_by_category,
                "keys": services_keys,
                "location": "PAN India",
            }
            with open('temp.json', 'w') as fp:
                json.dump({"address": geo_location_dict, "context": context}, fp)
            services_menu = get_services_menu(services_keys, "PAN India")
            services_menu = "Sorry, we don't have any information about essential services in your State.\n" + services_menu
            return as_twilio_response(services_menu)

    if incoming_msg in constants.numeric_inputs:  # possible range of values for essential service options
        with open('temp.json') as json_data:
            geo_location_dict = json.load(json_data).get("address", {})
            print(geo_location_dict)
        with open('temp.json') as json_data:
            context = json.load(json_data).get("context", {})
            print(context)
        # TODO: Handle keys index issue.
        # If key is outside the keys range of services, show exception message
        key = context["keys"][int(incoming_msg)-1]
        services_list = context["services"][key]
        services_message = get_services_message(services_list, key, context["location"])
        return as_twilio_response(services_message)

    return as_twilio_response(fallback_message)


def get_response(url):
    response = requests.get(url)
    return response.json()


def get_statewise_data_message(state, data):
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
*Total cases:*
Active: *{active}*
Confirmed: *{confirmed}*
Recovered: *{recovered}*
Deceased: *{deaths}*
*New cases:*
Confirmed: *{delta_confirmed}*
Recovered: *{delta_recovered}*
Deceased: *{delta_deaths}*

Last Updated: *{last_updated_timestamp}*

View more: https://www.covid19india.org/
'''
    return data_message


def get_geocode(city):
    location = geolocator.geocode(city)
    coordinates_tuple = (location.latitude, location.longitude)
    return coordinates_tuple


def get_reverse_geocode(coordinates):
    location = geolocator.reverse(coordinates, exactly_one=True)
    address_dict = location.raw['address']
    print(address_dict)
    return address_dict


def get_nearest_city_from_geo_location_in_resources(services_list_by_state, state, city):
    cities = [each["city"] for each in services_list_by_state]
    nearest_city = get_nearest_city(cities, city)
    return nearest_city


def get_nearest_city(cities, city):
    pass


def get_location_message(geo_location_dict):
    village = geo_location_dict.get('village', '')
    city = geo_location_dict.get('city', '')
    district = geo_location_dict.get('state_district', '')
    state = geo_location_dict.get('state', '')
    if city:
        address = ', '.join([city, district, state])
    elif village:
        address = ', '.join([village, district, state])
    else:
        address = ', '.join([district, state])
    location_message = f'''
Your detected location is {address}.
-Type *Cases* to get the lastest cases in your current District.
-Type *Services* to see the essential services available in your region.
'''
    return location_message


def get_district_data(states_with_district_list, district, state):
    for each in states_with_district_list:
        if state == each['state']:  # state is not lowercase
            for district_data in each['districtData']:
                if district == district_data['district']:  # district is not lowercase
                    return district_data


def get_district_data_message(data):
    active = data.get('active')
    confirmed = data.get('confirmed')
    recovered = data.get('recovered')
    deceased = data.get('deceased')
    delta_confirmed = data.get('delta').get('confirmed')
    delta_deceased = data.get('delta').get('deceased')
    delta_recovered = data.get('delta').get('recovered')

    data_message = f'''
*Latest Covid-19 data from {data.get('district')} (District)*
*Total cases:*
Active: *{active}*
Confirmed: *{confirmed}*
Recovered: *{recovered}*
Deceased: *{deceased}*
*New cases:*
Confirmed: *{delta_confirmed}*
Recovered: *{delta_recovered}*
Deceased: *{delta_deceased}*
'''
# Type *Services* to see the essential services available in your region.
    return data_message


def get_closest_active_case(*args):
    # get district from city name
    pass


def get_services_by_category(services_list):
    services_dict = {}
    for service in services_list:
        key = service["category"]
        services = []
        services = [each for each in services_list if each["category"] == key]
        services_dict[key] = services
    return services_dict


def get_services_menu(services_keys, location):
    services_menu = '\n'.join([str(services_keys.index(each)+1)+". "+each for each in services_keys])
    services_menu = f'''
*Essential Services available in {location}*:
Reply with the number corresponding to each service to see available services in that category: 
{services_menu}
'''
    return services_menu


def get_services_message(services_list, key, location):
    services = []
    for service in services_list:
        phone_numbers = service["phonenumber"].split(',\n')
        # each service is a dict, and we need to extract their values
        services.append('*'+service["nameoftheorganisation"]+'*'+'\nContact: '+'*'+service["contact"]+'*'+"\nPhone: "+'*'+', '.join(phone_numbers)+'*')
    services_message = '\n'.join(str(services.index(each)+1)+". "+each for each in services)
    services_message = f'''
Essential Services in the category *{key}* available in *{location}*: 
{services_message}

Reply with another number to view the corresponding services.
Type *Services* to view the Services Menu again.

Visit https://www.covid19india.org/essentials for more.
'''
    print(services_message)
    return services_message


def get_essential_services(services_list, key, value):
    # if service_list is complete, key is "state" and value is state. return is statewise services list
    # if services_list is statewise, key is "city" and value is city name. return is citywise services list
    filtered_services_list = [each for each in services_list if each[key] == value]
    return filtered_services_list
####


if __name__ == '__main__':
    app.run()
