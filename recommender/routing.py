from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/l_room/(?P<room_name>\w+)/$', consumers.L_RoomConsumer.as_asgi())
    #re_path(r'ws/l_room/$', consumers.L_RoomConsumer.as_asgi())
]