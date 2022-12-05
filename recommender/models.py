from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

'''Custom User Model
- Brandon Ngo'''
class User(AbstractUser):
    email = models.EmailField(_('email'), unique=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to="profile/")
    # direct_messages = models.ManyToManyField('DirectMessage') TODO: Update with Design Team 3
    preferences = models.CharField(null=False, default='{}', max_length=1000)
    following = models.ForeignKey('self', null=True, on_delete=models.CASCADE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class ThreadModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')

class MessageModel(models.Model):
    thread = models.ForeignKey('ThreadModel', related_name='+', on_delete=models.CASCADE, blank=True, null=True)
    sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    receiver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    body = models.CharField(max_length=1000)
    date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

'''
Data model for a song.
'''
class MusicData(models.Model):
    track_id = models.TextField()
    track_name = models.TextField()
    track_album_id  = models.TextField()
    track_album_name = models.TextField()
    track_genre = models.TextField(default='')
    album_cover = models.TextField()
    artist_name = models.TextField()
    release_date = models.TextField()
    preview_url = models.TextField(null=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

class Notification(models.Model):
    notification_type = models.IntegerField()
    to_user = models.ForeignKey(User, related_name = 'notification_to', on_delete = models.CASCADE, null = True)
    from_user = models.ForeignKey(User, related_name = 'notification_from', on_delete = models.CASCADE, null = True)
    thread = models.ForeignKey('ThreadModel', on_delete = models.CASCADE, related_name = '+', blank = True, null = True)
    date = models.DateTimeField(default = timezone.now)
    user_has_seen = models.BooleanField(default = False)


'''
Post model designed for the post feed.
- Brandon Ngo
'''
class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', default=None)
    music = models.ForeignKey(MusicData, on_delete=models.CASCADE, default=None)
    body = models.CharField(max_length=1000, default="")
    image = models.ImageField(upload_to='', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)

'''
Keeps track of which users have liked/disliked which songs.
This model has the following fields:

    user - the user engaged in a like/dislike relationship with the song.
    post - the Post object with the ID of the song in the like/dislike relationship.
    value - 1 if the user likes the Post, 2 if the user dislikes the Post.

Jeremy Juckett
'''
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.IntegerField()

    def __str__(self):
        return str(self.user) + ', ' + str(self.post) + ', ' + str(self.value)
    
    class Meta:
        unique_together = ("user", "post", "value")

'''Playlist model to store a user's playlists
- Brandon Ngo'''
class Playlist(models.Model):
    name = models.TextField(default="")
    songs = models.CharField(null=False, default='', max_length=100)
    is_public = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    #creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')


'''Listening room model, contains multiple listeners and the currently playing song
- Brandon Ngo'''
class ListeningRoom(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    listeners = models.ManyToManyField(User)
    currently_playing = models.IntegerField()
    genre = models.CharField(max_length=150)

class ChatRoom(models.Model):
    room_name = models.CharField(max_length=25)
    room_slug = models.SlugField(unique=True)
