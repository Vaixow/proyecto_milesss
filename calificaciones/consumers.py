import json
from channels.generic.websocket import AsyncWebsocketConsumer


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

        message = data.get("message", "")
        mode = data.get("mode", "global")
        target = data.get("target")

        if not message.strip():
            return

        # ✅ ✅ ✅ PRIVADO (SE ENVÍA A AMBOS: EMISOR + RECEPTOR)
        if mode == "private" and target:

            payload = {
                "type": "chat_message",
                "message": message,
                "user": self.user.username,
                "mode": "private",
                "target": target,
            }

            # 👉 Receptor
            await self.channel_layer.group_send(f"user_{target}", payload)

            # 👉 Emisor (para que se vea a sí mismo)
            await self.channel_layer.group_send(f"user_{self.user.username}", payload)

        # ✅ ✅ ✅ GLOBAL
        else:
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
