# coding=utf-8
import os

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
import datetime
from dotenv import load_dotenv

load_dotenv("env/.env")

@login_required
def index(request):
    api_key = os.getenv("WEATHER_API_KEY")
    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&appid={}'

    if request.method == 'POST':
        city = request.POST['city']

        try:
            if city:
                weather_data, daily_forecasts = fetch_weather_and_forecast(city, api_key, current_weather_url,
                                                                             forecast_url)
            else:
                weather_data, daily_forecasts = None, None

            context = {
                'weather_data': weather_data,
                'daily_forecasts': daily_forecasts,
            }

            return render(request, 'weather/index.html', context)

        except KeyError as e:
            print(f"KeyError: {e}")
            messages.error(request, f"City not found, maybe city name can be more accurate or the API key is wrong.")
            return redirect('weather')

    else:
        return render(request, 'weather/index.html')


def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    response = requests.get(current_weather_url.format(city, api_key)).json()
    lat, lon = response['coord']['lat'], response['coord']['lon']
    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()
    weather_data = {
        'city': city,
        'country': response['sys']['country'],
        'temperature': response['main']['temp'],
        'feels_like': response['main']['feels_like'],
        'description': str(response['weather'][0]['description']).capitalize(),
        'icon': response['weather'][0]['icon'],
        'humidity': response['main']['humidity'],
        'visibility': round(response['visibility'] / 1000, 2),
        'wind_speed': round(response['wind']['speed'] * 3.6, 2),
        # 'precipitation': response['rain']['1h'],
        'cloudiness': response['clouds']['all'],
        'date': datetime.datetime.fromtimestamp(response['dt']).strftime('%b %d'),
        'time': datetime.datetime.fromtimestamp(response['dt']).strftime("%I:%M %p"),
    }

    daily_forecasts = []
    for daily_data in forecast_response['list'][:25]:
        daily_forecasts.append({
            'day': datetime.datetime.fromtimestamp(daily_data['dt']).strftime('%A'),
            'date': datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%b %d"),
            'time': datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%I:%M %p"),
            'temperature': daily_data['main']['temp'],
            'description': str(daily_data['weather'][0]['description']).capitalize(),
            'icon': daily_data['weather'][0]['icon'],
            'humidity': daily_data['main']['humidity'],
            'visibility': round(daily_data['visibility'] / 1000, 2),
            'wind_speed': round(daily_data['wind']['speed'] * 3.6, 2),
            'wind_gust': round(daily_data['wind']['gust'] * 3.6, 2),
            'feels_like': daily_data['main']['feels_like'],
            'temp_min': daily_data['main']['temp_min'],
            'temp_max': daily_data['main']['temp_max'],
            'cloudiness': daily_data['clouds']['all'],
            'pop': round(daily_data['pop'] * 100, 2),
        })

    return weather_data, daily_forecasts