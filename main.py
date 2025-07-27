
import streamlit as st
import requests

"""
https://api.openweathermap.org/data/3.0/onecall?lat=32.0351&lon=34.5142&appid=c4d9b7d003d31461abe0aec452e24151
"""

#service
open_weatehr_base = "https://api.openweathermap.org/data/3.0/onecall"

#my parmas
my_api_key = "c4d9b7d003d31461abe0aec452e24151"

#applicatio params
my_lat = 32.0351 #41.878113 #
my_lon = 34.5142 # -87.629799

my_params = {"lat": {my_lat}, "lon": {my_lon}, "appid": {my_api_key}}

response = requests.get(open_weatehr_base, params=my_params)
try: response.raise_for_status()
except response.exceptions.HTTPError as e: print(e)

print(response.json())

