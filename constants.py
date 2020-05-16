# stores common constant values in one place

country_common_names = {
    "us": "usa",
    "usa": "usa",
    "united states": "usa",
    "united states of america": "usa",
    "uk": "uk",
    "united kingdom": "uk",
    "britain": "uk",
    "great britain": "uk",
    "england": "uk",
    "uae": "uae",
    "united arab emirates": "uae",
    "guinea-bissau": "guinea-bissau",
    "guinea bissau": "guinea-bissau",
    "timor-leste": "timor-leste",
    "timor leste": "timor-leste",
    "s. korea": "s. korea",
    "s.korea": "s. korea",
    "south korea": "s. korea"
}  # a map of common names of countries that users can send in their message

districts = {
    'Pune District': 'Pune',
    'Hugli': 'Hooghly'
}

# city_from_resources = {}

states_from_resources = {
    'Andaman and Nicobar Islands': 'Andaman & Nicobar',
    'Jammu and Kashmir': 'Jammu & Kashmir'
}

numeric_inputs = [str(each) for each in range(1, 17)]

greeting_tokens = ['hi', 'hello', 'hey']

# Default messages
welcome_message = f'''
Hi there! I am a bot that gives you the latest information on Covid-19 from India.
-Type *India* to get the latest country-wide Covid-19 stats.
-Type the exact name of a state to get it's latest Covid-19 stats.
-Send your location to get the latest stats from your district along with essential services available in your region.
-Type *Help* anytime to to learn how to interact with me.
'''

help_message = f'''
Say *Hi* to begin an interaction with me anytime.
-Type *India* to get the latest country-wide Covid-19 stats.
-Type the exact name of a state to get it's latest Covid-19 stats.
-Send your location to get the latest stats from your district along with essential services available in your region.
'''

fallback_message = 'Sorry, I did not quite get that. Type *help* to learn how to interact with me.'