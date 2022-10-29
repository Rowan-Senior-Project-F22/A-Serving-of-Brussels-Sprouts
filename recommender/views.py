from django.shortcuts import render, redirect
from django.http import Http404
from recommender.models import ThreadModel, MessageModel
from .forms import   ThreadForm, MessageForm
from .forms import SearchForm
import random
from email import message
from urllib import request
from django.contrib.auth import login
from django.dispatch import receiver
from django.views import View
from django.db.models import Q
from django.contrib.auth.models import User

def get_landing_guest(request):
    return render(request, "recommender/landingguest.html")
    
def user_profile(request):
    # query the DB
    return render(request, 'recommender/user_profile.html', {})

def user_playlist(request):
    return render(request, 'recommender/user_playlist.html', {})


class ListThreads(View):
    def get(self, request, *arg, **kwargs):
        threads = ThreadModel.objects.filter(Q(user = request.user) | Q(receiver = request.user))

        context = {
            'threads':threads
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
        receiver = User.objects.get(username = username)
        if ThreadModel.objects.filter(user = request.user, receiver = receiver).exists():
            thread = ThreadModel.objects.filter(user = request.user, receiver = receiver)[0]
            return redirect('thread',pk = thread.pk)
        elif ThreadModel.objects.filter(user = receiver, receiver = request.user).exists():
            thread = ThreadModel.objects.filter(user = receiver, reciever = request.user)[0]
            return redirect('thread', pk = thread.pk)
        if form.is_valid:
            thread = ThreadModel(
                user = request.user,
                receiver = receiver
            )
            thread.save()
            return redirect('thread', pk =thread.pk )
       except:
        return redirect('create-thread')

class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk =pk)
        message_list = MessageModel.objects.filter(thread__pk__contains = pk)
        context = {
            'thread': thread,
            'form': form, 
            'message_list': message_list
        }
        return render(request, 'recommender/thread.html', context)

class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        thread = ThreadModel.objects.get(pk = pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver
        
        message = MessageModel(
            thread = thread, 
            sender_user = request.user,
            reciever_user = receiver,
            body = request.POST.get('message')
        )
        message.save()
        return redirect('thread', pk = pk)
        


def l_room(request, room_name):
    return render(request, 'l_room.html', {'room_name': room_name})
