import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User

class IntelligenceConsumer(AsyncWebsocketConsumer):
    user = None

    async def connect(self):
        # 1. Extract token from URL query string: ?token=YOUR_JWT_TOKEN
        token = self.scope['url_route']['kwargs'].get('token') or self.scope['query_string'].decode().split('token=')[-1]
        
        if not token or token == 'null':
            print("❌ WebSocket connection rejected: No token provided.")
            await self.close()
            return

        # 2. Validate the JWT Token
        self.user = await self.get_user_from_token(token)
        
        if self.user is None:
            print(f"❌ WebSocket connection rejected: Invalid token.")
            await self.close()
            return

        # 3. Connect authenticated user
        self.room_group_name = 'intelligence_feed'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"✅ AUTHENTICATED USER CONNECTED: {self.user.username}")

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            # Validate token and get user
            valid_token = AccessToken(token)
            user_id = valid_token['user_id']
            return User.objects.get(id=user_id)
        except Exception:
            return None

    async def disconnect(self, close_code):
        if self.user:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"⚠️ USER DISCONNECTED: {self.user.username}")

    async def receive(self, text_data):
        pass 

    async def new_threat(self, event):
        report = event['report']
        await self.send(text_data=json.dumps({
            'type': 'NEW_THREAT',
            'report': report
        }))
