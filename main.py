
import streamlit as st
import requests
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import pytz
import json
import folium
from streamlit_folium import st_folium


#================================================================================================
GEO_BASE_URL = "http://api.openweathermap.org/geo/1.0/direct"
CURRENT_WEATHER_BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"
HISTORICAL_WEATHER_BASE_URL = CURRENT_WEATHER_BASE_URL + "/timemachine"
WEATHER_ICON_BASE_URL = "http://openweathermap.org/img/wn/"
MY_API_KEY = "c4d9b7d003d31461abe0aec452e24151"
FAVORITE_LOCATIONS_FILE = "favorite_locations.json"
CELSIUS = "C"

#================================================================================================
def webapi_call(url, params={}):
    response = requests.get(url, params=params)
    try: response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        return {}
    return response.json()

#=================================================================================================
def get_curent_weather_data_for(lat, lon):
    json = webapi_call(CURRENT_WEATHER_BASE_URL, params={"lat":lat, "lon":lon, "appid":MY_API_KEY})
    if json == {}: st.write(f"lat:{lat}, lon:{lon} cannt get web infomation")

    return json

#==================================================================================================
def convert_kelvin_to_local(kelvin, local_units=CELSIUS):
    return int(kelvin - 273.15) if local_units == CELSIUS else int((kelvin * 1.8) - 459.67)

#==================================================================================================
def get_historical_weather_data_for(lat, lon, years_back):

    # Get current UTC time
    now_utc = datetime.now(timezone.utc)

    # One year ago
    last_year_utc = now_utc - relativedelta(years=years_back)

    # Timestamp
    timestamp_last_year = int(last_year_utc.timestamp())

    return webapi_call(HISTORICAL_WEATHER_BASE_URL, params={"lat":lat, "lon":lon, "dt":timestamp_last_year, "appid": MY_API_KEY})

#=================================================================================================
def get_weather_data_for(location, local_units=CELSIUS, historical=False):

    json1 = webapi_call(GEO_BASE_URL, params={"q": location, "appid": MY_API_KEY})
    if json1 == {}:
        st.write(f"{my_location} cannt get web infomation")
        return {}

    current_weather_data = get_curent_weather_data_for(json1[0]["lat"], json1[0]["lon"])

    historical_weather_data = {}

    if historical:
        current_year = 2025
        historical_weather_data[current_year] = convert_kelvin_to_local(current_weather_data['current']['temp'], local_units)

        for years_back in range(1,20+1):
            json2 = get_historical_weather_data_for(json1[0]["lat"], json1[0]["lon"], years_back)
            historical_weather_data[current_year-years_back] = convert_kelvin_to_local(json2['data'][0]['temp'], local_units)

    return current_weather_data, historical_weather_data

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
    local_temp = convert_kelvin_to_local(location_data['current']['temp'], local_units)

    # local weather
    st.write(f"{location_data['current']['weather'][0]['description']},  {int(local_temp)}{local_units},  {location_data['current']['humidity']}% humidity")

    # local-weather icon
    st.image(WEATHER_ICON_BASE_URL + location_data['current']['weather'][0]['icon'] + "@2x.png")

#=================================================================================================
def show_weather_for(location, local_units=CELSIUS, historical=False):
    location_data, historical_data = get_weather_data_for(location, local_units, historical)
    show_weather_data_for(location, local_units, location_data)
    show_map_for(location_data)
    if historical: st.write(historical_data)

#================================================================================================
def get_local_datetime(utc_timestamp, local_timezone):
    utc_dt = datetime.fromtimestamp(utc_timestamp, timezone.utc)

    #utc_dt = datetime.datetime.fromtimestamp(utc_timestamp, datetime.UTC).replace(tzinfo=pytz.utc)
    return utc_dt.astimezone(pytz.timezone(local_timezone)).strftime("%A, %B %d, %Y, %I:%M %p")

#=================================================================================================
def get_favorite_locations():

    parsed_json = {}

    uploaded_file = st.file_uploader("Upload a favorite locations JSON file", type=["json"])
    if uploaded_file is None: return parsed_json

    json_data = uploaded_file.read()

    try: parsed_json = json.loads(json_data)
    except json.JSONDecodeError: st.error("Error: Invalid JSON format. Please upload a valid JSON file.")

    return parsed_json

#=================================================================================================
def select_from_favorite_locations():

    favorite_locations = get_favorite_locations()

    if favorite_locations == {}: return favorite_locations

    # Create the multiselect widget
    selected_locations = st.multiselect(
        label="Select your preferred locations:",
        options=[location for location in favorite_locations.keys()]
    )

    return { location: favorite_locations[location] for location in selected_locations }

#================================================================================================
def show_weather_for_favorite_locaitons(historical=False):
    for location, units in select_from_favorite_locations().items():
        show_weather_for(location, units, historical)

#=================================================================================================

st.title(""" Weather App """)

if st.checkbox('Show favorite locations'):
    show_weather_for_favorite_locaitons(historical=False)

location = st.text_input('Enter a location name', '')
if location:
    if st.checkbox(f"Show historical temperatures for {location} at this day/hour"):
        show_weather_for(location, historical=True)
    else:
        show_weather_for(location, historical=False)

