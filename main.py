
import streamlit as st
import requests
import datetime
import pytz
import json
import folium
from streamlit_folium import st_folium

#================================================================================================
GEO_BASE_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"
WEATHER_ICON_BASE_URL = "http://openweathermap.org/img/wn/"
MY_API_KEY = "c4d9b7d003d31461abe0aec452e24151"
FAVORITE_LOCATIONS_FILE = 'favorite_locations.json'
DEFAULT_LOCAL_UNITS = "C"

#================================================================================================
def webapi_call(url, params={}):
    response = requests.get(url, params=params)
    try: response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        return {}
    return response.json()

#=================================================================================================
def get_weather_data_for(location):
    json1 = webapi_call(GEO_BASE_URL, params={"q": location, "appid": MY_API_KEY})

    if json1 == {}: st.write(f"{my_location} cannt get web infomation")
    else: json2 = webapi_call(WEATHER_BASE_URL, params={"lat":json1[0]["lat"], "lon":json1[0]["lon"], "appid": MY_API_KEY})

    if json2 == {}: st.write(f"lat:{json1[0]["lat"]}, lon:{json1[0]["lon"]} cannt get web infomation")
    return json2

#================================================================================================
def show_map_for(this_location):
    # Create a Folium map around the location
    m = folium.Map(location=[this_location['lat'], this_location['lon']], zoom_start=13)

    # Add a marker at the location
    folium.Marker(location=[this_location['lat'], this_location['lon']], popup="This is a marker", tooltip="Click me").add_to(m)

    # Display the map in Streamlit and get user interaction data
    output = st_folium(m, width=700, height=500)

#=================================================================================================
def show_weather_data_for(location, local_units, location_data):

    # location
    st.write(f"Weather Conditions in {location}")

    # local time
    st.write(f"Local time: {get_local_datetime(location_data['current']['dt'], location_data['timezone'])}")

    # local temprature
    if local_units == "C": local_temp = location_data['current']['temp'] - 273.15
    else: local_temp = (location_data['current']['temp'] * 1.8) - 459.67

    # local weather
    st.write(f"{location_data['current']['weather'][0]['description']},  {int(local_temp)}{local_units},  {location_data['current']['humidity']}% humidity")

    # local-weather icon
    st.image(WEATHER_ICON_BASE_URL + location_data['current']['weather'][0]['icon'] + "@2x.png")

#=================================================================================================
def show_weather_for(location, local_units):
    location_data = get_weather_data_for(location)
    show_weather_data_for(location, local_units, location_data)
    show_map_for(location_data)

#================================================================================================
def get_local_datetime(utc_timestamp, loca_timezone):
    utc_dt = datetime.datetime.fromtimestamp(utc_timestamp, datetime.UTC).replace(tzinfo=pytz.utc)
    return utc_dt.astimezone(pytz.timezone(loca_timezone)).strftime("%A, %B %d, %Y, %I:%M %p")

#=================================================================================================
def get_json_from_file(filename):
    json_data = {}
    try:
        f=open(filename, 'r')
    except FileNotFoundError:
        print(f"{filename} cannt open")
    else:
        try: json_data = json.load(f)
        except json.decoder.JSONDecodeError:
            print(f"{filename} cannt decode")

    return json_data

#=================================================================================================
def get_favorite_locations():

    uploaded_file = st.file_uploader("Upload a favorite locations JSON file", type=["json"])
    if uploaded_file is None: return {}

    json_data = uploaded_file.read()

    try: parsed_json = json.loads(json_data)
    except json.JSONDecodeError: st.error("Error: Invalid JSON format. Please upload a valid JSON file.")

    return parsed_json

#=================================================================================================
def select_from_favorite_locations():

    favorite_locations = get_favorite_locations()
    if favorite_locations == {}: return {}

    # Create the multiselect widget
    selected_locations = st.multiselect(
        label="Select your preferred locations:",
        options=[location for location in favorite_locations.keys()],
        default=[]  # Set default selected options
    )

    return { location: favorite_locations[location] for location in selected_locations }

#================================================================================================
def show_weather_for_favorite_locations():
    selected_locations = select_from_favorite_locations()

    for location, units in selected_locations.items():
        show_weather_for(location, units)

#=================================================================================================

st.title(""" Weather App """)

if st.checkbox('Show favorite locations'):
    show_weather_for_favorite_locations()

location = st.text_input('Enter a location name', '')
if location: show_weather_for(location, DEFAULT_LOCAL_UNITS)

