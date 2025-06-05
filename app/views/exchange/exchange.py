#coding = utf-8

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv(".env")

EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

# currencies = {
#     "USD": {"code": "USD", "name": "美元", "flag": "🇺🇸"},
#     "EUR": {"code": "EUR", "name": "歐元", "flag": "🇪🇺"},
#     "GBP": {"code": "GBP", "name": "英鎊", "flag": "🇬🇧"},
#     "JPY": {"code": "JPY", "name": "日圓", "flag": "🇯🇵"},
#     "AUD": {"code": "AUD", "name": "澳幣", "flag": "🇦🇺"},
#     "CAD": {"code": "CAD", "name": "加幣", "flag": "🇨🇦"},
#     "CHF": {"code": "CHF", "name": "瑞士法郎", "flag": "🇨🇭"},
#     "CNY": {"code": "CNY", "name": "人民幣", "flag": "🇨🇳"},
#     "SEK": {"code": "SEK", "name": "瑞典克朗", "flag": "🇸🇪"},
#     "NZD": {"code": "NZD", "name": "紐幣", "flag": "🇳🇿"},
#     "TWD": {"code": "TWD", "name": "新台幣", "flag": "🇹🇼"},
#     "HKD": {"code": "HKD", "name": "港幣", "flag": "🇭🇰"},
#     "SGD": {"code": "SGD", "name": "新幣", "flag": "🇸🇬"},
#     "KRW": {"code": "KRW", "name": "韓圓", "flag": "🇰🇷"},
#     "INR": {"code": "INR", "name": "印度盧比", "flag": "🇮🇳"},
#     "MXN": {"code": "MXN", "name": "墨西哥披索", "flag": "🇲🇽"},
#     "RUB": {"code": "RUB", "name": "俄羅斯盧布", "flag": "🇷🇺"},
#     "ZAR": {"code": "ZAR", "name": "南非幣", "flag": "🇿🇦"},
#     "BRL": {"code": "BRL", "name": "巴西幣", "flag": "🇧🇷"},
#     "TRY": {"code": "TRY", "name": "土耳其里拉", "flag": "🇹🇷"},
# }

currency_path = os.path.join(os.path.dirname(__file__), 'currencies.json')
currencies = json.load(open(currency_path, "r", encoding="utf-8"))


def get_exchange_rate(from_currency, to_currency):
    url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{from_currency}/{to_currency}'
    response = requests.get(url, timeout=5)
    data = response.json()
    if data['result'] == 'success':
        return data['conversion_rate']
    else:
        return Exception(data.get("error-type", "Unknown error"))

@login_required
def exchange_view(request):
    result = None
    if request.method == 'POST':
        from_currency = request.POST.get('from_currency')
        to_currency = request.POST.get('to_currency')
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
            rate = get_exchange_rate(from_currency, to_currency)
            if isinstance(rate, Exception):
                messages.error(request, rate.args[0])
            converted = amount * rate
            result = f"{amount} {from_currency} = {converted:.2f} {to_currency}"
        except Exception as e:
            result = f"錯誤：{str(e)}"
        return render(request, 'exchange/exchange.html', {
            'currencies': currencies.values(),
            'from': currencies.get(from_currency),
            'to': currencies.get(to_currency),
            'result': result,
        })

    return render(request, 'exchange/exchange.html', {
        'currencies': currencies.values(),
    })