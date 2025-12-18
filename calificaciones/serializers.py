from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import ArchivoMasivo, Auditoria, Calificacion, ChatMessage

class ChatMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            "user",
            "target",
            "message",
            "mode",
            "timestamp",
        ]

class CalificacionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Calificacion
        fields = [
            "url",
            "id",
            "usuario",
            "monto",
            "tipo_movimiento",
            "estado",
            "fecha_registro",
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            "url",
            "id",
            "username",
            "email",
            "is_staff",
            "is_active",
            "groups",
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = [
            "url",
            "id",
            "name"
        ]


class ArchivoMasivoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ArchivoMasivo
        fields = [
            "url",
            "id",
            "nombre_archivo",
            "fecha_carga",
            "usuario",
        ]


class AuditoriaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Auditoria
        fields = [
            "url",
            "id",
            "usuario",
            "accion",
            "fecha",
            "detalle",
        ]