from recommender.forms import SearchForm
from django.shortcuts import render
from django.http import Http404
from .forms import SearchForm
import random


def get_landing_guest(request):
    return render(request, "recommender/landingguest.html")
