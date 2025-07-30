
import streamlit as st
import requests
import datetime
import pytz

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



st.title('Weather App')

location = st.text_input('Enter a location name', '')

if location:
    json = get_weather_data_for(location)
    st.write(f"Weather Conditions in {location}")
    st.write(f"{get_local_datetime(json['current']['dt'], json['timezone'])} (local time)")
    st.write(f"{json['current']['weather'][0]['description']}")
    st.write(f"{int(json['current']['temp']-273.15)}C")
    st.write(f"{json['current']['humidity']}% humidity")


