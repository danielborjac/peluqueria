from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

# lo dejo para gestionar los datos y permisos del superuser
admin.site.register(Usuario, UserAdmin)
