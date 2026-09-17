import json
from channels.generic.websocket import AsyncWebsocketConsumer

class IntelligenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'intelligence_feed'
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
        pass # We only push from server to client

    async def new_threat(self, event):
        report = event['report']
        await self.send(text_data=json.dumps({
            'type': 'NEW_THREAT',
            'report': report
        }))