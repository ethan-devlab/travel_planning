# coding=utf-8

from ...models import Itinerary
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden


def itinerary_detail(request, id):
    itinerary = get_object_or_404(Itinerary, pk=id)
    if not itinerary.is_public and itinerary.owner != request.user and request.user not in itinerary.collaborators.all():
        return HttpResponseForbidden("You do not have permission to view this itinerary.")
    return render(request, 'itinerary/itinerary_detail.html', {'itinerary': itinerary})