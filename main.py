"""
Weather App using Streamlit and OpenWeatherMap APIs.

This script fetches and displays current and historical weather data for a given
location. It also supports favorite locations loaded from a JSON file, and shows
interactive charts and maps using Plotly and Folium.
"""

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
import plotly.graph_objects as go
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
# API constants
GEO_BASE_URL = "http://api.openweathermap.org/geo/1.0/direct"
CURRENT_WEATHER_BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"
HISTORICAL_WEATHER_BASE_URL = CURRENT_WEATHER_BASE_URL + "/timemachine"
WEATHER_ICON_BASE_URL = "http://openweathermap.org/img/wn/"
MY_API_KEY = "c4d9b7d003d31461abe0aec452e24151"

# Units
CELSIUS = "C"

# ----------------------------------------------------------------------------------------------------------------------
def webapi_call(url, params=None):
    """
    Send a GET request to an API endpoint.

    Args:
        url (str): API endpoint URL.
        params (dict, optional): Query parameters for the request.

    Returns:
        dict: Parsed JSON response from the API, or an empty dictionary if an error occurs.
    """
    if params is None:
        params = {}

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

# ----------------------------------------------------------------------------------------------------------------------
def get_curent_weather_data_for(lat, lon):
    """
    Retrieve current weather data for a specific location.

    Args:
        lat (float): Latitude coordinate.
        lon (float): Longitude coordinate.

    Returns:
        dict: Current weather data in JSON format.
    """
    json_data = webapi_call(CURRENT_WEATHER_BASE_URL, params={"lat": lat, "lon": lon, "appid": MY_API_KEY})
    if json_data == {}:
        st.write(f"lat:{lat}, lon:{lon} cannot get web information")
    return json_data

# ----------------------------------------------------------------------------------------------------------------------
def convert_kelvin_to_local(kelvin, local_units=CELSIUS):
    """
    Convert temperature from Kelvin to Celsius or Fahrenheit.

    Args:
        kelvin (float): Temperature in Kelvin.
        local_units (str): Target unit. Either "C" for Celsius or "F" for Fahrenheit.

    Returns:
        int: Converted temperature as an integer.
    """
    return int(kelvin - 273.15) if local_units == CELSIUS else int((kelvin * 1.8) - 459.67)

# ----------------------------------------------------------------------------------------------------------------------
def get_historical_weather_data_for(lat, lon, years_back):
    """
    Retrieve historical weather data for a specific location and past year.

    Args:
        lat (float): Latitude coordinate.
        lon (float): Longitude coordinate.
        years_back (int): Number of years to look back.

    Returns:
        dict: Historical weather data in JSON format.
    """
    now_utc = datetime.now(timezone.utc)
    last_year_utc = now_utc - relativedelta(years=years_back)
    timestamp_last_year = int(last_year_utc.timestamp())
    return webapi_call(HISTORICAL_WEATHER_BASE_URL, params={
        "lat": lat, "lon": lon, "dt": timestamp_last_year, "appid": MY_API_KEY
    })

# ----------------------------------------------------------------------------------------------------------------------
def get_weather_data_for(location, local_units=CELSIUS, historical=False):
    """
    Retrieve current weather and optional historical weather data.

    Args:
        location (str): Location name (e.g., "London").
        local_units (str): Unit for temperature display ("C" or "F").
        historical (bool | int): Number of past years to retrieve, or False to skip.

    Returns:
        tuple:
            dict: Current weather data.
            dict: Historical weather data, mapping year -> temperature.
    """
    geo_data = webapi_call(GEO_BASE_URL, params={"q": location, "appid": MY_API_KEY})

    if not geo_data:
        st.write(f"{location} cannot get web information")
        return None, None

    lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
    current_weather_data = get_curent_weather_data_for(lat, lon)

    historical_weather_data = {}
    if historical:
        current_year = datetime.now().year
        historical_weather_data[current_year] = convert_kelvin_to_local(
            current_weather_data['current']['temp'], local_units
        )

        for years_back in range(1, historical + 1):
            hist_data = get_historical_weather_data_for(lat, lon, years_back)
            if 'data' in hist_data and hist_data['data']:
                historical_weather_data[current_year - years_back] = convert_kelvin_to_local(
                    hist_data['data'][0]['temp'], local_units
                )
            else:
                print(f"[Warning] No historical data for year {current_year - years_back}")
                return None, None

    return current_weather_data, historical_weather_data

# ----------------------------------------------------------------------------------------------------------------------
def show_map_for(this_location):
    """
    Display an interactive map with a marker for the given location.

    Args:
        this_location (dict): Dictionary containing 'lat' and 'lon' keys.
    """
    m = folium.Map(location=[this_location['lat'], this_location['lon']], zoom_start=13)
    folium.Marker(
        location=[this_location['lat'], this_location['lon']],
        popup="This is a marker", tooltip="Click me"
    ).add_to(m)
    st_folium(m, width=700, height=500)

# ----------------------------------------------------------------------------------------------------------------------
def show_temperature_trendline(historical_data):
    """
    Display a line chart of temperature trends over the years.

    Args:
        historical_data (dict): Mapping of year -> temperature.
    """
    data = pd.DataFrame({
        'Year': historical_data.keys(),
        'Temperature': historical_data.values()
    })
    fig = px.line(data, x='Year', y='Temperature', title="Historical Temperature Trend")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------------------------------------------------
def show_temperature_histogram(historical_data, local_units=CELSIUS, nbins=20, title=None, show_in_streamlit=True):
    """
    Display a histogram of temperature distribution.

    Args:
        historical_data (dict | list): Temperature values or mapping of date -> temperature.
        local_units (str): Unit of temperature ("C" or "F").
        nbins (int): Number of bins in the histogram.
        title (str, optional): Custom chart title.
        show_in_streamlit (bool): Whether to render in Streamlit.

    Returns:
        plotly.graph_objs.Figure: The generated histogram figure.
    """
    temps = [float(v) for v in historical_data.values()] if isinstance(historical_data, dict) else list(map(float, historical_data))
    if not temps:
        raise ValueError("No temperature data available for histogram.")

    hover = f"Temp (bin center): %{{x:.2f}}°{local_units}<br>Count: %{{y}}"

    fig = go.Figure(data=go.Histogram(
        x=temps, nbinsx=nbins, hovertemplate=hover, marker_line_width=0.5, opacity=0.9
    ))
    fig.update_layout(
        title=title or f"Temperature distribution ({len(temps)} samples)",
        xaxis_title=f"Temperature (°{local_units})",
        yaxis_title="Count",
        bargap=0.1,
        template="simple_white",
    )

    if show_in_streamlit:
        try:
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

    return fig

# ----------------------------------------------------------------------------------------------------------------------
def show_weather_for(location, local_units=CELSIUS, historical=False):
    """
    Display weather information for a location, including optional historical charts.

    Args:
        location (str): Location name.
        local_units (str): Unit for temperature ("C" or "F").
        historical (bool | int): Number of past years to include, or False.
    """
    location_data, historical_data = get_weather_data_for(location, local_units, historical)
    if not location_data:
        st.error("No weather data for this location.")
        return

    st.write(f"Weather Conditions in {location}:")
    st.write(f"Local time: {get_local_datetime(location_data['current']['dt'], location_data['timezone'])}")

    local_temp = convert_kelvin_to_local(location_data['current']['temp'], local_units)
    st.write(
        f"{location_data['current']['weather'][0]['description']}, "
        f"{int(local_temp)}°{local_units}, "
        f"{location_data['current']['humidity']}% humidity"
    )
    st.image(WEATHER_ICON_BASE_URL + location_data['current']['weather'][0]['icon'] + "@2x.png")

    if historical:
        show_temperature_trendline(historical_data)
        show_temperature_histogram(historical_data, local_units, nbins=20)

    show_map_for(location_data)

# ----------------------------------------------------------------------------------------------------------------------
def get_local_datetime(utc_timestamp, local_timezone):
    """
    Convert a UTC timestamp to a local time string.

    Args:
        utc_timestamp (int): UTC timestamp.
        local_timezone (str): Timezone string (e.g., "Europe/London").

    Returns:
        str: Localized formatted date and time string.
    """
    utc_dt = datetime.fromtimestamp(utc_timestamp, timezone.utc)
    return utc_dt.astimezone(pytz.timezone(local_timezone)).strftime("%A, %B %d, %Y, %I:%M %p")

# ----------------------------------------------------------------------------------------------------------------------
def get_favorite_locations():
    """
    Prompt the user to upload a JSON file of favorite locations.

    Returns:
        dict: Parsed favorite locations with keys as location names and values as units.
    """
    parsed_json = {}
    uploaded_file = st.file_uploader("Upload a favorite locations JSON file", type=["json"])
    if uploaded_file is None:
        return parsed_json

    try:
        parsed_json = json.loads(uploaded_file.read())
        parsed_json.pop('_comment', None)
        parsed_json.pop('_note', None)
    except json.JSONDecodeError:
        st.error("Error: Invalid JSON format.")

    return parsed_json

# ----------------------------------------------------------------------------------------------------------------------
def select_from_favorite_locations():
    """
    Display a multi-select widget for favorite locations.

    Returns:
        dict: Selected locations and their units.
    """
    favorite_locations = get_favorite_locations()
    if not favorite_locations:
        return {}

    selected_locations = st.multiselect(
        label="Select your preferred locations:",
        options=list(favorite_locations.keys())
    )
    return {loc: favorite_locations[loc] for loc in selected_locations}

# ----------------------------------------------------------------------------------------------------------------------
def show_weather_for_favorite_locaitons(historical=False):
    """
    Display weather information for all selected favorite locations.

    Args:
        historical (bool | int): Number of past years to include, or False.
    """
    for location, units in select_from_favorite_locations().items():
        show_weather_for(location, units, historical)

# ----------------------------------------------------------------------------------------------------------------------
# Streamlit UI
st.title("Weather App")

if st.checkbox('Show favorite locations'):
    show_weather_for_favorite_locaitons(historical=False)

location = st.text_input('Enter a location name', '')
if location:
    years_back = st.slider(
        f"Show temperatures of past years in {location} at current Day:Hour",
        min_value=0, max_value=45, value=0
    )
    show_weather_for(location, historical=years_back)
