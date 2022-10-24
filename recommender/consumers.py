import json
from channels.generic.websocket import AsyncWebsocketConsumer

class L_RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'l_room'
        self.room_group_name = 'recommender_%s' % self.room_name
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
            }
        )

    async def chatroom_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
        }))
    
    pass