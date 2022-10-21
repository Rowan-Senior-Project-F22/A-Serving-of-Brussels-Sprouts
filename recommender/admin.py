from django.contrib import admin
from .models import Musicdata, User

# Register your models here.
admin.site.register(Musicdata)

# Registering the custom user model.
admin.site.register(User)