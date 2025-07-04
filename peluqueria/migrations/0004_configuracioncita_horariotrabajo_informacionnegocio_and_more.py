# Generated by Django 5.1.4 on 2025-04-22 02:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("peluqueria", "0003_servicio_activo"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConfiguracionCita",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "intervalo_descanso",
                    models.PositiveIntegerField(
                        help_text="Minutos de descanso entre citas"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HorarioTrabajo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "dia",
                    models.CharField(
                        choices=[
                            ("LU", "Lunes"),
                            ("MA", "Martes"),
                            ("MI", "Miércoles"),
                            ("JU", "Jueves"),
                            ("VI", "Viernes"),
                            ("SA", "Sábado"),
                            ("DO", "Domingo"),
                        ],
                        max_length=2,
                    ),
                ),
                ("hora_inicio", models.TimeField()),
                ("hora_fin", models.TimeField()),
                ("activo", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="InformacionNegocio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
                ("direccion", models.CharField(max_length=200)),
                ("telefono", models.CharField(max_length=20)),
                ("email", models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name="Notificacion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("por_email", models.BooleanField(default=True)),
                ("por_sms", models.BooleanField(default=False)),
                (
                    "usuario_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
