from django.urls import path
from . import views

app_name = 'recommender'

urlpatterns = [
    path('artist/', views.get_artist, name='get_artist'),
    path('album/', views.get_album, name='get_album'),
    path("register/", views.get_registration, name="get_registration"),
    path("login/", views.get_login, name="get_login"),
    path("profile/<int:user_id>", views.user_profile , name="profile"),
]
 