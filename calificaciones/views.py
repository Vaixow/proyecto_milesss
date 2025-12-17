# calificaciones/views.py
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Calificacion

from django.contrib.auth.models import User

from .models import ChatMessage



import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime
from .models import Calificacion, ArchivoMasivo, Auditoria
from .forms import CalificacionForm, ArchivoMasivoForm

# Modelos y Formularios
from .models import Calificacion, ArchivoMasivo, Auditoria
from .forms import CalificacionForm 

# calificaciones/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime
import csv
from django.db.models import Q # <--- ¡NUEVA IMPORTACIÓN NECESARIA!


# Modelos y Formularios
from .models import Calificacion, ArchivoMasivo, Auditoria
from .forms import CalificacionForm, ArchivoMasivoForm 


#SERIALIZERS
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from .serializers import GroupSerializer, UserSerializer, CalificacionSerializer, AuditoriaSerializer, ArchivoMasivoSerializer, ChatMessageSerializer


class CalificacionViewSet(viewsets.ModelViewSet):
    queryset = Calificacion.objects.all().order_by("id")
    serializer_class = CalificacionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.object.all()
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
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- LISTAR (R de CRUD) / DASHBOARD ---
@login_required
def dashboard_view(request):
    query = request.GET.get('q')

    calificaciones_qs = Calificacion.objects.all()

    if query:
        filters = Q(usuario__username__icontains=query)

        try:
            calificacion_id = int(query)
            filters |= Q(id=calificacion_id)
        except ValueError:
            pass

        calificaciones_qs = calificaciones_qs.filter(filters)

    # ✅ ORDENAMIENTO
    orden = request.GET.get('orden', 'id')

    ordenes_validos = [
        'id', '-id',
        'monto', '-monto',
        'fecha_registro', '-fecha_registro',
        'estado'
    ]

    if orden not in ordenes_validos:
        orden = 'id'

    listado_calificaciones = calificaciones_qs.order_by(orden)
    total_calificaciones = calificaciones_qs.count()

    # ✅ CONTADORES DEL DASHBOARD
    pendientes_validacion = Calificacion.objects.filter(estado='pendiente').count()

    cargas_recientes = ArchivoMasivo.objects.filter(
        fecha_carga__gte=timezone.now() - datetime.timedelta(hours=24)
    ).count()

    errores_simulados = 0  # Simulado

    # ✅ USUARIOS PARA EL CHAT (EXCLUYE AL ACTUAL)
    users = User.objects.exclude(username=request.user.username)

    context = {
        'listado_calificaciones': listado_calificaciones,
        'total_calificaciones': total_calificaciones,
        'usuario': request.user,
        'pendientes_validacion': pendientes_validacion,
        'cargas_recientes': cargas_recientes,
        'errores_simulados': errores_simulados,
        'users': users,  # ✅ IMPORTANTE PARA EL CHAT
        'historial_global': ChatMessage.objects.filter(mode="global").order_by("timestamp"),

    }

    return render(request, 'calificaciones/dashboard.html', context)

    query = request.GET.get('q')

    calificaciones_qs = Calificacion.objects.all()
    
    if query:
        filters = Q(usuario__username__icontains=query)
        
        try:
            calificacion_id = int(query)
            filters |= Q(id=calificacion_id)
        except ValueError:
            pass

        calificaciones_qs = calificaciones_qs.filter(filters)

    orden = request.GET.get('orden', 'id')  # por defecto ordena por ID

    # Seguridad: solo permitir estos campos
    ordenes_validos = ['id', 'monto', 'fecha_registro', 'estado', '-id', '-monto', '-fecha_registro']

    if orden not in ordenes_validos:
        orden = 'id'

    listado_calificaciones = calificaciones_qs.order_by(orden)

    total_calificaciones = calificaciones_qs.count()

    
# --- CREAR (C de CRUD) ---
@login_required
def crear_calificacion(request):
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.usuario = request.user # Asignar el usuario logueado
            calificacion.save()
            # Registrar en Auditoria (simulación simple)
            Auditoria.objects.create(
                usuario=request.user, accion='CREAR', detalle=f'Calificación ID {calificacion.id} creada manualmente.'
            )
            return redirect('dashboard')
    else:
        form = CalificacionForm()

    context = {'form': form, 'titulo': 'Nueva Calificación'}
    return render(request, 'calificaciones/calificacion_form.html', context)


# --- VER DETALLE (R de CRUD) ---
@login_required
def ver_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    context = {
        'calificacion': calificacion,
        # Obtener logs de auditoría relacionados (asumiendo que Auditoria funciona)
        'registros_auditoria': Auditoria.objects.filter(detalle__icontains=f'ID {pk}').order_by('-fecha')[:5]
    }
    return render(request, 'calificaciones/calificacion_detalle.html', context)

# --- ACTUALIZAR (U de CRUD) ---
@login_required
def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)

    if request.method == 'POST':
        form = CalificacionForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()
            Auditoria.objects.create(
                usuario=request.user, accion='EDITAR', detalle=f'Calificación ID {pk} editada. Monto: {calificacion.monto}'
            )
            return redirect('dashboard')
    else:
        form = CalificacionForm(instance=calificacion) # Precargar datos

    context = {'form': form, 'titulo': f'Editar Calificación {pk:d}', 'calificacion_id': pk}
    return render(request, 'calificaciones/calificacion_form.html', context)


# --- ELIMINAR (D de CRUD) ---
@login_required
def eliminar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)

    if request.method == 'POST':
        Auditoria.objects.create(
            usuario=request.user, accion='ELIMINAR', detalle=f'Calificación ID {pk} eliminada.'
        )
        calificacion.delete()
        return redirect('dashboard')

    context = {'calificacion': calificacion}
    return render(request, 'calificaciones/calificacion_confirm_delete.html', context)

# --- CARGA MASIVA (mejorada con validaciones y soporte CSV/XLSX) ---
@login_required
def carga_masiva_view(request):
    if request.method == 'POST':
        form = ArchivoMasivoForm(request.POST, request.FILES)

        if form.is_valid():

            archivo = request.FILES.get("archivo_carga")

            if not archivo:
                return render(request, 'calificaciones/calificacion_upload_form.html', {
                    'form': form,
                    'titulo': 'Carga Masiva',
                    'error': "Debes seleccionar un archivo."
                })

            # --- VALIDACIONES ---
            nombre = archivo.name.lower()
            extension = nombre.split(".")[-1]
            mime = archivo.content_type

            extensiones_validas = ["csv", "xlsx"]
            mimes_validos = [
                "text/csv",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ]

            if extension not in extensiones_validas:
                return render(request, 'calificaciones/calificacion_upload_form.html', {
                    'form': form,
                    'titulo': 'Carga Masiva',
                    'error': "Formato inválido. Solo se admiten CSV o XLSX."
                })

            if mime not in mimes_validos:
                return render(request, 'calificaciones/calificacion_upload_form.html', {
                    'form': form,
                    'titulo': 'Carga Masiva',
                    'error': f"El archivo no tiene formato válido ({mime})."
                })

            if archivo.size > 20 * 1024 * 1024:
                return render(request, 'calificaciones/calificacion_upload_form.html', {
                    'form': form,
                    'titulo': 'Carga Masiva',
                    'error': "El archivo supera el tamaño máximo permitido (20MB)."
                })

            # Registrar archivo cargado
            archivo_registro = ArchivoMasivo.objects.create(
                nombre_archivo=archivo.name,
                usuario=request.user
            )

            num_creados = 0

            try:
                # --- PROCESAR CSV ---
                if extension == "csv":
                    data = archivo.read().decode('utf-8').splitlines()
                    reader = csv.DictReader(data)

                    for row in reader:
                        try:
                            Calificacion.objects.create(
                                usuario=request.user,
                                monto=row.get('monto', 0),
                                tipo_movimiento=row.get('tipo_movimiento', 'abono'),
                                estado=row.get('estado', 'pendiente')
                            )
                            num_creados += 1

                        except Exception as e:
                            print(f"Error fila CSV: {e}")

                # --- PROCESAR XLSX ---
                elif extension == "xlsx":
                    import openpyxl
                    
                    wb = openpyxl.load_workbook(archivo)
                    sheet = wb.active

                    headers = [cell.value for cell in sheet[1]]

                    for row in sheet.iter_rows(min_row=2, values_only=True):
                        data = dict(zip(headers, row))

                        try:
                            Calificacion.objects.create(
                                usuario=request.user,
                                monto=data.get('monto', 0),
                                tipo_movimiento=data.get('tipo_movimiento', 'abono'),
                                estado=data.get('estado', 'pendiente')
                            )
                            num_creados += 1
                        except Exception as e:
                            print(f"Error fila XLSX: {e}")

                # Registrar auditoría
                Auditoria.objects.create(
                    usuario=request.user,
                    accion='CARGA_MASIVA',
                    detalle=f'Archivo \"{archivo.name}\" procesado con {num_creados} registros.'
                )

                return redirect('dashboard')

            except Exception as e:
                return render(request, 'calificaciones/calificacion_upload_form.html', {
                    'form': form,
                    'titulo': 'Carga Masiva',
                    'error': f"Error al procesar el archivo: {e}"
                })

    else:
        form = ArchivoMasivoForm()

    return render(request, 'calificaciones/calificacion_upload_form.html', {
        'form': form,
        'titulo': 'Carga Masiva'
    })




from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import openpyxl
import csv

# ==========================
# ✅ EXPORTAR CSV
# ==========================
@login_required
def exportar_calificaciones_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="calificaciones.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Monto', 'Tipo', 'Estado', 'Fecha', 'Usuario'])

    for cal in Calificacion.objects.all().order_by('id'):
        writer.writerow([
            cal.id,
            cal.monto,
            cal.get_tipo_movimiento_display(),
            cal.get_estado_display(),
            cal.fecha_registro,
            cal.usuario.username
        ])

    return response


# ==========================
# ✅ EXPORTAR EXCEL
# ==========================
@login_required
def exportar_calificaciones_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Calificaciones"

    ws.append(['ID', 'Monto', 'Tipo', 'Estado', 'Fecha', 'Usuario'])

    for cal in Calificacion.objects.all().order_by('id'):
        ws.append([
            cal.id,
            cal.monto,
            cal.get_tipo_movimiento_display(),
            cal.get_estado_display(),
            cal.fecha_registro.strftime("%d-%m-%Y"),
            cal.usuario.username
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="calificaciones.xlsx"'
    wb.save(response)

    return response


# ==========================
# ✅ EXPORTAR PDF
# ==========================
@login_required
def exportar_calificaciones_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="calificaciones.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica", 9)
    p.drawString(50, y, "REPORTE DE CALIFICACIONES")
    y -= 30

    for cal in Calificacion.objects.all().order_by('id'):
        linea = f"{cal.id} | {cal.monto} | {cal.get_tipo_movimiento_display()} | {cal.get_estado_display()} | {cal.fecha_registro} | {cal.usuario.username}"
        p.drawString(50, y, linea)
        y -= 15

        if y < 60:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 9)

    p.save()
    return response

from django.contrib.auth.models import User

from django.http import JsonResponse

@login_required
def cargar_mensajes(request):
    mode = request.GET.get("mode")
    target = request.GET.get("target")

    if mode == "global":
        mensajes = ChatMessage.objects.filter(mode="global").order_by("timestamp")

    elif mode == "private" and target:
        mensajes = ChatMessage.objects.filter(
            mode="private"
        ).filter(
            Q(user=request.user, target__username=target) |
            Q(user__username=target, target=request.user)
        ).order_by("timestamp")

    else:
        mensajes = []

    data = [
        {
            "user": m.user.username,
            "message": m.message,
            "mode": m.mode,
        }
        for m in mensajes
    ]

    return JsonResponse(data, safe=False)
