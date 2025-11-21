# calificaciones/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime

# Modelos y Formularios
from .models import Calificacion, ArchivoMasivo, Auditoria
from .forms import CalificacionForm 

# --- LISTAR (R de CRUD) / DASHBOARD ---
@login_required
def dashboard_view(request):
    # Obtener los datos más recientes
    listado_calificaciones = Calificacion.objects.all().order_by('-fecha_registro')[:10]
    total_calificaciones = Calificacion.objects.count()

    context = {
        'listado_calificaciones': listado_calificaciones,
        'total_calificaciones': total_calificaciones,
        'usuario': request.user,
        # Valores simulados, como teníamos antes
        'pendientes_validacion': Calificacion.objects.filter(estado='pendiente').count(),
        'cargas_recientes': ArchivoMasivo.objects.filter(fecha_carga__gte=timezone.now() - datetime.timedelta(hours=24)).count(),
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

    context = {'form': form, 'titulo': f'Editar Calificación C-{pk:04d}', 'calificacion_id': pk}
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