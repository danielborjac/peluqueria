from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    GroupViewSet,
    UsuarioViewSet,
    EspecialistaViewSet,
    ServicioViewSet,
    EspecialistaServicioViewSet,
    ReservaViewSet,
    obtener_reserva_por_codigo,
    NotificacionViewSet,
    InformacionNegocioViewSet,
    HorarioTrabajoViewSet,
    user_info,
    change_specialist_status,
    change_service_status,
    horarios_disponibles,
    actualizar_reserva
)

default_router = DefaultRouter()
default_router.register(r"roles", GroupViewSet, basename="rol")
default_router.register(r"usuarios", UsuarioViewSet, basename="usuario")
default_router.register(r"especialistas", EspecialistaViewSet, basename="especialista")
default_router.register(r"servicios", ServicioViewSet, basename="servicio")
default_router.register(
    r"especialistaservicio",
    EspecialistaServicioViewSet,
    basename="especialistaservicio",
)
default_router.register(r"reservas", ReservaViewSet, basename="reserva")
default_router.register(r"notificaciones", NotificacionViewSet, basename="notificacion")
default_router.register(r"informacionnegocio", InformacionNegocioViewSet, basename="informacionnegocio")
default_router.register(r"horariotrabajo", HorarioTrabajoViewSet, basename="horariotrabajo")

urlpatterns = [
    path(
        "reservas/codigo/<str:codigo_reserva>/",
        obtener_reserva_por_codigo,
        name="reserva-por-codigo",
    ),
    path("me/", user_info, name="me"),
    path('especialistas/<int:pk>/activo/<int:set_active>/', change_specialist_status, name='estadoespecialista'),
    path('servicios/<int:pk>/activo/<int:set_active>/', change_service_status, name='estadoservicio'),
    path('reservas/horarios_disponibles/', horarios_disponibles, name='horariosdisponibles'),
    path('reservas/actualizar/<int:pk>/<str:estado>/', actualizar_reserva, name='actualizarreserva'),
]

urlpatterns += default_router.urls
