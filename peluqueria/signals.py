# peluqueria/signals.py

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

@receiver(post_migrate)
def crear_grupos_y_permisos(sender, **kwargs):
    # Crear grupos si no existen
    admin_group, _ = Group.objects.get_or_create(name="Administrador")
    cliente_group, _ = Group.objects.get_or_create(name="Cliente")

    # Modelos para permisos del administrador
    modelos_admin = [
        'Usuario',
        'Especialista',
        'Servicio',
        'EspecialistaServicio',
        'Reserva',
        'Notificacion',
        'InformacionNegocio',
        'HorarioTrabajo'
    ]

    permisos_para_admin = []

    for nombre_modelo in modelos_admin:
        Modelo = apps.get_model('peluqueria', nombre_modelo)
        content_type = ContentType.objects.get_for_model(Modelo)
        permisos = Permission.objects.filter(content_type=content_type)
        permisos_para_admin.extend(permisos)

    admin_group.permissions.set(permisos_para_admin)

    # Permisos del cliente: puede cambiar su perfil y gestionar sus reservas
    permisos_cliente = []

    # Permiso para editar su perfil
    Usuario = apps.get_model('peluqueria', 'Usuario')
    ct_usuario = ContentType.objects.get_for_model(Usuario)
    permiso_editar_usuario = Permission.objects.filter(
        codename='change_usuario',
        content_type=ct_usuario
    ).first()
    if permiso_editar_usuario:
        permisos_cliente.append(permiso_editar_usuario)

    # Permisos para crear y editar reservas
    Reserva = apps.get_model('peluqueria', 'Reserva')
    ct_reserva = ContentType.objects.get_for_model(Reserva)
    permiso_add_reserva = Permission.objects.filter(
        codename='add_reserva',
        content_type=ct_reserva
    ).first()
    permiso_change_reserva = Permission.objects.filter(
        codename='change_reserva',
        content_type=ct_reserva
    ).first()

    for p in [permiso_add_reserva, permiso_change_reserva]:
        if p:
            permisos_cliente.append(p)

    cliente_group.permissions.set(permisos_cliente)

