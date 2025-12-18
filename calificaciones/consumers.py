import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.global_group = "chat_global"
        self.private_group = f"user_{self.user.username}"

        await self.channel_layer.group_add(self.global_group, self.channel_name)
        await self.channel_layer.group_add(self.private_group, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.global_group, self.channel_name)
        await self.channel_layer.group_discard(self.private_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        message = data.get("message")
        mode = data.get("mode", "global")
        target = data.get("target")

        if not message:
            return

        await self.guardar_mensaje(message, mode, target)

        payload = {
            "type": "chat_message",
            "message": message,
            "user": self.user.username,
            "mode": mode,
            "target": target,
        }

        if mode == "private" and target:
            await self.channel_layer.group_send(f"user_{target}", payload)
            await self.channel_layer.group_send(self.private_group, payload)
        else:
            await self.channel_layer.group_send(self.global_group, payload)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def guardar_mensaje(self, message, mode, target):
        # ⬇️ IMPORTS SOLO AQUÍ, NUNCA ARRIBA NI EN LA CLASE
        from django.contrib.auth.models import User
        from .models import ChatMessage

        if mode == "private" and target:
            receptor = User.objects.get(username=target)
            ChatMessage.objects.create(
                user=self.user,
                target=receptor,
                message=message,
                mode="private"
            )
        else:
            ChatMessage.objects.create(
                user=self.user,
                message=message,
                mode="global"
            )
