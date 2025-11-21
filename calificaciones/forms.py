from django import forms
from .models import Calificacion

class CalificacionForm(forms.ModelForm):

    class Meta:
        model = Calificacion
        fields = ['monto', 'factor', 'estado']

        labels = {
            'monto': 'Monto (CLP)',
            'factor': 'Factor de Multiplicación',
            'estado': 'Estado de Validación',
        }

        widgets = {
        'monto': forms.NumberInput(attrs={'step': '1'}),
        'factor': forms.NumberInput(attrs={'step': '1'}),   # <--- aquí sin decimales
        }

        help_texts = {
            'monto': 'Ingrese el monto en pesos chilenos (CLP).',
            'factor': 'Ingrese el factor de multiplicación (por ejemplo, 1.00).',
            'estado': 'Seleccione el estado de la calificación.',
        }