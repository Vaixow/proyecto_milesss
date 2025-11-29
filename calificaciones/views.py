# calificaciones/views.py

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

    listado_calificaciones = calificaciones_qs.order_by('id')
    total_calificaciones = calificaciones_qs.count()

    context = {
        'listado_calificaciones': listado_calificaciones,
        'total_calificaciones': total_calificaciones,
        'usuario': request.user,
        'pendientes_validacion': Calificacion.objects.filter(estado='pendiente').count(),
        'cargas_recientes': ArchivoMasivo.objects.filter(
            fecha_carga__gte=timezone.now() - datetime.timedelta(hours=24)
        ).count(),
        'errores_simulados': 0,
    }
    return render(request, 'calificaciones/dashboard.html', context)


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
