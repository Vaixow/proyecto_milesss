import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # ⚠️ JWT NO llega al WebSocket → permitir conexión
        self.user = self.scope.get("user")

        self.username = (
            self.user.username
            if self.user and self.user.is_authenticated
            else "Anon"
        )

        self.global_group = "chat_global"
        self.private_group = f"user_{self.username}"

        await self.channel_layer.group_add(
            self.global_group,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.private_group,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.global_group,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.private_group,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        message = data.get("message")
        mode = data.get("mode", "global")
        target = data.get("to")  # ✅ COINCIDE con el frontend

        if not message:
            return

        # Guardar mensaje (si hay usuario real)
        await self.guardar_mensaje(message, mode, target)

        payload = {
            "type": "chat_message",
            "payload": {
                "user": self.username,
                "message": message,
                "mode": mode
            }
        }

        if mode == "private" and target:
            await self.channel_layer.group_send(
                f"user_{target}",
                payload
            )

            # eco al emisor
            await self.channel_layer.group_send(
                self.private_group,
                payload
            )

        else:
            await self.channel_layer.group_send(
                self.global_group,
                payload
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # =========================
    # 💾 Guardar en BD (seguro)
    # =========================
    @sync_to_async
    def guardar_mensaje(self, message, mode, target):
        if not self.user or not self.user.is_authenticated:
            return  # No guardar anónimos

        if mode == "private" and target:
            try:
                receptor = User.objects.get(username=target)
                ChatMessage.objects.create(
                    user=self.user,
                    target=receptor,
                    message=message,
                    mode="private"
                )
            except User.DoesNotExist:
                pass
        else:
            ChatMessage.objects.create(
                user=self.user,
                message=message,
                mode="global"
            )
