from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.contrib.auth.models import Group
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from .models import Usuario, Especialista, Servicio, EspecialistaServicio, Reserva, Notificacion, InformacionNegocio, HorarioTrabajo
from .serializers import UsuarioSerializer, GroupSerializer, EspecialistaSerializer, ServicioSerializer, EspecialistaServicioSerializer, ReservaSerializer, NotificacionSerializer, InformacionNegocioSerializer, HorarioTrabajoSerializer
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta, date
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from django.utils.timezone import now
from django.db.models import Q

import re
import locale

class GroupViewSet(ReadOnlyModelViewSet): 
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class UsuarioViewSet(ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [DjangoModelPermissions]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        
        email = data.get('email')
        data['username'] = email
        data['password'] = make_password(data['password'])

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()

        try:
            nombre_grupo = data.get('rol')  

            if not nombre_grupo:
                
                grupo_cliente = Group.objects.get(name="Cliente")
                usuario.groups.add(grupo_cliente)

            elif nombre_grupo.capitalize() == "Administrador":
                grupo_admin = Group.objects.get(name="Administrador")
                usuario.groups.add(grupo_admin)
                usuario.is_staff = True
                usuario.save()

            elif nombre_grupo.capitalize() == "Cliente":
                grupo_cliente = Group.objects.get(name="Cliente")
                usuario.groups.add(grupo_cliente)

            else:
                return Response({'error': f'El grupo "{nombre_grupo}" no es válido'}, status=400)

        except Group.DoesNotExist:
            return Response({'error': 'El grupo especificado no existe'}, status=400)

        return Response({
            'message': 'Usuario creado correctamente',
            'usuario': {
                'id': usuario.id,
                'Email': usuario.email,
                'Nombre': usuario.first_name,
                'Apellido': usuario.last_name,
                'Telefono': usuario.telefono,
                'Direccion': usuario.direccion,
            }
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        usuario_actual = request.user

        # Validar si el usuario actual es cliente
        es_cliente = usuario_actual.groups.filter(name="Cliente").exists()
        es_admin = usuario_actual.groups.filter(name="Administrador").exists()

        # Si es cliente, solo puede editarse a sí mismo
        if es_cliente and usuario_actual.id != instance.id:
            return Response({'error': 'No tienes permiso para editar a otros usuarios.'}, status=403)

        # Si cambia el correo, actualiza también el username
        nuevo_email = data.get('email')
        if nuevo_email:
            data['username'] = nuevo_email

        # Si es cliente, no puede cambiar el rol
        if es_cliente and 'rol' in data:
            data.pop('rol')

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()

        # Si el usuario actual es admin y desea cambiar el rol
        if es_admin and 'rol' in data:
            nuevo_rol = data['rol']
            try:
                grupo = Group.objects.get(name=nuevo_rol)
                usuario.groups.clear()
                usuario.groups.add(grupo)

                if nuevo_rol == "Administrador":
                    usuario.is_staff = True
                else:
                    usuario.is_staff = False

                usuario.save()

            except Group.DoesNotExist:
                return Response({'error': f'El grupo "{nuevo_rol}" no existe'}, status=400)

        return Response({
            'message': 'Usuario actualizado correctamente',
            'usuario': {
                'id': usuario.id,
                'Email': usuario.email,
                'Nombre': usuario.first_name,
                'Apellido': usuario.last_name,
                'Telefono': usuario.telefono,
                'Direccion': usuario.direccion,
            }
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user
    return Response({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'telefono': user.telefono,
        'direccion': user.direccion,
        'is_staff': user.is_staff,
        'groups': [group.name for group in user.groups.all()]
    })

class EspecialistaViewSet(ModelViewSet):
    queryset = Especialista.objects.all()
    serializer_class = EspecialistaSerializer

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'error': 'No tienes permiso para actualizar especialistas.'}, status=403)
        return super().update(request, *args, **kwargs)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_specialist_status(request, pk, set_active):
    if not request.user.is_staff:
        return Response({'error': 'No tienes permiso para realizar esta acción'}, status=status.HTTP_403_FORBIDDEN)

    try:
        especialista = Especialista.objects.get(pk=pk)
    except Especialista.DoesNotExist:
        return Response({'error': 'Especialista no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if set_active not in [0, 1]:
        return Response({'error': 'El valor debe ser 1 (activo) o 0 (inactivo)'}, status=status.HTTP_400_BAD_REQUEST)

    especialista.activo = bool(set_active)
    especialista.save()
    return Response({'message': f'Especialista {"activado" if especialista.activo else "desactivado"} correctamente'})

class ServicioViewSet(ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'error': 'No tienes permiso para actualizar servicios.'}, status=403)
        return super().update(request, *args, **kwargs)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_service_status(request, pk, set_active):
    if not request.user.is_staff:
        return Response({'error': 'No tienes permiso para realizar esta acción'}, status=status.HTTP_403_FORBIDDEN)

    try:
        servicio = Servicio.objects.get(pk=pk)
    except Servicio.DoesNotExist:
        return Response({'error': 'Servicio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if set_active not in [0, 1]:
        return Response({'error': 'El valor debe ser 1 (activo) o 0 (inactivo)'}, status=status.HTTP_400_BAD_REQUEST)

    servicio.activo = bool(set_active)
    servicio.save()
    return Response({'message': f'Servicio {"activado" if servicio.activo else "desactivado"} correctamente'})

class EspecialistaServicioViewSet(ModelViewSet):
    queryset = EspecialistaServicio.objects.all()
    serializer_class = EspecialistaServicioSerializer
    permission_classes = [DjangoModelPermissions]

    def create(self, request, *args, **kwargs):
        servicios_ids = request.data.pop('servicios', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        especialista = serializer.save()

        # Crear relaciones con servicios
        for servicio_id in servicios_ids:
            try:
                servicio = Servicio.objects.get(id=servicio_id)
                EspecialistaServicio.objects.create(especialista_id=especialista, servicio_id=servicio)
            except Servicio.DoesNotExist:
                continue  # O puedes retornar un error

        return Response({
            'message': 'Especialista creado con servicios asociados',
            'especialista_id': especialista.id
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        servicios_ids = request.data.pop('servicios', None)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        especialista = serializer.save()

        # Si se especificaron servicios, actualizamos las asociaciones
        if servicios_ids is not None:
            # Eliminamos las relaciones actuales
            EspecialistaServicio.objects.filter(especialista_id=especialista).delete()

            # Creamos nuevas relaciones
            for servicio_id in servicios_ids:
                try:
                    servicio = Servicio.objects.get(id=servicio_id)
                    EspecialistaServicio.objects.create(especialista_id=especialista, servicio_id=servicio)
                except Servicio.DoesNotExist:
                    continue  # o return error si quieres ser más estricto

        return Response({
            'message': 'Especialista actualizado correctamente',
            'especialista_id': especialista.id
        }, status=status.HTTP_200_OK)

class ReservaViewSet(ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [DjangoModelPermissions]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
            
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        especialista_id = data.get('especialista_id')
        fecha = data.get('fecha')
        hora_str = data.get('hora')
        servicio_id = data.get('servicio_id')
        clientEmail = data.get('clientEmail')  

        if not (especialista_id and servicio_id and fecha and hora_str and clientEmail):
            return Response({'error': 'Todos los campos son obligatorios.'}, status=400)

        data['clientEmail'] = clientEmail  

        try:
            servicio = Servicio.objects.get(id=servicio_id)
        except Servicio.DoesNotExist:
            return Response({'error': 'Servicio no válido'}, status=400)
        
        try:
            hora_inicio_nueva = datetime.strptime(hora_str, "%H:%M:%S")
        except ValueError:
            return Response({'error': 'Formato de hora inválido. Usa HH:MM:SS'}, status=400)
        
        especialista = Especialista.objects.get(id=especialista_id)
        if not especialista.activo or not servicio.activo:
            return Response({'error': 'Especialista o Servicio no se encuentran activos'}, status=400)

        duracion_servicio = servicio.duracion_estimada
        hora_fin_nueva = hora_inicio_nueva + timedelta(minutes=duracion_servicio)

        reservas_existentes = Reserva.objects.filter(
            especialista_id=especialista_id,
            fecha=fecha
        )

        for reserva in reservas_existentes:
            hora_inicio_existente = datetime.strptime(str(reserva.hora), "%H:%M:%S")
            duracion_existente = reserva.servicio_id.duracion_estimada
            hora_fin_existente = hora_inicio_existente + timedelta(minutes=duracion_existente)

            if hora_inicio_nueva < hora_fin_existente and hora_fin_nueva > hora_inicio_existente:
                return Response({'error': 'El especialista ya tiene una reserva en ese intervalo de tiempo'}, status=400)

        codigo = get_random_string(length=6)
        while Reserva.objects.filter(codigo_reserva=codigo).exists():
            codigo = get_random_string(length=6)
        data['codigo_reserva'] = codigo.upper()

        # No asociar usuario autenticado
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        reserva = serializer.save(usuario_id=None)

        enviar_correo(reserva, 'emails/booking_template.html', request)

        return Response({
            'message': 'Reserva creada exitosamente',
            'reserva': {
                'id': reserva.id,
                'fecha': reserva.fecha,
                'hora': reserva.hora,
                'estado': reserva.estado,
                'codigo_reserva': reserva.codigo_reserva,
                'clientEmail': reserva.clientEmail,
                'especialista_id': reserva.especialista_id.id,
                'servicio_id': reserva.servicio_id.id
            }
        }, status=status.HTTP_201_CREATED)

def enviar_correo(reserva, template, request):

    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    week_day = reserva.fecha.strftime('%A').lower()

    # Obtener correo del destinatario
    mailto = (
        reserva.usuario_id.email
        if reserva.usuario_id and reserva.usuario_id.email
        else request.data.get('clientEmail')
    )

    try:
        subject = f'Confirmación de Reserva N° {reserva.codigo_reserva}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [mailto]
        context = {
            'usuario': str(reserva.usuario_id) if reserva.usuario_id else request.data.get('clientName'),
            'especialista': str(reserva.especialista_id) if reserva.especialista_id else '',
            'servicio': str(reserva.servicio_id.nombre) if reserva.servicio_id and reserva.servicio_id.nombre else '',
            'fecha': str(reserva.fecha) if reserva.fecha else '',
            'hora': str(reserva.hora) if reserva.hora else '',
            'codigo_reserva': str(reserva.codigo_reserva) if reserva.codigo_reserva else '',
            'dia_semana': str(week_day) if week_day else '',
        }

        html_content = render_to_string(template, context)

        message = EmailMultiAlternatives(
            subject=subject,
            body='',
            from_email=from_email,
            to=to_email
        )
        message.attach_alternative(html_content, 'text/html')
        message.send()

    except Exception as e:
        return Response({'error': f'Error al enviar el correo: {str(e)}'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_reserva_por_codigo(request, codigo_reserva):
    try:
        if re.match(r"[^@]+@[^@]+\.[^@]+", codigo_reserva):
            fecha_actual = now().date()
            hora_actual = now().time()

            reserva = (
                Reserva.objects
                .filter(
                    clientEmail=codigo_reserva,
                    estado__in=["pendiente", "confirmada"]
                )
                .filter(
                    Q(fecha__gt=fecha_actual) |
                    Q(fecha=fecha_actual, hora__gte=hora_actual)
                ).order_by("fecha", "hora").first()
            )
        else:
            reserva = Reserva.objects.filter(
                codigo_reserva=codigo_reserva,
                estado__in=["pendiente", "confirmada"]
            ).first()
        if not reserva:
            return Response({'error': 'La reserva no existe o ya no se encuentra disponible'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReservaSerializer(reserva)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Reserva.DoesNotExist:
        return Response({'error': 'Ha ocurrido un error al obtener la reserva.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([AllowAny])
def actualizar_reserva(request, pk, estado):
    try:
        reserva = Reserva.objects.get(pk=pk)
    except Reserva.DoesNotExist:
        return Response({'error': 'Reserva no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    reserva.estado = estado
    reserva.save()

    if reserva.estado == "confirmada":
        enviar_correo(reserva, 'emails/booking_confirmed_template.html', request)
        return Response({'message': 'Su cita ha sido confirmada con éxito.'}, status=status.HTTP_200_OK)
    elif reserva.estado == "cancelada":
        return Response({'message': 'Su cita ha sido cancelada con éxito.'}, status=status.HTTP_200_OK)

    return Response({'message': 'Reserva actualizada exitosamente'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def horarios_disponibles(request):
    fecha_str = request.data.get("fecha")
    especialista_id = request.data.get("especialista_id")
    servicio_id = request.data.get("servicio_id")

    if not (fecha_str and especialista_id and servicio_id):
        return Response({"error": "Todos los campos son requeridos."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Fecha inválida, formato requerido: YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

    # Validar fecha en el pasado
    if fecha < date.today():
        return Response({"error": "No se puede consultar horarios para una fecha pasada."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        servicio = Servicio.objects.get(id=servicio_id)
    except Servicio.DoesNotExist:
        return Response({"error": "Servicio no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    DIAS_SEMANA = {
        0: "LU",
        1: "MA",
        2: "MI",
        3: "JU",
        4: "VI",
        5: "SA",
        6: "DO",
    }
    
    duracion = servicio.duracion_estimada
    dia_semana = DIAS_SEMANA[fecha.weekday()]

    try:
        horario = HorarioTrabajo.objects.get(dia=dia_semana, activo=True)
    except HorarioTrabajo.DoesNotExist:
        return Response({"error": "No hay horario de trabajo configurado para este día."}, status=status.HTTP_404_NOT_FOUND)

    hora_inicio = datetime.combine(fecha, horario.hora_inicio)
    hora_fin = datetime.combine(fecha, horario.hora_fin)

    reservas = Reserva.objects.filter(
        especialista_id=especialista_id,
        fecha=fecha
    )

    horas_ocupadas = []
    for reserva in reservas:
        duracion_reserva = reserva.servicio_id.duracion_estimada
        hora_inicio_reserva = datetime.combine(fecha, reserva.hora)
        hora_fin_reserva = hora_inicio_reserva + timedelta(minutes=duracion_reserva)
        horas_ocupadas.append((hora_inicio_reserva, hora_fin_reserva))

    horarios_disponibles = []
    hora_actual = hora_inicio
    while hora_actual + timedelta(minutes=duracion) <= hora_fin:
        fin_actual = hora_actual + timedelta(minutes=duracion)

        conflicto = any(
            inicio < fin_actual and hora_actual < fin
            for inicio, fin in horas_ocupadas
        )

        if not conflicto:
            horarios_disponibles.append(hora_actual.time().strftime("%H:%M:%S"))

        hora_actual += timedelta(minutes=duracion)

    return Response(horarios_disponibles, status=status.HTTP_200_OK)


class NotificacionViewSet(ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [DjangoModelPermissions]

class InformacionNegocioViewSet(ModelViewSet):
    queryset = InformacionNegocio.objects.all()
    serializer_class = InformacionNegocioSerializer
    permission_classes = [DjangoModelPermissions]

class HorarioTrabajoViewSet(ModelViewSet):
    queryset = HorarioTrabajo.objects.all()
    serializer_class = HorarioTrabajoSerializer
    permission_classes = [DjangoModelPermissions]