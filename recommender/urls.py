from django.urls import path
from .views import CreateThread, ListThreads,ThreadView,CreateMessage
from .import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('inbox/', ListThreads.as_view(), name = 'inbox'),
    path('inbox/create-thread', CreateThread.as_view(), name= 'create-thread'),
    path('inbox/<int:pk>', ThreadView.as_view(), name = 'thread'),
    path('inbox/<int:pk>/create-message', CreateMessage.as_view(), name = 'create-message'),
    path("", views.get_landing_guest, name="get_landing_guest"),
    path("profile/<int:user_id>", views.user_profile , name="profile"),
    path("playlist/<int:user_id>", views.user_playlist, name="profile"),
    path("l_room/<str:room_name>", views.l_room, name = "l_room")
]
 