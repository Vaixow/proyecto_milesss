# calificaciones/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

# Por simplicidad, usaremos el modelo User de Django para 'USUARIOS'
# Este modelo ya incluye ID, nombre de usuario (que puede ser el correo si se personaliza),
# contraseña y fecha de creación.
# Podemos extenderlo para añadir ROL y otros campos si es necesario, pero para la funcionalidad básica
# con el login y SuperAdmin es suficiente.

# --- CALIFICACIONES (Relacionado 1:N con USUARIOS) ---
class Calificacion(models.Model):
    # ID_CALIFICACION : NUMBER <PK> (Django lo genera automáticamente como 'id')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario",
                                related_name='calificaciones_realizadas') # ID_USUARIO : NUMBER <FK>
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto") # MONTO : NUMBER(12,2)
    factor = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Factor", default=1.00) # FACTOR : NUMBER(5,2)
    fecha_registro = models.DateField(default=timezone.now, verbose_name="Fecha de Registro") # FECHA_REGISTRO : DATE
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('validado', 'Validado'),
        ('rechazado', 'Rechazado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name="Estado") # ESTADO : VARCHAR2(20)

    def __str__(self):
        return f"Calificación #{self.id} - Monto: {self.monto} - Estado: {self.estado}"

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"


# --- ARCHIVOS_MASIVOS (Relacionado 1:N con USUARIOS) ---
class ArchivoMasivo(models.Model):
    # ID_ARCHIVO : NUMBER <PK> (Django lo genera automáticamente como 'id')
    nombre_archivo = models.CharField(max_length=255, verbose_name="Nombre del Archivo") # NOMBRE_ARCHIVO : VARCHAR2(255)
    fecha_carga = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Carga") # FECHA_CARGA : TIMESTAMP
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuario de Carga",
                                related_name='archivos_cargados') # ID_USUARIO : NUMBER <FK>
    # Simplificamos el proceso de carga por ahora, enfocándonos en el registro.

    def __str__(self):
        return self.nombre_archivo

    class Meta:
        verbose_name = "Archivo Masivo"
        verbose_name_plural = "Archivos Masivos"


# --- AUDITORIA (Relacionado 1:N con USUARIOS) ---
class Auditoria(models.Model):
    # ID_AUDITORIA : NUMBER <PK> (Django lo genera automáticamente como 'id')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuario que Ejecuta",
                                related_name='acciones_auditadas') # ID_USUARIO : NUMBER <FK>
    accion = models.CharField(max_length=100, verbose_name="Acción") # ACCION : VARCHAR2(100)
    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora") # FECHA : TIMESTAMP
    detalle = models.TextField(verbose_name="Detalle") # DETALLE : CLOB (Usamos TextField para grandes textos)

    def __str__(self):
        return f"{self.accion} por {self.usuario.username if self.usuario else 'N/A'} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-fecha']