# streamer/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.stream_id = self.scope['url_route']['kwargs']['stream_id']
        self.group_name = f"stream_{self.stream_id}"

        # Join the group associated with the stream ID
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print(f"WebSocket connected for stream_id: {self.stream_id}")

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected for stream_id: {self.stream_id}, code: {close_code}")

    async def stream_frame(self, event):
        frame = event['frame']
        await self.send(text_data=json.dumps({'frame': frame}))