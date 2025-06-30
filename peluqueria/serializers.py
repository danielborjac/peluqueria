from rest_framework import serializers
from .models import (
    Usuario,
    Especialista,
    Servicio,
    EspecialistaServicio,
    Reserva,
    Notificacion,
    InformacionNegocio,
    HorarioTrabajo,
)
from django.contrib.auth.models import Group


class UsuarioSerializer(serializers.ModelSerializer):
    rol = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = "__all__"


class EspecialistaSerializer(serializers.ModelSerializer):
    servicios = serializers.ListField(
        write_only=True, child=serializers.IntegerField(), required=False
    )
    servicios_asociados = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Especialista
        fields = [
            "id",
            "nombre",
            "apellido",
            "especialidad",
            "foto_url",
            "descripcion",
            "activo",
            "servicios",
            "servicios_asociados",
        ]

    def create(self, validated_data):
        servicios_ids = validated_data.pop("servicios", [])
        especialista = Especialista.objects.create(**validated_data)

        for servicio_id in servicios_ids:
            try:
                servicio = Servicio.objects.get(id=servicio_id)
                EspecialistaServicio.objects.create(
                    especialista_id=especialista, servicio_id=servicio
                )
            except Servicio.DoesNotExist:
                continue

        return especialista
    
    def update(self, instance, validated_data):
        # Si no se envía 'servicios', asumimos que quiere eliminar todos
        servicios_ids = validated_data.pop('servicios', [])

        # Actualiza los campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Eliminar TODAS las relaciones existentes
        EspecialistaServicio.objects.filter(especialista_id=instance).delete()

        # Crear nuevas relaciones solo si hay servicios
        for servicio_id in servicios_ids:
            try:
                servicio = Servicio.objects.get(id=servicio_id)
                EspecialistaServicio.objects.create(especialista_id=instance, servicio_id=servicio)
            except Servicio.DoesNotExist:
                continue

        return instance


    def get_servicios_asociados(self, obj):
        servicios = Servicio.objects.filter(
            especialistaservicio__especialista_id=obj.id
        )
        return [
            {
                "id": servicio.id,
                "nombre": servicio.nombre,
                "precio": servicio.precio,
                "duracion_estimada": servicio.duracion_estimada,
            }
            for servicio in servicios
        ]


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = "__all__"


class EspecialistaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecialistaServicio
        fields = "__all__"


class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = "__all__"


class InformacionNegocioSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacionNegocio
        fields = "__all__"


class HorarioTrabajoSerializer(serializers.ModelSerializer):
    dia_display = serializers.CharField(source="get_dia_display", read_only=True)

    class Meta:
        model = HorarioTrabajo
        fields = "__all__"
