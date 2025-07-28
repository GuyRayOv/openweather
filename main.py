
import streamlit as st
import requests

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
    if json2 == []:
        st.write(f"lat:{json1[0]["lat"]}, lon:{json1[0]["lon"]} cannt get web infomation")

    return json2

#================================================================================================

st.title('Weather App')

my_location = st.text_input('Enter a location name', '')

if my_location:
    json = get_weather_data_for(my_location)
    st.write(f"Current Weather Conditions in {my_location}: {json['current']['weather'][0]['description']}, {int(json['current']['temp']-273.15)}C, {json['current']['humidity']}% humidity")
