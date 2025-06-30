from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ## Campos heredados:
    # first_name
    # last_name
    # email
    # password
    # rol (en lugar de groups)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Especialista(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    foto_url = models.URLField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        especialidad = self.especialidad.capitalize() if self.especialidad else ""
        return f'{self.nombre} {self.apellido} - {especialidad}'

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_estimada = models.IntegerField(help_text="Duración en minutos")
    imagen_url = models.URLField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class EspecialistaServicio(models.Model):
    especialista_id = models.ForeignKey(Especialista, on_delete=models.CASCADE)
    servicio_id = models.ForeignKey(Servicio, on_delete=models.CASCADE)

class Reserva(models.Model):
    usuario_id = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    clientEmail = models.EmailField(null=True, blank=True)
    especialista_id = models.ForeignKey(Especialista, on_delete=models.CASCADE)
    servicio_id = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('completada', 'Completada'), ('cancelada', 'Cancelada')], default='pendiente')
    codigo_reserva = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return f"Reserva de {self.usuario_id.__str__ or self.clientEmail} con {self.especialista_id} para {self.servicio_id} en {self.fecha} a las {self.hora}"

class Notificacion(models.Model):
    usuario_id = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    por_email = models.BooleanField(default=True)
    por_sms = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación - {self.usuario_id}"

class InformacionNegocio(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

class HorarioTrabajo(models.Model):
    DIA_CHOICES = [
        ('LU', 'Lunes'),
        ('MA', 'Martes'),
        ('MI', 'Miércoles'),
        ('JU', 'Jueves'),
        ('VI', 'Viernes'),
        ('SA', 'Sábado'),
        ('DO', 'Domingo'),
    ]
    dia = models.CharField(max_length=2, choices=DIA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_dia_display()} ({self.hora_inicio} - {self.hora_fin})"