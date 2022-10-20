from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Musicdata(models.Model):
    track_id = models.TextField()
    track_name = models.TextField()
    track_artist = models.TextField()
    track_popularity  = models.FloatField()
    track_album_id  = models.TextField()
    track_album_name = models.TextField()
    track_album_release_date = models.IntegerField()
    playlist_name = models.TextField()
    playlist_id = models.TextField()
    playlist_genre = models.TextField()
    playlist_subgenre = models.TextField()
    danceability = models.FloatField()
    energy = models.FloatField()
    key = models.FloatField()
    loudness = models.FloatField()
    mode = models.FloatField()
    speechiness = models.FloatField()
    acousticness = models.FloatField()
    instrumentalness = models.FloatField()
    liveness = models.FloatField()
    valence = models.FloatField()
    tempo = models.FloatField()
    duration_ms  = models.IntegerField()

'''Custom User Model
- Brandon Ngo'''
class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(null=True, blank=True,upload_to="profile/")
    direct_messages = models.ManyToManyField('DirectMessage')
    preferences = models.CharField(null=False, default='{}')

    following = models.ForeignKey('self', on_delete=models.CASCADE)


    USERNAME_FIELD = 'email'
    required_fields = []

    def __str__(self):
        return self.email

'''Post model designed for the post feed
- Brandon Ngo'''
class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    song = models.ForeignKey(Musicdata)
    body = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)

'''Playlist model to store a user's playlists
- Brandon Ngo'''
class Playlist(models.Model):
    songs = models.CharField(null=False, default='[]')
    is_public = models.BooleanField(default=False)
    owner = creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')

'''Listening room model, contains multiple listeners and the currently playing song
- Brandon Ngo'''
class ListeningRoom(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    listeners = models.ManyToManyField(User, on_delete=models.CASCADE)
    currently_playing = models.ForeignKey(Musicdata, on_delete=models.CASCADE)
    genre = models.CharField()