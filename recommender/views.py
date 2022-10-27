from recommender.forms import SearchForm
from django.shortcuts import render
from django.http import Http404
from .forms import SearchForm
import random


def get_landing_guest(request):
    return render(request, "recommender/landingguest.html")
    
def user_profile(request):
    # query the DB
    return render(request, 'recommender/user_profile.html', {})

def user_playlist(request):
    return render(request, 'recommender/user_playlist.html', {})

def l_room(request, room_name):
    return render(request, 'l_room.html', {'room_name': room_name})