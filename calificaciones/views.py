# calificaciones/views.py
import csv
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db.models import Q

from rest_framework import permissions, viewsets

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import openpyxl

from .models import (
    Calificacion,
    ArchivoMasivo,
    Auditoria,
    ChatMessage
)

from .forms import CalificacionForm, ArchivoMasivoForm
from .serializers import (
    GroupSerializer,
    UserSerializer,
    CalificacionSerializer,
    AuditoriaSerializer,
    ArchivoMasivoSerializer,
    ChatMessageSerializer
)

# =========================
# API REST
# =========================

class CalificacionViewSet(viewsets.ModelViewSet):
    queryset = Calificacion.objects.all().order_by("id")
    serializer_class = CalificacionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().order_by("timestamp")
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]


class ArchivoMasivoViewSet(viewsets.ModelViewSet):
    queryset = ArchivoMasivo.objects.all().order_by("-fecha_carga")
    serializer_class = ArchivoMasivoSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuditoriaViewSet(viewsets.ModelViewSet):
    queryset = Auditoria.objects.all().order_by("-fecha")
    serializer_class = AuditoriaSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

# =========================
# DASHBOARD
# =========================

@login_required
def dashboard_view(request):
    query = request.GET.get("q")
    orden = request.GET.get("orden", "id")

    calificaciones_qs = Calificacion.objects.all()

    if query:
        filtros = Q(usuario__username__icontains=query)
        if query.isdigit():
            filtros |= Q(id=int(query))
        calificaciones_qs = calificaciones_qs.filter(filtros)

    ordenes_validos = [
        "id", "-id",
        "monto", "-monto",
        "fecha_registro", "-fecha_registro",
        "estado"
    ]

    if orden not in ordenes_validos:
        orden = "id"

    listado_calificaciones = calificaciones_qs.order_by(orden)

    context = {
        "listado_calificaciones": listado_calificaciones,
        "total_calificaciones": calificaciones_qs.count(),
        "usuario": request.user,
        "pendientes_validacion": Calificacion.objects.filter(estado="pendiente").count(),
        "cargas_recientes": ArchivoMasivo.objects.filter(
            fecha_carga__gte=timezone.now() - datetime.timedelta(hours=24)
        ).count(),
        "errores_simulados": 0,
        "users": User.objects.exclude(username=request.user.username),
    }

    return render(request, "calificaciones/dashboard.html", context)

# =========================
# CRUD
# =========================

@login_required
def crear_calificacion(request):
    if request.method == "POST":
        form = CalificacionForm(request.POST)
        if form.is_valid():
            cal = form.save(commit=False)
            cal.usuario = request.user
            cal.save()

            Auditoria.objects.create(
                usuario=request.user,
                accion="CREAR",
                detalle=f"Calificación ID {cal.id} creada."
            )
            return redirect("dashboard")
    else:
        form = CalificacionForm()

    return render(request, "calificaciones/calificacion_form.html", {
        "form": form,
        "titulo": "Nueva Calificación"
    })


@login_required
def ver_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    auditoria = Auditoria.objects.filter(
        detalle__icontains=f"ID {pk}"
    ).order_by("-fecha")[:5]

    return render(request, "calificaciones/calificacion_detalle.html", {
        "calificacion": calificacion,
        "registros_auditoria": auditoria
    })


@login_required
def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)

    if request.method == "POST":
        form = CalificacionForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()
            Auditoria.objects.create(
                usuario=request.user,
                accion="EDITAR",
                detalle=f"Calificación ID {pk} editada."
            )
            return redirect("dashboard")
    else:
        form = CalificacionForm(instance=calificacion)

    return render(request, "calificaciones/calificacion_form.html", {
        "form": form,
        "titulo": f"Editar Calificación {pk}"
    })


@login_required
def eliminar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)

    if request.method == "POST":
        Auditoria.objects.create(
            usuario=request.user,
            accion="ELIMINAR",
            detalle=f"Calificación ID {pk} eliminada."
        )
        calificacion.delete()
        return redirect("dashboard")

    return render(request, "calificaciones/calificacion_confirm_delete.html", {
        "calificacion": calificacion
    })

# =========================
# CHAT (HTTP)
# =========================

@login_required
def cargar_mensajes(request):
    mode = request.GET.get("mode")
    target = request.GET.get("target")

    if mode == "global":
        mensajes = ChatMessage.objects.filter(mode="global")

    elif mode == "private" and target:
        mensajes = ChatMessage.objects.filter(
            Q(user=request.user, target__username=target) |
            Q(user__username=target, target=request.user)
        )

    else:
        mensajes = ChatMessage.objects.none()

    data = [
        {"user": m.user.username, "message": m.message, "mode": m.mode}
        for m in mensajes.order_by("timestamp")
    ]

    return JsonResponse(data, safe=False)
