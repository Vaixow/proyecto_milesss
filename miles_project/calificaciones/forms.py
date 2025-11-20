# calificaciones/forms.py
from django import forms
from .models import Calificacion

class CalificacionForm(forms.ModelForm):
    """
    Formulario para Crear y Editar calificaciones.
    Incluye 'monto', 'factor' y ahora 'estado'.
    """
    class Meta:
        model = Calificacion
        # Incluimos 'estado' para que sea editable
        fields = ['monto', 'factor', 'estado'] 
        
        # Definición de labels para una mejor visualización en el formulario
        labels = {
            'monto': 'Monto (CLP)',
            'factor': 'Factor de Multiplicación',
            'estado': 'Estado de Validación',
        }