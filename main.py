from turtle import color
from flask import Flask, render_template, request
from markupsafe import escape
from pprint import pprint
from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk
import requests
import logging

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
    
    #Weather API call
    weather_base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = processed_text

    weather_complete_url = weather_base_url + "appid=" + api_key + "&q=" + city_name

    weather_response = requests.get(weather_complete_url)

    weather = weather_response.json()

    if not city_name:
        return render_template('not-found.html', title=title, )
    elif weather["cod"] != "404":
        
        #One call API call (Forecast). Makes the call to the second API if the call to the first one was succesfull
        one_base_url = "https://api.openweathermap.org/data/2.5/onecall?"
        
        lat = weather["coord"]["lat"]
        lon = weather["coord"]["lon"]

        one_complete_url = one_base_url + "lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + api_key

        one_response = requests.get(one_complete_url)

        one = one_response.json()
        y = weather["main"]

        icon_base_url = "http://openweathermap.org/img/wn/"

        #To get the actual time of the searched location
        timezone_minutes = weather["timezone"] / 60
        delta_sum = timedelta(minutes=timezone_minutes)
        utc_time = datetime.utcnow()
        actual_raw_time = (utc_time + delta_sum)
        actual_time = actual_raw_time.strftime("%#I:%M %p")
        actual_date = actual_raw_time.strftime("%#I:%M %p - %A, %B %#d")

        #Hourly forecast for the next 24 hours, every 5 hours
        hourly = one["hourly"]
        hours = []
        hIconsUrls = []
        forecast_raw_temps = []

        interval = [1,6,11,16,21]

        for i in interval:
            hours.append((datetime.utcfromtimestamp(hourly[i]["dt"]) + (delta_sum)).strftime("%#I:%M"))
            hIconsUrls.append(icon_base_url + hourly[i]["weather"][0]["icon"] + "@2x.png")
            forecast_raw_temps.append(hourly[i]["temp"])

        daily = one["daily"]
        days = []
        mins = []
        maxes = []
        dIconsUrls = []

        for i in range(5):
            days.append((datetime.utcfromtimestamp(daily[i]["dt"]) + (delta_sum)).strftime("%A"))
            mins.append(daily[i]["temp"]["min"])
            maxes.append(daily[i]["temp"]["max"])
            dIconsUrls.append(icon_base_url + daily[i]["weather"][0]["icon"] + "@2x.png")


        #To get the sunrise an sunset formatted times for the searchad location
        raw_sunrise = (datetime.utcfromtimestamp(weather["sys"]["sunrise"]) + (delta_sum))
        sunrise = raw_sunrise.strftime("%H:%M")
        raw_sunset = (datetime.utcfromtimestamp(weather["sys"]["sunset"]) + (delta_sum))
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
        color = "" 

        #Depending on the time of the day, selects one of 4 available icons
        if sunrise_float <= actual_float_time <= 11.0:
            time_icon = "morning.png"
            back_icon = "morning-land.jpeg"
            color = "rgba(0, 0, 0, 0.8);"
            background_color = "rgba(255, 255, 255, 0.5);"
 
        elif 11.0 <= actual_float_time <= sunset_float - 1.3:
            time_icon = "afternoon.png"
            back_icon = "afternoon-land.jpeg"
            color = "rgba(0, 0, 0, 0.8)"
            background_color = "rgba(255, 255, 255, 0.5);"

        elif sunset_float - 1.3 <= actual_float_time <= sunset_float:
            time_icon = "evening.png"
            back_icon = "evening-land.jpeg"
            color = "rgba(0, 0, 0, 0.8)"
            background_color = "rgba(255, 255, 255, 0.5);"

        elif sunset_float <= actual_float_time <= 24.0:
            time_icon = "night.png"
            back_icon = "night-land.jpeg"
            color = "rgba(255, 255, 255, 0.8);"
            background_color = "rgba(255, 255, 255, 0.2);"

        else:
            time_icon = "night.png"
            back_icon = "night-land.jpeg"
            color = "rgba(255, 255, 255, 0.8);"
            background_color = "rgba(255, 255, 255, 0.2);"


        #Depending on what nomenclature the user chooses
        if nomenclature == "F":
            current_temperature = str(round(((y["temp"] - 273)*1.8 + 32))) + "°"
            feels_like = str(round(((y["feels_like"] - 273)*1.8 + 32), 2)) + "°" 
            max_temp = str(round(((y["temp_max"] - 273)*1.8 + 32))) + "°"
            min_temp = str(round(((y["temp_min"] - 273)*1.8 + 32))) + "°"
            forecast_temps = getTemps(forecast_raw_temps,"F")
            min_temps = getTemps(mins,"F")
            max_temps = getTemps(maxes,"F")
        else:
            current_temperature = str(round(y["temp"] - 273.15)) + "°"
            feels_like = str(round(y["feels_like"] - 273.15, 2)) + "°" 
            max_temp = str(round(y["temp_max"] - 273.15)) + "°"
            min_temp = str(round(y["temp_min"] - 273.15)) + "°"
            forecast_temps = getTemps(forecast_raw_temps, "C")
            min_temps = getTemps(mins,"C")
            max_temps = getTemps(maxes,"C")
        

        city_region_name = city_name + " " + str(weather["sys"]["country"])
        current_pressure = str(y["pressure"])
        current_humidity = str(y["humidity"]) + "%"
        current_cloudiness = str(one["current"]["clouds"]) + "%"
        current_uvi = one["current"]["uvi"]

        curr_weather = weather["weather"]
        weather_description = curr_weather[0]["description"].title()
        
        #Current weather icon
        icon_code = curr_weather[0]["icon"]
        icon_complete_url = icon_base_url + icon_code + "@2x.png"


        return render_template('results.html', 
            hourly=hours, 
            hourly_icons=hIconsUrls,
            hourly_temps=forecast_temps,
            daily=days,
            daily_min_temps=min_temps,
            daily_max_temps=max_temps,
            daily_icons=dIconsUrls,
            background_opacity=background_color, 
            text_color=color, 
            back_icon=back_icon, 
            time_icon=time_icon, 
            sunrise=sunrise, 
            sunset=sunset,
            time=actual_time,
            date=actual_date,
            icon=icon_complete_url, 
            title=title, 
            city=city_region_name, 
            temperature=current_temperature, 
            feels=feels_like, 
            max=max_temp, min=min_temp, 
            pressure=current_pressure,
            uvi=current_uvi,
            clouds=current_cloudiness, 
            humidity=current_humidity, 
            description=weather_description
        )
    else:
        return render_template('not-found.html', title=title, )

def getTemps(temps, nomenclature):
    final_temps = []
    
    for i in temps:
        if nomenclature == "C":
            processed_temp = str(round((i - 273.15), 1)) + "°"
        else:
            processed_temp = str(round((round((i - 273.15), 1) * 1.8 + 32), 1)) + "°"

        final_temps.append(processed_temp)
    
    return final_temps
    


    



if __name__ == "__main__":
    app.run()