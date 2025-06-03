# coding=utf-8

from ...models import Itinerary
from django.shortcuts import render


def my_itineraries(request):
    itineraries = Itinerary.objects.filter(owner=request.user).order_by('-updated_at')
    return render(request, 'my_itineraries.html', {'itineraries': itineraries})