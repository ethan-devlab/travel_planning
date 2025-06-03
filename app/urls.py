# coding=utf-8

from django.urls import path
from .views.auth import auth
from .views.itinerary import search, create, edit, delete, detail, template, my_iter


urlpatterns = [
    path('', search.search_itineraries, name='search'),
    path('search/', search.search_itineraries, name='search'),
    path('create/', create.create_itinerary, name='create'),
    path('templates/', template.template_list, name='template_list'),
    path('copy/', template.copy_itinerary, name='copy_itinerary'),
    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),
    path('register/', auth.register, name='register'),
    path('itinerary/<int:id>/', detail.itinerary_detail, name='itinerary_detail'),
    path('my-itineraries/', my_iter.my_itineraries, name='my_itineraries'),
    path('edit/<int:id>/', edit.edit_itinerary, name='edit_itinerary'),
    path('delete/<int:id>/', delete.delete_itinerary, name='delete_itinerary'),
]