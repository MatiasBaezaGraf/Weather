from flask import Flask, render_template, request
from markupsafe import escape
from pprint import pprint
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
now = datetime.now().strftime("%H %M %S")


@app.route('/')
def index():
    return render_template('city-form.html')


@app.route('/results', methods=['POST'])
def results():
    title = 'Results'
    text = request.form['city']
    nomenclature = request.form['degrees']
    processed_text = text.title()

    api_key = "a3c6982a608e2a1b1959640042e4dd25"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = processed_text

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name

    response = requests.get(complete_url)

    data = response.json()

    if not city_name:
        return render_template('not-found.html', title=title, )
    elif data["cod"] != "404":
        y = data["main"]

        #To get the actual time of the searched location
        timezone_minutes = data["timezone"] / 60
        delta_sum = timedelta(minutes=timezone_minutes)
        utc_time = datetime.utcnow()
        actual_raw_time = (utc_time + delta_sum)
        actual_time = actual_raw_time.strftime("%H:%M")

        #To get the sunrise an sunset formatted times for the searchad location
        raw_sunrise = (datetime.utcfromtimestamp(data["sys"]["sunrise"]) + (delta_sum))
        sunrise = raw_sunrise.strftime("%H:%M")
        raw_sunset = (datetime.utcfromtimestamp(data["sys"]["sunset"]) + (delta_sum))
        sunset = raw_sunset.strftime("%H:%M")

        #Get times in float to compare them and get the corresponding icon
        actual_hour = int(actual_raw_time.strftime("%H"))
        actual_minute = int(actual_raw_time.strftime("%M"))
        actual_float_time = float(str(actual_hour)+"."+str(actual_minute))

        sunrise_hour = int(raw_sunrise.strftime("%H"))
        sunrise_minute = int(raw_sunrise.strftime("%M"))
        sunrise_float = float(str(sunrise_hour)+"."+str(sunrise_minute))

        sunset_hour = int(raw_sunset.strftime("%H"))
        sunset_minute = int(raw_sunset.strftime("%M"))
        sunset_float = float(str(sunset_hour)+"."+str(sunset_minute))

        time_icon = ""
        back_icon = ""
        moment = ""

        #Depending on the time of the day, selects one of 4 available icons
        if sunrise_float <= actual_float_time <= 11.0:
            time_icon = "morning.png"
            back_icon = "morning-land.png"
            moment = "Morning"
        elif 11.0 <= actual_float_time <= sunset_float - 1.3:
            time_icon = "afternoon.png"
            back_icon = "afternoon-land.png"
            moment = "Afternoon"
        elif sunset_float - 1.3 <= actual_float_time <= sunset_float:
            time_icon = "evening.png"
            back_icon = "evening-land.png"
            moment = "Evening"
        elif sunset_float <= actual_float_time <= 24.0:
            time_icon = "night.png"
            back_icon = "night-land.png"
            moment = "Night"
        else:
            time_icon = "night.png"
            back_icon = "night-land.png"
            moment = "Night"


        if nomenclature == "F":
            current_temperature = str(round(((y["temp"] - 273)*1.8 + 32), 2)) + " °F"
            feels_like = str(round(((y["feels_like"] - 273)*1.8 + 32), 2)) + "°" 
            max_temp = str(round(((y["temp_max"] - 273)*1.8 + 32), 2)) + "°"
            min_temp = str(round(((y["temp_min"] - 273)*1.8 + 32), 2)) + "°"
        else:
            current_temperature = str(round(y["temp"] - 273.15, 2)) + " °C"
            feels_like = str(round(y["feels_like"] - 273.15, 2)) + "°" 
            max_temp = str(round(y["temp_max"] - 273.15, 2)) + "°"
            min_temp = str(round(y["temp_min"] - 273.15, 2)) + "°"
        

        city_region_name = city_name + ", " + str(data["sys"]["country"])
        current_pressure = str(y["pressure"])
        current_humidity = str(y["humidity"]) + "%"

        weather = data["weather"]
        weather_description = weather[0]["description"].title()
        
        icon_code = weather[0]["icon"]
        icon_base_url = "http://openweathermap.org/img/w/"
        icon_complete_url = icon_base_url + icon_code + ".png"

        return render_template('results.html', moment=moment, back_icon=back_icon, time_icon=time_icon, sunrise=sunrise, sunset=sunset,time=actual_time ,icon=icon_complete_url, title=title, city=city_region_name, temperature=current_temperature, feels=feels_like, max=max_temp, min=min_temp, pressure=current_pressure, humidity=current_humidity, description=weather_description)
    else:
        return render_template('not-found.html', title=title, )


if __name__ == "__main__":
    app.run()