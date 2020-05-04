districts = {'Pune District': 'Pune',
             'Hugli': 'Hooghly'}

# states = {'India': 'Total'}

city_from_resources = {}

states_from_resources = {'Andaman and Nicobar Islands': 'Andaman & Nicobar',
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