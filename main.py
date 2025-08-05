
import streamlit as st
import requests
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import pytz
import json
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


#=======================================================================================================================
GEO_BASE_URL = "http://api.openweathermap.org/geo/1.0/direct"
CURRENT_WEATHER_BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"
HISTORICAL_WEATHER_BASE_URL = CURRENT_WEATHER_BASE_URL+"/timemachine"
WEATHER_ICON_BASE_URL = f"http://openweathermap.org/img/wn/"
MY_API_KEY = "c4d9b7d003d31461abe0aec452e24151"
CELSIUS = "C"

#=======================================================================================================================
def webapi_call(url, params={}):
    """Send a GET request to a given URL with parameters.

    Args:
        url (str): API endpoint URL.
        params (dict): Query parameters for the request.

    Returns:
        dict: Parsed JSON response or an empty dictionary if an error occurs.
    """
    try:
        response = requests.get(url, params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e} - URL: {response.url}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"Request timed out: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Unexpected error: {e}")
    return {}

#=======================================================================================================================
def get_curent_weather_data_for(lat, lon):
    """Retrieve current weather data for a specific location.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.

    Returns:
        dict: Current weather data.
    """
    json = webapi_call(CURRENT_WEATHER_BASE_URL, params={"lat": lat, "lon": lon, "appid": MY_API_KEY})
    if json == {}: st.write(f"lat:{lat}, lon:{lon} cannot get web information")
    return json

#=======================================================================================================================
def convert_kelvin_to_local(kelvin, local_units=CELSIUS):
    """Convert temperature from Kelvin to Celsius or Fahrenheit.

    Args:
        kelvin (float): Temperature in Kelvin.
        local_units (str): Target unit (C or F).

    Returns:
        int: Converted temperature.
    """
    return int(kelvin - 273.15) if local_units == CELSIUS else int((kelvin * 1.8) - 459.67)

#=======================================================================================================================
def get_historical_weather_data_for(lat, lon, years_back):
    """Retrieve historical weather data for a past year.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.
        years_back (int): Number of years to look back.

    Returns:
        dict: Historical weather data.
    """
    now_utc = datetime.now(timezone.utc)
    last_year_utc = now_utc - relativedelta(years=years_back)
    timestamp_last_year = int(last_year_utc.timestamp())
    return webapi_call(HISTORICAL_WEATHER_BASE_URL, params={"lat": lat, "lon": lon, "dt": timestamp_last_year, "appid": MY_API_KEY})

#=======================================================================================================================
def get_weather_data_for(location, local_units=CELSIUS, historical=False):
    """Retrieve current and optional historical weather data.

    Args:
        location (str): Name of the location.
        local_units (str): Unit for temperature display.
        historical (bool or int): Whether to include historical data.

    Returns:
        tuple: (current weather data, historical weather dictionary)
    """
    json1 = webapi_call(GEO_BASE_URL, params={"q": location, "appid": MY_API_KEY})
    if json1 == {}:
        st.write(f"{location} cannot get web information")
        return {}

    lat, lon = json1[0]["lat"], json1[0]["lon"]
    current_weather_data = get_curent_weather_data_for(lat, lon)

    historical_weather_data = {}
    if historical:

        current_year = 2025

        historical_weather_data[current_year] = (
            convert_kelvin_to_local(current_weather_data['current']['temp'], local_units))

        for years_back in range(1, historical + 1):
            json2 = get_historical_weather_data_for(lat, lon, years_back)

            if 'data' in json2 and json2['data']:
                historical_weather_data[current_year - years_back] = (
                    convert_kelvin_to_local(json2['data'][0]['temp'], local_units))
            else:
                print(f"[Warning] No historical data found for year {current_year - years_back}: {json2}")
                break

    return current_weather_data, historical_weather_data

#=======================================================================================================================
def show_map_for(this_location):
    """Display a map with a marker for the given location.

    Args:
        this_location (dict): Dictionary with 'lat' and 'lon' keys.
    """
    m = folium.Map(location=[this_location['lat'], this_location['lon']], zoom_start=13)
    folium.Marker(location=[this_location['lat'], this_location['lon']],
                  popup="This is a marker", tooltip="Click me").add_to(m)
    st_folium(m, width=700, height=500)

#======================================================================================================================
def show_weather_for(location, local_units=CELSIUS, historical=False):
    """Display full weather view including chart and map.

    Args:
        location (str): Location name.
        local_units (str): Temperature unit.
        historical (bool or int): Include historical data.
    """
    location_data, historical_data = get_weather_data_for(location, local_units, historical)

    st.write(f"Weather Conditions in {location}: ")
    st.write(f"Local time: {get_local_datetime(location_data['current']['dt'], location_data['timezone'])}")

    local_temp = convert_kelvin_to_local(location_data['current']['temp'], local_units)
    st.write(
        f"{location_data['current']['weather'][0]['description']},  "
        f"{int(local_temp)}°{local_units},  "
        f"{location_data['current']['humidity']}% humidity"
    )
    st.image(WEATHER_ICON_BASE_URL + location_data['current']['weather'][0]['icon'] + "@2x.png")

    #Create line plot
    if historical:
        data = pd.DataFrame({
            'Year': historical_data.keys(),
            'temperature': historical_data.values()
        })
        fig = px.line(data, x='Year', y='temperature', title=f"Historical data for {location}, this date/hour")
        st.plotly_chart(fig, use_container_width=True)

        fig, ax = plt.subplots()
        ax.hist(x=list(historical_data.values()), bins=20)
        ax.set_title("Distribution of historical Temperatures at this Date:Hour")
        ax.set_xlabel(f"Temperature (°{local_units})")
        ax.set_ylabel("Number of Days")
        st.plotly_chart(fig)

    show_map_for(location_data)

#=======================================================================================================================
def get_local_datetime(utc_timestamp, local_timezone):
    """Convert UTC timestamp to local time string.

    Args:
        utc_timestamp (int): UTC timestamp.
        local_timezone (str): Timezone string.

    Returns:
        str: Localized formatted date string.
    """
    utc_dt = datetime.fromtimestamp(utc_timestamp, timezone.utc)
    return utc_dt.astimezone(pytz.timezone(local_timezone)).strftime("%A, %B %d, %Y, %I:%M %p")

#=======================================================================================================================
def get_favorite_locations():
    """Prompt user to upload a favorite locations JSON file.

    Returns:
        dict: Parsed favorite locations.
    """
    parsed_json = {}
    uploaded_file = st.file_uploader("Upload a favorite locations JSON file", type=["json"])
    if uploaded_file is None: return parsed_json

    json_data = uploaded_file.read()
    try:
        parsed_json = json.loads(json_data)
        parsed_json.pop('_comment', None)
        parsed_json.pop('_note', None)

    except json.JSONDecodeError:
        st.error("Error: Invalid JSON format. Please upload a valid JSON file.")

    return parsed_json

#=======================================================================================================================
def select_from_favorite_locations():
    """Display a multiselect of uploaded favorite locations.

    Returns:
        dict: Selected favorite locations.
    """
    favorite_locations = get_favorite_locations()
    if favorite_locations == {}: return favorite_locations

    selected_locations = st.multiselect(
        label="Select your preferred locations:",
        options=[location for location in favorite_locations.keys()]
    )
    return { location:favorite_locations[location] for location in selected_locations }

#=======================================================================================================================
def show_weather_for_favorite_locaitons(historical=False):
    """Display weather info for selected favorite locations.

    Args:
        historical (bool or int): Include historical weather data.
    """
    for location, units in select_from_favorite_locations().items():
        show_weather_for(location, units, historical)

# ------------------------------------------------ Streamlit UI --------------------------------------------------------
st.title(""" Weather App """)

if st.checkbox('Show favorite locations'):
    show_weather_for_favorite_locaitons(historical=False)

location = st.text_input('Enter a location name', '')
if location:
    years_back = st.slider(f"Show temperatures of past years in {location} at current Day:Hour", min_value=0, max_value=25, value=0)
    show_weather_for(location, historical=years_back)
