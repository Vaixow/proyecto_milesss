from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Calificacion(models.Model):

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuario",
        related_name='calificaciones_realizadas'
    )

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Monto (CLP)"
    )

    TIPO_MOVIMIENTO_CHOICES = [
        ('abono', 'ABONO'),
        ('cargo', 'CARGO'),
        ('pago', 'PAGO'),
        ('reembolso', 'REEMBOLSO'),
    ]


    tipo_movimiento = models.CharField(
        max_length=10,
        choices=TIPO_MOVIMIENTO_CHOICES,
        default='abono',
        verbose_name="Tipo de Movimiento"
    )

    fecha_registro = models.DateField(
        default=timezone.now,
        verbose_name="Fecha de Registro"
    )

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('validado', 'Validado'),
        ('rechazado', 'Rechazado'),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado"
    )

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"

    def __str__(self):
        return f"Calificación #{self.id} - Monto: {self.monto} - Estado: {self.estado}"


class ArchivoMasivo(models.Model):

    nombre_archivo = models.CharField(
        max_length=255,
        verbose_name="Nombre del Archivo"
    )

    fecha_carga = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Carga"
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Usuario de Carga",
        related_name='archivos_cargados'
    )

    class Meta:
        verbose_name = "Archivo Masivo"
        verbose_name_plural = "Archivos Masivos"

    def __str__(self):
        return self.nombre_archivo


class Auditoria(models.Model):

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Usuario que Ejecuta",
        related_name='acciones_auditadas'
    )

    accion = models.CharField(
        max_length=100,
        verbose_name="Acción"
    )

    fecha = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha y Hora"
    )

    detalle = models.TextField(verbose_name="Detalle")

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.accion} por {self.usuario.username if self.usuario else 'N/A'} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"
