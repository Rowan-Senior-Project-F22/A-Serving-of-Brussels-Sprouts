import ast
import json, re
from django.template.defaultfilters import slugify
from django.shortcuts import render, redirect
from recommender.models import ThreadModel, MessageModel, MusicData, Playlist
from django.http import Http404, HttpResponseRedirect
from utils.users import init_users_preferences
from .forms import ThreadForm, MessageForm, UserPreferencesForm
from .forms import SearchForm, ListeningRoomForm
import random, spotipy
from email import message
from urllib import request
from django.contrib.auth import login, authenticate, logout
from django.dispatch import receiver
from django.views import View
from django.db.models import Q
from .models import User
from .forms import CustomUserForm
from .models import ListeningRoom, ChatRoom
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

cid = '2de1575d99b14786ae4f7e46e33e494e'
secret = 'fbf315776bda4ea2aaeeeb1ec559de7d'
client_credentials = spotipy.oauth2.SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials)

'''
get_new_releases()

Gets a number of randomly selected, newly released songs. By default, the
number of random tracks is 10.

Gets new releases from Spotify, which returns a collection of albums. Tracks
are then selected at random from each returned album.
If the track_id is not already associated with an instance of MusicData, a new
MusicData instance is created and stored in the database.

Jeremy Juckett
'''
@login_required
def get_new_releases(request):
    count = 25
    data = [] # context sent to template
    results = sp.new_releases(country = None, limit = count, offset = 0)

    # check track against MusicData model, creating a new instance if it does
    # not exist. For each song, create a new post.
    for item in results['albums']['items']:
        # store album info
        album_id = item['id']
        album_name = item['name']
        artist = item['artists'][0]['name']
        album_cover = item['images'][0]['url']
        release_date = item['release_date']

        # store track info
        tracks = sp.album_tracks(album_id)
        random_index = random.randint(0, item['total_tracks'] - 1) #grab random track
        track_id = tracks['items'][random_index]['id']
        track_name = tracks['items'][random_index]['name']
        preview_url = tracks['items'][random_index]['preview_url']

        # check against model instances
        obj = MusicData.objects.all().filter(track_id=track_id)
        if len(obj) == 0:
            # create new instance
            song = MusicData(
                track_id = track_id,
                track_name = track_name,
                track_album_id = album_id,
                track_album_name = album_name,
                album_cover = album_cover,
                artist_name = artist,
                release_date = release_date[0:4],
                preview_url = preview_url
            )
            song.save()
            data.append(song)
        else:
            # instance already exists in the database
            data.append(obj[0])

    ''' Uncomment the following code to remove the database records '''
    #print('Deleting all Playlist objects\n')
    #Playlist.objects.all().delete()
    #print('Deleting all MusicData objects\n')
    #MusicData.objects.all().delete()

    return render(request, 'recommender/new_releases.html', {'data': data})

'''
like_view(request)

Handles both a user's likes and dislikes.

Jeremy Juckett
'''
@login_required
def like_view(request):
    like_query_result = Playlist.objects.all().filter(owner=request.user, name='likes')
    dislike_query_result = Playlist.objects.all().filter(owner=request.user, name='dislikes')

    print("Dislike Size:", len(dislike_query_result))
    print("Like Size:", len(like_query_result))

    # handle liked songs
    if 'like' in request.POST:
        liked_track_id = request.POST['like']
        # if the liked song is already in the dislike-playlist, remove it and update the record.
        # if the dislike count is not zero, decrement.
        if len(dislike_query_result) != 0 and liked_track_id in dislike_query_result[0].songs:
            dislike_query_result[0].songs = dislike_query_result[0].songs.replace(liked_track_id + ',', '')
            dislike_query_result[0].save()

            obj = MusicData.objects.get(track_id=liked_track_id)
            if obj.dislikes > 0:
                obj.dislikes = obj.dislikes - 1
                obj.save()

        # if the liked-song is not already in the 'likes' playlist,
        # then append it.
        # increment the like count
        if liked_track_id not in like_query_result[0].songs:
            like_query_result[0].songs += liked_track_id + ','
            like_query_result[0].save()

            obj = MusicData.objects.get(track_id=liked_track_id)
            obj.likes = obj.likes + 1
            obj.save()

    # handle disliked songs
    elif 'dislike' in request.POST:
        disliked_track_id = request.POST['dislike']
        # if the disliked song is already in the like-playlist, remove it and update the record.
        # if the like count is not zero, decrement it.
        if len(like_query_result) != 0 and disliked_track_id in like_query_result[0].songs:
            like_query_result[0].songs = like_query_result[0].songs.replace(disliked_track_id + ',', '')
            like_query_result[0].save()

            obj = MusicData.objects.get(track_id=disliked_track_id)
            if obj.likes > 0:
                obj.likes = obj.likes - 1
                obj.save()

        # if the disliked-song is not already in the 'dislikes' playlist,
        # then append it.
        # increment the dislike count.
        if disliked_track_id not in dislike_query_result[0].songs:
            dislike_query_result[0].songs += disliked_track_id + ','
            dislike_query_result[0].save()

            obj = MusicData.objects.get(track_id=disliked_track_id)
            obj.dislikes = obj.dislikes + 1
            obj.save()

    #return get_new_releases(request)
    return user_profile(request)


'''
user_profile(request)

Jeremy Juckett
'''
@login_required
def user_profile(request):
    number_of_loads = 4
    like_query_result = Playlist.objects.all().filter(owner=request.user, name='likes')
    dislike_query_result = Playlist.objects.all().filter(owner=request.user, name='dislikes')

    liked_music_data = []
    disliked_music_data = []

    print('Likes:', like_query_result[0].songs.split(","))
    print('Dislikes:', dislike_query_result[0].songs.split(","))

    print("Dislike Size:", len(dislike_query_result))
    print("Like Size:", len(like_query_result))

    # handle the likes
    if len(like_query_result) != 0 and like_query_result[0].songs != "":
        # populate the context with music data from random liked track ids
        liked_track_ids = like_query_result[0].songs.split(",")
        liked_track_ids.remove('') # remove the empty entry at the end
        
        if number_of_loads >= len(liked_track_ids):
            likes_subset = liked_track_ids
        else:
            likes_subset = liked_track_ids[0:number_of_loads - 1]
        
        for l in likes_subset:
            liked_music_data.append(MusicData.objects.all().filter(track_id=l)[0])

    # handle the dislikes
    if len(dislike_query_result) != 0 or dislike_query_result[0].songs != "":
        # populate the context with music data from random disliked track ids
        disliked_track_ids = dislike_query_result[0].songs.split(",")
        disliked_track_ids.remove('') # remove the empty entry at the end
        
        if number_of_loads >= len(disliked_track_ids):
            dislikes_subset = disliked_track_ids
        else:
            dislikes_subset = disliked_track_ids[0:number_of_loads - 1]

        for d in dislikes_subset:
            disliked_music_data.append(MusicData.objects.all().filter(track_id=d)[0])

    context = {
        'liked_music': liked_music_data,
        'disliked_music': disliked_music_data
    }

    return render(request, 'recommender/user_profile.html', context)


def get_landing_guest(request):
    return render(request, "recommender/landingguest.html")


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

def l_room(request, slug):
    slug = slugify(slug)
    if (ChatRoom.objects.filter(room_slug = slug)):
        return render(request, 'l_room.html', {'l_room': l_room, 'slug': slug})
    else:
        messages.error(request, "This room does not exist")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
@login_required
def l_room_create(request):
    if request.method == "POST":
        form = ListeningRoomForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('room_name')
            slug = slugify(name)
            if ChatRoom.objects.filter(room_slug=slug):
                messages.error(request, "This chatroom already exists")
                form = ListeningRoomForm()
                return render(request, 'l_room_create.html')
            chat = ChatRoom(room_name=name, room_slug=slug)
            chat.save()
            messages.success(request, "Chatroom created successfully")
            return redirect("recommender:l_room", slug)
    form = ListeningRoomForm()
    return render(request, 'l_room_create.html')


def get_register(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            # create the default likes and dislikes playlists
            like_playlist = Playlist(name='likes',
                is_public=True, owner=user)
            like_playlist.save()
            print("\n\n\nCREATED LIKE PLAYLIST\n\n\n")

            dislike_playlist = Playlist(name='dislikes',
                is_public=True, owner=user)
            dislike_playlist.save()
            print("\n\n\nCREATED LIKE PLAYLIST\n\n\n")

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
    and passes as context. Inefficient version

    """
    # Pulls genre list from Spotify API using the client credentials authentication flow
    available_genre_seeds = []
    genre_list = list(sp.recommendation_genre_seeds().values())
    for i in range(len(genre_list[0])):
        available_genre_seeds.append(genre_list[0][i])

    users_preferences = init_users_preferences(request=request, available_genre_seeds=available_genre_seeds)

    if request.method == 'POST':
        # TODO: Handle form logic to remove from the user's preferences.
        form = UserPreferencesForm(genre_seed_options=available_genre_seeds, data=request.POST)
        try:
                user = request.user

                if 'likes' not in users_preferences:
                    users_preferences['likes'] = []
                if 'dislikes' not in users_preferences:
                    users_preferences['dislikes'] = []

                if 'preferences_like' in form.data:
                    users_preferences['likes'].append(form.data["genre_seed"])
                    user.preferences = users_preferences
                    user.save()
                elif 'preferences_dislike' in form.data:
                    users_preferences['dislikes'].append(form.data["genre_seed"])
                    user.preferences = users_preferences
                    user.save()
                messages.success(request=request, message='Successfully modified user preferences.')
        except BaseException as E:
            print(E)
            # Pass since there was an error, setting the message to
            # let the user know.
            messages.error(request, "An error occurred while processing your request. Please try again.")

    # Inefficient for now but works
    genres_available = list(filter(lambda x: x not in users_preferences['likes'] and x not in users_preferences['dislikes'], available_genre_seeds))
    preference_form = UserPreferencesForm(genre_seed_options=genres_available)
    playlist_count = Playlist.objects.filter(Q(creator=request.user)).count()

    return render(request=request, template_name="recommender/user_preferences.html",
                        context={"likes": users_preferences['likes'],'dislikes': users_preferences['dislikes'],
                                 "available_genre_seeds": available_genre_seeds,
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
    like_query_result = Playlist.objects.all().filter(owner=request.user, name='likes')
    dislike_query_result = Playlist.objects.all().filter(owner=request.user, name='dislikes')

    # fetch like playlist
    if len(like_query_result) != 0 or like_query_result[0].songs != "":
        # populate the context with music data from random liked track ids
        liked_track_ids = like_query_result[0].songs.split(",")
        liked_track_ids.remove('') # remove the empty entry at the end
        
        liked_music_data = []
        for l in liked_track_ids:
            liked_music_data.append(MusicData.objects.all().filter(track_id=l)[0])

    # fetch the dislike playlist
    if len(dislike_query_result) != 0 or dislike_query_result[0].songs != "":
        # populate the context with music data from random liked track ids
        disliked_track_ids = dislike_query_result[0].songs.split(",")
        disliked_track_ids.remove('') # remove the empty entry at the end
        
        disliked_music_data = []
        for d in disliked_track_ids:
            disliked_music_data.append(MusicData.objects.all().filter(track_id=d)[0])

    context = {
        'liked_music': liked_music_data,
        'disliked_music': disliked_music_data
    }

    return render(request, 'recommender/user_playlist.html', context)
