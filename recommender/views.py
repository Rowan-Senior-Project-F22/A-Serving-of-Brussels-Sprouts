import json

from django.shortcuts import render, redirect
from django.http import Http404
from recommender.models import ThreadModel, MessageModel
from .forms import ThreadForm, MessageForm
from .forms import SearchForm
import random
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
                return redirect('thread', pk=thread.pk)
        except:
            return redirect('create-thread')


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
            reciever_user=receiver,
            body=request.POST.get('message')
        )
        message.save()
        return redirect('thread', pk=pk)


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

    # TODO: Pull these from Spotify Genre Seed Web API
    available_genre_seeds = ['rock', 'country', 'rap']

    # Retrieve the current user, parse their preferences given the available
    # genre seeds and ensure genre seeds are in the list of Spotify genre seeds.
    current_user = request.user
    try:
        users_preferences = json.loads(current_user.preferences)
        users_preferences['likes'] = list(filter(lambda x: x in available_genre_seeds, users_preferences['likes']))
        users_preferences['dislikes'] = list(filter(lambda x: x in available_genre_seeds, users_preferences['dislikes']))
    except any as E:
        # TODO: Fallback for if user preferences are not valid formatting.
        users_preferences = {
            "likes": [],
            "dislikes": []
        }
    return render(request=request, template_name="recommender/user_preferences.html",
                  context={"users_preferences": users_preferences})


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
