from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    
class ThreadModel(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = '+')
    receiver = models.ForeignKey(User, on_delete = models.CASCADE, related_name = '+')

class MessageModel(models.Model):
    thread = models.ForeignKey('ThreadModel', related_name= '+', on_delete = models.CASCADE, blank = True, null = True)
    sender_user = models.ForeignKey(User, on_delete= models.CASCADE, related_name = '+')
    reciever_user = models.ForeignKey(User, on_delete= models.CASCADE, related_name = '+')
    body = models.CharField(max_length = 1000)
    date = models.DateTimeField(default = timezone.now)
    is_read = models.BooleanField(default = False)



