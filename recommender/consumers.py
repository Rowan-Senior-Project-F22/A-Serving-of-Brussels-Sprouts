import datetime
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom

class L_RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['slug']
        room = ChatRoom.objects.filter(room_slug=self.scope['url_route']['kwargs']['slug'])
        self.room_group_name = 'recommender_%s' % self.room_name
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        room.isActive = True

        await self.accept()


    async def disconnect(self, close_code):
        room = ChatRoom.objects.filter(room_slug=self.scope['url_route']['kwargs']['slug'])
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        room.isActive = False

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                'username': username, 
            }
        )

    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']
        # current dateTime
        now = datetime.datetime.now()

        # convert to string
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp
        }))
    pass   