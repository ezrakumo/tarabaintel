import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class IntelligenceConsumer(AsyncWebsocketConsumer):
    user = None

    async def connect(self):
        # 1. Extract token from URL query string
        query_string = self.scope.get('query_string', b'').decode()
        token = None
        for part in query_string.split('&'):
            if part.startswith('token='):
                token = part.split('=')[1]
                break
        
        if not token:
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
        # ✅ FIX: Import BOTH User and AccessToken INSIDE the function
        from django.contrib.auth.models import User
        from rest_framework_simplejwt.tokens import AccessToken
        
        try:
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
