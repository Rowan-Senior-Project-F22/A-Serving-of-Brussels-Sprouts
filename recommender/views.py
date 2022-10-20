
from recommender.forms import SearchForm
from django.shortcuts import render, redirect
from django.http import Http404
from recommender.models import Musicdata, ThreadModel, MessageModel
from .forms import SearchForm, SignUpForm, ThreadForm, MessageForm
import random
from email import message
from urllib import request
from django.contrib.auth import login
from django.dispatch import receiver
from django.views import View
from django.db.models import Q
from django.contrib.auth.models import User

def find_albums(artist, from_year = None, to_year = None):
    query = Musicdata.objects.filter(track_artist__contains = artist)
    if from_year is not None:
        query = query.filter(track_album_release_date__gte = from_year)
    if to_year is not None:
        query = query.filter(track_album_release_date__lte = to_year)
    return list(query.order_by('-track_popularity').values('track_id'))
    

def find_album_by_name(album):
    query = Musicdata.objects.filter(track_name__contains = album).values('track_id')
    resp = list(query)
    # Randomize to get different results each time
    random.shuffle(resp) 
    # Return the id of up to 3 albums
    return { 
        'albums': [item['track_id'] for item in resp[:3]]
    }


def get_artist(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            from_year = None if form.cleaned_data['from_year'] == None else int(form.cleaned_data['from_year'])
            to_year = None if form.cleaned_data['to_year'] == None else int(form.cleaned_data['to_year'])
            albums = find_albums(
                    form.cleaned_data['artist'],
                    from_year,
                    to_year
                )
            
            # Random 3 of top 10 popular albums
            answer = albums[:10]
            random.shuffle(answer)
            answer = list(answer)[:3] 
            return render(request, 'recommender/artist.html', {'form': form, 'albums': answer })
        else:
            raise Http404('Something went wrong')
    else:
        form = SearchForm()
        return render(request, 'recommender/artist.html', {'form': form})

def get_album(request):
    if request.method == 'GET':
        album = request.GET.get('album', None)
        if album is None:
            return render(request, "recommender/album.html", {})
        else:
            albums = {}
            if album != "":
                albums = find_album_by_name(album)
            return render(request, "recommender/results.html", albums)
  
def frontpage(request):
    return render(request, 'recommender/frontpage.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect('frontpage')
    else:
        form = SignUpForm()

    return render(request, 'recommender/signup.html', {'form': form})
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
        


