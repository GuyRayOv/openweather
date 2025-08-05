# 🌦️ Weather Dashboard – BIUDS20 Project


This project was developed as part of the Practice Python module in the BIUDS20 course.
---

##### It is a Streamlit web application that retrieves current and historical weather data from the OpenWeatherMap API, and displays it alongside interactive maps.

# 

# 🔧 Features

##### Two ways to select locations:

##### 

##### Manual entry – Type a location name in the text box.

##### 

##### Displays current and historical weather data.

##### 

##### Favorite locations file – Upload a .json file of preferred locations.

##### 

##### Displays current weather data only (no historical data).

##### 

##### Visual presentation:

##### 

##### Temperature trendline (year-by-year comparison) 📈

##### 

##### Temperature distribution histogram 📊

##### 

##### Interactive map for each location 🗺️

##### 

# 📁 JSON Schema Example

##### {

##### &nbsp; "\_note": "Temperature units per location. F = Fahrenheit, C = Celsius",

##### 

##### &nbsp; "Chandler": "F",

##### &nbsp; "Sydney": "C",

##### &nbsp; "Beit Nir": "C",

##### 

##### &nbsp; "\_comment": "KEEP THIS LINE LAST"

##### }

##### A sample favorite\_locations.json is included with preferred temperature units per location.

# 

# 🛠️ Technology Stack

# Python 3.x

# 

##### Streamlit – Web app UI

##### Requests – API calls

##### Folium + streamlit-folium – Interactive maps

##### Plotly – Data visualizations

##### Pandas – Data manipulation

# 

# 💬 Reflection

##### This was my first full Python web app project and my first time using AI chat tools to debug and fine-tune my code.

##### The experience was surprisingly effective — though two of the three visualization-functions *show\_temperature\_histogram* and *show\_temperature\_trendline* were adapted from various chat-generated versions until I found ones that didn’t crash, all other functions were handwritten.

##### 

##### Performance? Let’s just say… it’s not winning any speed records. I need to learn Python profiling and optimizations in the future. 🐢

##### 

##### The project took me around 200 hours to complete. It deepened my understanding of API integration, JSON handling, Data visualization, and Deploying interactive web apps with Streamlit

##### 

##### Overall, it was a challenging but rewarding process — and it definitely leveled up my Python skills.

