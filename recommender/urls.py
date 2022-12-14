from django.urls import path
from .views import CreateThread, ListThreads, ThreadView, CreateMessage, ThreadNotification
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'recommender'

urlpatterns = [
    path('inbox/', ListThreads.as_view(), name='inbox'),
    path('inbox/create-thread', CreateThread.as_view(), name='create-thread'),
    path('inbox/<int:pk>', ThreadView.as_view(), name='thread'),
    path('inbox/<int:pk>/create-message', CreateMessage.as_view(), name='create-message'),
    path('notification/<int:notification_pk>/thread/<int:object_pk>', ThreadNotification.as_view(), name = 'thread-notification'),
    path("", views.get_landing_guest, name="get_landing_guest"),
    path("profile/<str:user_name>", views.user_profile, name="user_profile"),
    path("playlist/<int:user_id>", views.user_playlist, name="user_playlist"),
    path("preferences", views.user_preferences, name="user_preferences"),
    path("settings", views.user_account_settings, name="user_account_settings"),
    path("landing/", views.get_member_feed, name="landing_member"),
    path("l_room/<slug:slug>/", views.l_room, name="l_room"),
    path("l_room_create/", views.l_room_create, name="l_room_create"),
    path("spotify_success/", views.spotify_success, name="spotify_success"),
    path("spotify_success/landing_spotify/", views.authenticate_spotify_user, name="landing_spotify"),
    path("login/", views.get_login, name="get_login"),
    path("register/", views.get_register, name="get_register"),
    path("logout/", views.get_logout, name="get_logout"),
    path("new_releases/", views.get_new_releases, name="new_releases"),
    path("like_song/", views.like_view, name="like_song"),
    path("recommendation", views.friend_recommendation, name="friend_recommendation"),
    path("import_spotify", views.import_spotify, name="import_spotify"),
    path("import_spotify_playlist/<str:playlist_id>", views.import_spotify_playlist, name="import_spotify_playlist") + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]
