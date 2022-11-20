import json

from django.shortcuts import render, redirect
from django.http import Http404
from recommender.models import ThreadModel, MessageModel, Playlist
from .forms import ThreadForm, MessageForm, UserPreferencesForm
from .forms import SearchForm
import random, spotipy
from email import message
from urllib import request
from django.contrib.auth import login, authenticate, logout
from django.dispatch import receiver
from django.views import View
from django.db.models import Q
from .models import User
from .forms import CustomUserForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

cid = '2de1575d99b14786ae4f7e46e33e494e'
secret = 'fbf315776bda4ea2aaeeeb1ec559de7d'
client_credentials = spotipy.oauth2.SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials)


def get_landing_guest(request):
    return render(request, "recommender/landingguest.html")


@login_required
def user_profile(request):
    # query the DB
    return render(request, 'recommender/user_profile.html', {})


class ListThreads(View):
    def get(self, request, *arg, **kwargs):
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))

        context = {
            'threads': threads
        }

        return render(request, 'recommender/inbox.html', context)


class CreateThread(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()
        context = {
            'form': form
        }

        return render(request, 'recommender/create_thread.html', context)

    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)

        username = request.POST.get('username')

        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(user=request.user, receiver=receiver).exists():
                thread = ThreadModel.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('thread', pk=thread.pk)
            elif ThreadModel.objects.filter(user=receiver, receiver=request.user).exists():
                thread = ThreadModel.objects.filter(user=receiver, reciever=request.user)[0]
                return redirect('thread', pk=thread.pk)
            if form.is_valid:
                thread = ThreadModel(
                    user=request.user,
                    receiver=receiver
                )
                thread.save()
                return redirect('recommender:thread', pk=thread.pk)
        except:
            return redirect('recommender:create-thread')


class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)
        context = {
            'thread': thread,
            'form': form,
            'message_list': message_list
        }
        return render(request, 'recommender/thread.html', context)


class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        thread = ThreadModel.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver

        message = MessageModel(
            thread=thread,
            sender_user=request.user,
            receiver_user=receiver,
            body=request.POST.get('message')
        )
        message.save()
        return redirect('recommender:thread', pk=pk)


def l_room(request, room_name):
    return render(request, 'l_room.html', {'room_name': room_name})


def get_register(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("recommender:user_profile")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = CustomUserForm()
    return render(request=request, template_name="recommender/register.html", context={"register_form": form})


@login_required
def user_preferences(request):
    """Retrieves the user's preferences. Fetches the current user in session,
    returns their information, parses the preferences to a readable format
    and passes as context.

    """
    if request.method == 'POST':
        # TODO: Handle form logic to add and remove from the user's preferences.
        pass

    else:
        # Pulls genre list from Spotify API using the client credentials authentication flow
        available_genre_seeds = []
        genre_list = list(sp.recommendation_genre_seeds().values())
        for i in range(len(genre_list[0])):
            available_genre_seeds.append(genre_list[0][i])

        # Retrieve the current user, parse their preferences given the available
        # genre seeds and ensure genre seeds are in the list of Spotify genre seeds.
        current_user = request.user
        try:
            users_preferences = json.loads(current_user.preferences)
            if 'likes' not in users_preferences:
                users_preferences['likes'] = []
            if 'dislikes' not in users_preferences:
                users_preferences['dislikes'] = []
            users_preferences['likes'] = list(filter(lambda x: x in available_genre_seeds, users_preferences['likes']))
            users_preferences['dislikes'] = list(
                filter(lambda x: x in available_genre_seeds, users_preferences['dislikes']))
        except any as E:
            users_preferences = {
                "likes": [],
                "dislikes": []
            }
        preference_form = UserPreferencesForm(genre_seed_options=available_genre_seeds)
        playlist_count = Playlist.objects.filter(Q(creator=request.user)).count()
        return render(request=request, template_name="recommender/user_preferences.html",
                      context={"users_preferences": users_preferences, "available_genre_seeds": available_genre_seeds,
                               "playlist_count": playlist_count, "preference_form": preference_form})


@login_required
def user_account_settings(request):
    """Retrieves the user's account settings.

    """
    # TODO: Handle post request for account settings
    if request.method == "POST":
        pass

    # Represents the current user.
    user = request.user

    # Retrieves the user's post count.
    playlist_count = Playlist.objects.filter(Q(creator=user)).count()

    return render(request=request, template_name="recommender/settings.html", context={
        "playlist_count": playlist_count
    })


def get_member_feed(request):
    if request.method == 'GET':
        memberlist = list([])
        random.shuffle(memberlist)
        answer = list(memberlist)[:4]  # Could put [:4] in comments
        page = request.GET.get('page', 1)
        paginator = Paginator(memberlist, 20)  # len(memberlist)
        try:
            numbers = paginator.page(page)
        except PageNotAnInteger:
            numbers = paginator.page(1)  # used to be 1
        except EmptyPage:
            numbers = paginator.page(paginator.num_pages)
        return render(request=request, template_name='recommender/landing_member.html', context={'memberlist': numbers})


def get_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {email}.")
                return redirect("recommender:user_profile")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="recommender/login.html", context={"login_form": form})


@login_required
def get_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("recommender:get_landing_guest")


@login_required
def user_playlist(request, user_id):
    return render(request, 'recommender/user_playlist.html', {})
