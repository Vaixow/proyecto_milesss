# calificaciones/admin.py
from django.contrib import admin
from .models import Calificacion, ArchivoMasivo, Auditoria

admin.site.register(Calificacion)
admin.site.register(ArchivoMasivo)
admin.site.register(Auditoria)
# Ahora puedes ver y gestionar estos datos en http://127.0.0.1:8000/admin