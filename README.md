# openweather

biuds20.python-project.openweather



🌦️ **Weather Dashboard – BIUDS20 Project**



This project was developed as part of the Practice Python module in the BIUDS20 course.

It is a Streamlit web application that presents current and historical weather data, along with interactive maps, for user-selected locations.



🔧 Features

Users can either:

* Enter a location manually via a text box, or
* Provide a list of favorite locations via a .json file.



For manual entries:

* The app displays both current and historical weather data.
* For locations in the JSON file, only current weather data is displayed (no historical data).
* Maps are displayed for all selected locations.



📁 **JSON Schema Example**

{

&nbsp; "\_note": "Temperature units per location. F = Fahrenheit, C = Celsius",



&nbsp; "Chandler": "F",

&nbsp; "Sydney": "C",

&nbsp; "Beit Nir": "C",



&nbsp; "\_comment": "KEEP THIS LINE LAST"

}

This project includes a favorite\_locations.json file with preferred temperature units per location.



💬 **Reflection**

Overall, I enjoyed building this application. It was my first time using AI chat tools to debug and fine-tune code, which was both helpful and an exciting new experience.

The project took me several tens of hours to complete, and it helped deepen my understanding of API integration, JSON handling, and web app deployment using Streamlit.



