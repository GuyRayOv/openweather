
import streamlit as st
import requests
import datetime
import pytz
import json
import folium

GEO_BASE_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"
MY_API_KEY = "c4d9b7d003d31461abe0aec452e24151"

#================================================================================================
def webapi_call(url, params={}):
    response = requests.get(url, params=params)
    try: response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        return []
    return response.json()
#=================================================================================================
def get_weather_data_for(location):
    json1 = webapi_call(GEO_BASE_URL, params={"q": location, "appid": MY_API_KEY})
    if json1 == []:
        st.write(f"{my_location} cannt get web infomation")
        return json1

    json2 = webapi_call(WEATHER_BASE_URL, params={"lat":json1[0]["lat"], "lon":json1[0]["lon"], "appid": MY_API_KEY})
    if json2 == []: st.write(f"lat:{json1[0]["lat"]}, lon:{json1[0]["lon"]} cannt get web infomation")

    return json2

#================================================================================================
def get_local_datetime(utc_timestamp, loca_timezone):
    utc_dt = datetime.datetime.fromtimestamp(utc_timestamp, datetime.UTC).replace(tzinfo=pytz.utc)
    return utc_dt.astimezone(pytz.timezone(loca_timezone)).strftime("%A, %B %d, %Y, %I:%M %p")

#=================================================================================================
def get_json_from_file(filename):
    try: f=open(filename, 'r')
    except FileNotFoundError: st.write(f"{filename} cannt open")
    return json.load(f)

#=================================================================================================
def get_favorite_locations():
    return get_json_from_file('favorite_locations.json')

#=================================================================================================
def preset_weather_for_location(location):
    json = get_weather_data_for(location)
    st.write(f"Weather Conditions in {location}: {json['current']['weather'][0]['description']}, {int(json['current']['temp'] - 273.15)}C, {json['current']['humidity']}% humidity")
    st.write(f"{get_local_datetime(json['current']['dt'], json['timezone'])} (local time)\n")


st.title('Weather App')

for location in get_favorite_locations().keys(): preset_weather_for_location(location)

location = st.text_input('Enter a location name', '')
if location: preset_weather_for_location(location)

