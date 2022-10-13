from django.urls import path
from . import views

app_name = 'recommender'

urlpatterns = [
    path('artist/', views.get_artist, name='get_artist'),
    path('album/', views.get_album, name='get_album'),
]
 