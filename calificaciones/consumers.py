import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.global_group = "chat_global"
        self.private_group = f"user_{self.user.username}"

        await self.channel_layer.group_add(self.global_group, self.channel_name)
        await self.channel_layer.group_add(self.private_group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.global_group, self.channel_name)
        await self.channel_layer.group_discard(self.private_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        message = data.get("message", "").strip()
        mode = data.get("mode", "global")
        target_username = data.get("target")

        if not message:
            return

        # ✅ MENSAJE PRIVADO
        if mode == "private" and target_username:
            target_user = await sync_to_async(User.objects.get)(username=target_username)

            # ✅ GUARDAR EN BD
            await sync_to_async(ChatMessage.objects.create)(
                user=self.user,
                target=target_user,
                message=message,
                mode="private"
            )

            payload = {
                "type": "chat_message",
                "message": message,
                "user": self.user.username,
                "mode": "private",
                "target": target_username,
            }

            # ✅ EMISOR
            await self.channel_layer.group_send(f"user_{self.user.username}", payload)

            # ✅ RECEPTOR
            await self.channel_layer.group_send(f"user_{target_username}", payload)

        # ✅ MENSAJE GLOBAL
        else:
            await sync_to_async(ChatMessage.objects.create)(
                user=self.user,
                message=message,
                mode="global"
            )

            await self.channel_layer.group_send(
                self.global_group,
                {
                    "type": "chat_message",
                    "message": message,
                    "user": self.user.username,
                    "mode": "global",
                },
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
