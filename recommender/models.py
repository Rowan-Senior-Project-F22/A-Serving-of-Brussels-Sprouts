from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


'''Custom User Model
- Brandon Ngo'''


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to="profile/")
    # direct_messages = models.ManyToManyField('DirectMessage') TODO: Update with Design Team 3
    preferences = models.CharField(null=False, default='{}', max_length=1000)

    following = models.ForeignKey('self', on_delete=models.CASCADE)

    # USERNAME_FIELD = 'email'
    # required_fields = []

    def __str__(self):
        return self.email


'''Post model designed for the post feed
- Brandon Ngo'''


class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    song = models.IntegerField()
    body = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)


'''Playlist model to store a user's playlists
- Brandon Ngo'''


class Playlist(models.Model):
    songs = models.CharField(null=False, default='[]', max_length=100)
    is_public = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')


'''Listening room model, contains multiple listeners and the currently playing song
- Brandon Ngo'''


class ListeningRoom(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    listeners = models.ManyToManyField(User)
    currently_playing = models.IntegerField()
    genre = models.CharField(max_length=150)



'''DM pages
-Thread model- Shows a list of people you have messages with
-Message model- Is how people send and recieve messages
-Wasiu Biobaku'''
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