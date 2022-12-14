import ast
import json, re
from django.template.defaultfilters import slugify
from django.shortcuts import render, redirect
from recommender.models import ThreadModel, MessageModel, MusicData, Playlist, Notification
from django.http import Http404, HttpResponseRedirect
from utils.users import init_users_preferences, generate_friend_recommendations
from .forms import ThreadForm, MessageForm, UserFriendSettingsForm, UserPreferencesForm
from .forms import SearchForm, ListeningRoomForm, UserSearchForm
from django.conf import settings
import random, spotipy
from email import message
from urllib import request
from django.contrib.auth import login, authenticate, logout
from django.dispatch import receiver
from django.views import View
from django.db.models import Q, Model
from .models import User
from .forms import CustomUserForm
from .models import ListeningRoom, ChatRoom
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render


cid = '2de1575d99b14786ae4f7e46e33e494e'
secret = 'fbf315776bda4ea2aaeeeb1ec559de7d'
client_credentials = spotipy.oauth2.SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials)


def update_musicdata_model(items):
    pass

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
def get_new_releases():
    count = 25
    data = [] # context sent to template
    results = sp.new_releases(country = None, limit = count, offset = 0)

    # check track against MusicData model, creating a new instance if it does
    # not exist. For each song, create a new post.
    for item in results['albums']['items']:
        album_id = item['id']
        album_name = item['name']

        # get the genres as a single, comma-separated string
        genre_list = sp.artist(item['artists'][0]['id'])['genres']
        genres = ''
        for i in range(len(genre_list)):
            genres += genre_list[i] + ','
            i += 1

        album_cover = item['images'][0]['url']
        release_date = item['release_date']

        # store track info
        tracks = sp.album_tracks(album_id)                

        # The upper limit of the random index interval should not exceed 50
        # to prevent an out of bounds index.
        # Spotify seems to return 50 tracks at most, even if the album has
        # more than 50 tracks total.
        if item['total_tracks'] >= 50:
            random_index = random.randint(0, 49) #grab random track
        else:
            random_index = random.randint(0, item['total_tracks'] - 1) #grab random track

        # get track artists
        artist_name = ''
        artist_id = ''
        for track_artist in tracks['items'][random_index]['artists']:
            artist_name += track_artist['name'] + ','
            artist_id += track_artist['id'] + ','

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
                track_genre = genres,
                album_cover = album_cover,
                artist_name = artist_name,
                artist_id = artist_id,
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

    return data

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
def user_profile(request, user_name):
    user = User.objects.get(username=user_name)
    if(user == ''):
        user = request.user
    number_of_loads = 4
    like_query_result = Playlist.objects.all().filter(owner=user, name='likes')
    dislike_query_result = Playlist.objects.all().filter(owner=user, name='dislikes')

    liked_music_data = []
    disliked_music_data = []

    like_count = 0
    dislike_count = 0

    # print('Likes:', like_query_result[0].songs.split(","))
    # print('Dislikes:', dislike_query_result[0].songs.split(","))

    # print("Dislike Size:", len(dislike_query_result))
    # print("Like Size:", len(like_query_result))

    # handle the likes
    if len(like_query_result) != 0 and like_query_result[0].songs != "":
        # populate the context with music data from random liked track ids
        liked_track_ids = like_query_result[0].songs.split(",")
        liked_track_ids.remove('') # remove the empty entry at the end
        like_count = len(liked_track_ids)
            
        random.shuffle(liked_track_ids)
        if number_of_loads >= len(liked_track_ids):
            likes_subset = liked_track_ids
        else:
            likes_subset = liked_track_ids[0:number_of_loads]
            
        for l in likes_subset:
            liked_music_data.append(MusicData.objects.all().filter(track_id=l)[0])

    # handle the dislikes
    if len(dislike_query_result) != 0 and dislike_query_result[0].songs != "":
        # populate the context with music data from random disliked track ids
        disliked_track_ids = dislike_query_result[0].songs.split(",")
        disliked_track_ids.remove('') # remove the empty entry at the end
        dislike_count = len(disliked_track_ids)
            
        random.shuffle(disliked_track_ids)
        if number_of_loads >= len(disliked_track_ids):
            dislikes_subset = disliked_track_ids
        else:
            dislikes_subset = disliked_track_ids[0:number_of_loads]

        for d in dislikes_subset:
            disliked_music_data.append(MusicData.objects.all().filter(track_id=d)[0])

    context = {
        'username': user.username,
        'user_email': user.email,
        'friend_count': user.friend_count,
        'like_count': like_count,
        'dislike_count': dislike_count,
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
            messages.error(request, 'Invalid username')
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

        notification = Notification.objects.create(
            notification_type = 4,
            from_user = request.user,
            to_user = receiver,
            thread = thread
        )
        return redirect('recommender:thread', pk=pk)

class ThreadNotification(View):
     def get(self, request, notification_pk, object_pk, *args, **kwargs):
         notification = Notification.objects.get(pk = notification_pk)
         thread = ThreadModel.objects.get(pk = object_pk)

         notification.user_has_seen = True
         notification.save()

         return redirect('recommender:thread', pk = object_pk)

def l_room(request, slug):
    slug = slugify(slug)
    if (slug == "main"):
        room = ChatRoom.objects.get(room_slug=slug)
        albums = sp.new_releases()
        album_id = albums['albums']['items'][0]['id']
        genres = sp.artist(sp.album(album_id)['artists'][0]['uri'])['genres']
        genres_json = json.dumps(genres)
        room.album = album_id
        room.genres = genres_json
        room.save()
        return render(request, 'l_room.html', {'l_room': l_room, 'room_name': room.room_name, 'slug': slug, 'album': album_id})
    if (ChatRoom.objects.filter(room_slug = slug)):
        room = ChatRoom.objects.get(room_slug=slug)
        return render(request, 'l_room.html', {'l_room': l_room, 'room_name': room.room_name, 'slug': slug, 'album': room.album})
    else:
        messages.error(request, "This room does not exist")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
@login_required
def l_room_create(request):
    if request.method == "POST":
        form = ListeningRoomForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('room_name')
            album = form.data.get('album')
            artist = form.data.get('artist')
            slug = slugify(name)
            slug = slug.replace('-', '')
            if artist == '':
                album_uri = sp.search(q='album:' + album, type="album")['albums']['items'][0]['id']
            else:
                album_uri = sp.search(q='album:' + album+', artist:'+artist, type="album")['albums']['items'][0]['id']
            genres = sp.artist(sp.album(album_uri)['artists'][0]['uri'])['genres']
            genres_json = json.dumps(genres)
            if ChatRoom.objects.filter(room_slug=slug):
                messages.error(request, "This chatroom already exists")
                form = ListeningRoomForm()
                return render(request, 'l_room_create.html', {})
            chat = ChatRoom(room_name=name, room_slug=slug, album=album_uri, genres=genres_json)
            chat.save()
            messages.success(request, "Chatroom created successfully")
            return redirect("recommender:l_room", slug)
    form = ListeningRoomForm()
    return render(request, 'l_room_create.html', {})


class ThreadNotification(View):
    def get(self, request, notification_pk, object_pk, *args, **kwargs):
        notification = Notification.objects.get(pk = notification_pk)
        thread = ThreadModel.objects.get(pk = object_pk)


def import_spotify_playlist(request, playlist_id):
    """Handles logic to import a playlist from Spotify. When the user clicks the 'import'
    button on the import_spotify view, passes the playlist ID in. This view
    will get all tracks on the playlist, collate the track IDs, copy the name and transfer
    those track IDs into a comma-separated list which will be persisted into the user's
    playlists.
    """
    spotify_playlist_id = playlist_id.split(':')[2]
    playlist_details = sp.playlist_tracks(playlist_id=spotify_playlist_id)
    if playlist_details is None:
        # If the details are invalid, signal an error message and route the user to the import spotify
        # view.
        messages.error(request=request, message="A playlist does not exist by that ID!")
        return import_spotify(request=request)
    print(playlist_details)
    track_ids = []
    for i in range(0, len(playlist_details['items'])):
        track_ids.append(map(lambda x: playlist_details['items'][i]['external_urls']))
    messages.success(request=request, message=f'You have successfully imported the playlist.')
    return user_profile(request=request)


def import_spotify(request):
    """Allows the user to import playlists from Spotify. First, if a user is authenticated
    via Spotify oAuth, lists the user's playlist using the Get Current User's Playlists
    API call. Then, aggregates this data into a list containing fields for the title,
    the Playlist image, and the track IDs.
    """
    playlists = sp.user_playlists('spotify')
    available_playlists = []
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            # print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
            print(str(playlist) + '\n')
            available_playlists.append({
                'name': playlist['name'],
                'uri': playlist['uri'],
                'thumbnail': playlist['images'][0]['url'] if ('images' in playlist and len(playlist['images']) > 0) else None,
                'tracksRef': playlist['tracks']
            })
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return render(request=request, template_name="recommender/import_spotify.html", context={
        'spotify_playlists': available_playlists
    })



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
            return redirect("recommender:landing_member")
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
    playlist_count = Playlist.objects.filter(Q(owner=request.user)).count()

    return render(request=request, template_name="recommender/user_preferences.html",
                        context={"likes": users_preferences['likes'],'dislikes': users_preferences['dislikes'],
                                 "available_genre_seeds": available_genre_seeds,
                                "playlist_count": playlist_count, "preference_form": preference_form})


@login_required
def user_account_settings(request):
    """Retrieves the user's account settings.

    """

    # Retrieves the user's post count.
    playlist_count = Playlist.objects.filter(Q(owner=request.user)).count()

    context = {
        "playlist_count": playlist_count
    }

    new_preferences = init_users_preferences(request=request, available_genre_seeds=None)

    context['friends'] = new_preferences['friends'] or 'Default'

    if request.method == "POST":
        user_friend_settings_form = UserFriendSettingsForm(data=request.POST)
        if user_friend_settings_form.is_valid():
            new_setting = user_friend_settings_form.cleaned_data['preference']
            new_preferences['friends'] = new_setting
            request.user.preferences = new_preferences
            request.user.save()
            messages.success(request=request, message=f'You have changed your recommendation preferences to: {new_setting}')
            context['form'] = user_friend_settings_form
    else:
        context['form'] = UserFriendSettingsForm()

    return render(request=request, template_name="recommender/settings.html", context=context)

def update_music_data(song):
    track_id = song['id']
    obj = MusicData.objects.all().filter(track_id=track_id)
    if len(obj) == 0:
        # create the obj and add to db
        track_name = song['name']
        track_album_id = song['album']['id']
        track_album_name = song['album']['name']

        genre_list = sp.artist(song['artists'][0]['id'])['genres']
        genres = ''
        for genre in genre_list:
            genres += genre + ','

        album_cover = song['album']['images'][0]['url']

        artist_name = ''
        artist_id = ''
        for artist in song['artists']:
            artist_name += artist['name'] + ','
            artist_id += artist['id'] + ','
        
        release_date = song['album']['release_date']
        preview_url = song['preview_url']

        song = MusicData(
            track_id = track_id,
            track_name = track_name,
            track_album_id = track_album_id,
            track_album_name = track_album_name,
            track_genre = genres,
            album_cover = album_cover,
            artist_name = artist_name,
            artist_id = artist_id,
            release_date = release_date[0:4],
            preview_url = preview_url
        )

        song.save()
        return song
    else:
        return obj[0]

'''
recommend_songs_by_genre(user, count)

Returns a list of recommended music based on the given user's preferences.
Each item in the list is a triplet containing two songs related to two liked
genres, and one song related to one disliked genre.
The number of triplets returned is specified by the count argument.

Jeremy Juckett
'''
def recommend_songs_by_genre(like_list, dislike_list, count):
    recommendations = [] # [like recommendations, dislike recommendations]

    # create 'count' recommended triplets
    for i in range(count):
        likes = []
        dislikes = []

        # loop until tracks are returned for a random liked genres.
        # This will loop forever if none of the genres return any results.
        # Not ideal
        loop = True
        while loop:
            # select a random liked genre to include in the search query
            random_index = random.randint(0, len(like_list) - 1)
            random_like_genre = like_list[random_index]
            like_search_query = 'genre:' + random_like_genre
            like_result = sp.search(q=like_search_query, limit=2, offset=random.randint(0,10), market=None)

            # If no tracks are returned, pick another random liked genre and try again.
            like_tracks = like_result['tracks']
            if like_tracks['items']:
                # Get the ID for each track and check them against the MusicData model.
                # If a track does not exits in the database, add it.
                for item in like_tracks['items']:
                    song = update_music_data(item)
                    #recommendations[0].append(song)
                    likes.append(song)
                loop = False
            else:
                print("No tracks returned for " + random_like_genre)

        loop = True
        while loop:
            # select a random liked genre to include in the search query
            random_index = random.randint(0, len(dislike_list) - 1)
            random_dislike_genre = dislike_list[random_index]
            dislike_search_query = 'genre:' + random_dislike_genre
            dislike_result = sp.search(q=dislike_search_query, limit=1, offset=random.randint(0,10), market=None)

            # If no tracks are returned, pick another random liked genre and try again.
            dislike_tracks = dislike_result['tracks']
            if dislike_tracks['items']:
                # Get the ID for each track and check them against the MusicData model.
                # If a track does not exits in the database, add it.
                song = update_music_data(dislike_tracks['items'][0])
                #recommendations[0].append(song)
                dislikes.append(song)

                loop = False
            else:
                print("No tracks returned for " + random_like_genre)

        recommendations.append({'likes': likes, 'dislikes': dislikes})        

    return recommendations


@login_required
def get_member_feed(request):
    #like_query_result = Playlist.objects.all().filter(owner=request.user, name='likes')
    #dislike_query_result = Playlist.objects.all().filter(owner=request.user, name='dislikes')
    preferences = ast.literal_eval(User.objects.get(email=request.user.email).preferences)
    likes = preferences['likes']
    dislikes = preferences['dislikes'] 

    # check if the user has likes and dislikes and get for-you data
    for_you_data = []
    if len(likes) != 0 and len(dislikes) != 0:
        # Otherwise, grab content from Spotify based on genre
        for_you_message = 'Recommended Content'
        for_you_data = recommend_songs_by_genre(likes, dislikes, 4)
    else:
        for_you_message = 'To get recommendation, customize your music preferences.'

    new_release_data = get_new_releases()

    context = {
        'for_you_message': for_you_message,
        'for_you_data': for_you_data,
        'new_release_data': new_release_data
    }

    return render(request=request, template_name='recommender/landing_member.html', context=context)

def friend_recommendation(request):
    # Get the current user.
    # Parse out their preferences using ast.literal_eval()

    user_preferences = init_users_preferences(request=request, available_genre_seeds=None)

    # Check their preferences field for one of four options to determine
    # the fit algorithm:

    # Similar
    # Opposite
    # Disparate
    # Default

    if request.method == 'POST':
        search_form = UserSearchForm(data=request.POST)
        if search_form.is_valid():
            username_query = search_form.cleaned_data['search_query']
            if username_query == "":
                recommendations = generate_friend_recommendations(request, preference=user_preferences['friends'])
                return render(request=request, template_name='recommender/friend_recommender.html', context={'memberlist': recommendations, 'form': search_form})
            results = User.objects.filter(username__contains=username_query)
            return render(request=request, template_name='recommender/friend_recommender.html', context={
                "memberlist": results,
                "form": search_form
            })
    else:
        recommendations = generate_friend_recommendations(request, preference=user_preferences['friends'])
        print(recommendations)
        search_form = UserSearchForm()

        return render(request=request, template_name='recommender/friend_recommender.html', context={'memberlist': recommendations, 'form': search_form})


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
                return redirect("recommender:landing_member")
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
    if len(like_query_result) > 0 or like_query_result[0].songs != "":
        # populate the context with music data from random liked track ids
        liked_track_ids = like_query_result[0].songs.split(",")
        liked_track_ids.remove('') # remove the empty entry at the end
        
        liked_music_data = []
        for l in liked_track_ids:
            liked_music_data.append(MusicData.objects.all().filter(track_id=l)[0])

    # fetch the dislike playlist
    if len(dislike_query_result) > 0 or dislike_query_result[0].songs != "":
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

def spotify_success(request):
    return render(request=request, template_name="recommender/spotify_success.html")

@csrf_exempt
def authenticate_spotify_user(request):
    if request.method == "POST":
        user_data = json.loads(request.body)
        username = user_data["username"]
        email = user_data["email"]
        password = user_data["password"]
        preferences = user_data["preferences"]
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user)
            messages.info(request, f"You are now logged in as {email}.")
            return redirect("recommender:landing_member")
        else:
            User.objects.create_user(email=email, username=username, password=password, preferences=preferences)
            user = User.objects.get(email=email)
            user.save()
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user)
            messages.info(request, f"You are now logged in as {email}.")
            return redirect("recommender:landing_member")
    return render(request, 'recommender/landing_spotify.html')
