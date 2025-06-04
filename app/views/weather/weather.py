# coding=utf-8
import os

from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import datetime
from dotenv import load_dotenv

# load_dotenv()
#
# print(os.getenv("API_KEY"))

def index(request):
    was_limited = getattr(request, 'limited', False)
    # if request.COOKIES.get("visited") is None or str(request.COOKIES.get("visited")).lower() == "false" \
    #         or request.COOKIES.get('id_token') is None or request.COOKIES.get('id_token') == "":
    #     log_out(request)
    #     return redirect("/weather_app/authentication")
    # api_key = request.COOKIES.get('id_token')

    api_key = "24d2092641c20c9b1bb9f0bc366aa03a"  # for testing purpose, put your api key here

    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&appid={}'

    if request.method == 'POST':
        # if os.path.exists("data.json"):
        #     os.remove("data.json")

        city1 = request.POST['city1']
        # city2 = request.POST['city2']

        try:
            # if city1 and city2:
            #     with open("data.json", )
            if city1:
                weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, api_key, current_weather_url,
                                                                             forecast_url)
            else:
                weather_data1, daily_forecasts1 = None, None

            # if city2:
            #     weather_data2, daily_forecasts2 = fetch_weather_and_forecast(city2, api_key, current_weather_url,
            #                                                                  forecast_url)
            # else:
            #     weather_data2, daily_forecasts2 = None, None

            context = {
                'weather_data1': weather_data1,
                'daily_forecasts1': daily_forecasts1,
                # 'weather_data2': weather_data2,
                # 'daily_forecasts2': daily_forecasts2,
            }

            return render(request, 'index.html', context)

        except KeyError as e:
            messages.error(request, f"City not found, maybe city name can be more accurate or the API key is wrong.")
            return redirect('index')

    else:
        return render(request, 'index.html')

    # return render(request, 'weather_app/index.html')


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
        # 'id': response['id'],
        # 'api': api_key,
    }

    # if os.path.exists("data.json"):
    #     with open("data.json", "r", encoding="utf-8") as f:
    #         data = json.load(f)
    #         with open("data.json", "w", encoding="utf-8") as file:
    #             data['data'].append(weather_data)
    #             data_ = json.dumps(data, indent=2, ensure_ascii=False)
    #             file.write(data_)
    #
    # else:
    #     data_set = {
    #         "data": []
    #     }
    #
    #     data_set['data'].append(weather_data)
    #
    #     data = json.dumps(data_set, indent=2, ensure_ascii=False)
    #
    #     with open("data.json", "a", encoding="utf-8") as f:
    #         f.write(data)

    # print(forecast_response['list'])
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

    # DATA = load_data()
    # print(DATA['data'])
    return weather_data, daily_forecasts