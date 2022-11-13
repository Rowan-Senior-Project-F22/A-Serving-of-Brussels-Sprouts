from django.contrib import admin
from .models import ThreadModel

# Register your models here.
admin.site.register(ThreadModel)
from .models import User, ListeningRoom, Post, Playlist

# Register your models here.
admin.site.register(ListeningRoom)
admin.site.register(Post)
admin.site.register(Playlist)

# Registering the custom user model.
admin.site.register(User)
