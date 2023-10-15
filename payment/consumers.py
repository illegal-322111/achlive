# your_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
class CoinbaseWebsocketConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        print("WebSocket connected")
        user = self.scope['user']
        user_id = self.scope['user'].id
        
        
        
        if user.is_anonymous:
            await self.close()

        # Create a unique group for the user
        await self.channel_layer.group_add(
            f"user_{user.id}_group",
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope['user']
        # Update user's online status
        user_id = self.scope['user'].id
        
        
        await self.channel_layer.group_discard(
            f"user_{user.id}_group",
            self.channel_name
        )

    async def webhook_update(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))


