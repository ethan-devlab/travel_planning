# coding=utf-8

from ...models import Itinerary
from django.shortcuts import get_object_or_404, redirect


def delete_itinerary(request, id):
    itinerary = get_object_or_404(Itinerary, pk=id, owner=request.user)
    itinerary.delete()
    return redirect('my_itineraries')