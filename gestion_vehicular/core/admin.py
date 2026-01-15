from django.contrib import admin
# Importamos tus modelos desde models.py
from .models import (
    Universidad, Cuenta, Administrador, Conductor, 
    Docente, Estudiante, Vehiculo, Reserva, Asistencia
)

# Registramos los modelos para que aparezcan en el panel
admin.site.register(Universidad)
admin.site.register(Cuenta)
admin.site.register(Administrador)
admin.site.register(Conductor)
admin.site.register(Docente)
admin.site.register(Estudiante)
admin.site.register(Vehiculo)
admin.site.register(Reserva)
admin.site.register(Asistencia)