from django import forms
from .models import Calificacion


class CalificacionForm(forms.ModelForm):

    class Meta:
        model = Calificacion
        fields = ['monto', 'tipo_movimiento', 'estado']

        labels = {
            'monto': 'Monto (CLP)',
            'tipo_movimiento': 'Tipo de Movimiento',
            'estado': 'Estado de Validación',
        }

        widgets = {
            'monto': forms.NumberInput(attrs={
                'step': '1',
                'class': 'form-control',
                'placeholder': 'Ingrese monto en CLP'
            }),

            'tipo_movimiento': forms.Select(attrs={
                'class': 'form-select'
            }),

            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

        help_texts = {
            'monto': 'Ingrese el monto en pesos chilenos (CLP).',
            'tipo_movimiento': 'Seleccione si es un CARGO o un ABONO.',
            'estado': 'Seleccione el estado de la calificación.',
        }


class ArchivoMasivoForm(forms.Form):
    archivo_carga = forms.FileField(
        label='Archivo de Calificaciones (.csv o .xlsx)',
        help_text='Sube tu archivo con el listado de calificaciones.',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )   