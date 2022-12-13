from django.urls import path
from .views import CreateThread, ListThreads, ThreadView, CreateMessage
from . import views

app_name = 'recommender'

urlpatterns = [
    path('inbox/', ListThreads.as_view(), name='inbox'),
    path('inbox/create-thread', CreateThread.as_view(), name='create-thread'),
    path('inbox/<int:pk>', ThreadView.as_view(), name='thread'),
    path('inbox/<int:pk>/create-message', CreateMessage.as_view(), name='create-message'),
    path("", views.get_landing_guest, name="get_landing_guest"),
    path("profile/", views.user_profile, name="user_profile"),
    path("playlist/<int:user_id>", views.user_playlist, name="user_playlist"),
    path("preferences", views.user_preferences, name="user_preferences"),
    path("settings", views.user_account_settings, name="user_account_settings"),
    path("landing/", views.get_member_feed, name="landing_member"),
    path("spotify_success/", views.spotify_success, name="spotify_success"),
    path("spotify_success/landing_spotify/", views.authenticate_spotify_user, name="landing_spotify"),
    path("l_room/<str:room_name>/", views.l_room, name="l_room"),
    path("login/", views.get_login, name="get_login"),
    path("register/", views.get_register, name="get_register"),
    path("logout/", views.get_logout, name="get_logout"),
]
