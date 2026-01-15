from django.db import models
from django.utils import timezone

# --- ENUMERACIONES (CHOICES) ---
# Representan las cajas con <<enumeration>> en tu diagrama

class TipoVehiculo(models.TextChoices):
    CAMIONETA = 'CAMIONETA', 'Camioneta'
    BUS = 'BUS', 'Bus'
    BUSETA = 'BUSETA', 'Buseta'
    CARRO = 'CARRO', 'Carro'

class EstadoReserva(models.TextChoices):
    ANULADA = 'ANULADA', 'Anulada'
    ESPERA_ACEPTACION = 'ESPERA', 'Espera Aceptación'
    ACEPTADA = 'ACEPTADA', 'Aceptada'
    RECHAZADA = 'RECHAZADA', 'Rechazada' 

class Facultad(models.TextChoices):
    # Puedes agregar más facultades aquí
    RECURSOS_NO_RENOVABLES = 'RNR', 'Recursos No Renovables y Energía'
    OTRA = 'OTRA', 'Otra Facultad'

# --- CLASES PRINCIPALES ---

class Universidad(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)

    def getInfoContacto(self):
        return f"{self.nombre} - {self.telefono}"

    def __str__(self):
        return self.nombre

class Cuenta(models.Model):
    """
    Representa la clase 'Cuenta'.
    Nota: En un entorno real, se recomienda usar el sistema de autenticación
    de Django (User/AbstractUser), pero aquí seguimos tu diagrama.
    """
    correo = models.EmailField(unique=True)
    clave = models.CharField(max_length=128)
    activo = models.BooleanField(default=True)

    def iniciarSesion(self, correo, clave):
        # Lógica de autenticación aquí
        pass

    def recuperarContrasena(self):
        pass

    def cambiarClave(self, nuevaClave):
        self.clave = nuevaClave
        self.save()

class Persona(models.Model):
    """
    Clase base. Usamos herencia multi-tabla o abstracta.
    Aquí la defino como abstracta para no crear una tabla 'persona' vacía,
    sino que sus campos pasen a los hijos.
    """
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    
    # Relación 1 a 1 con Cuenta ("autentica")
    cuenta = models.OneToOneField(Cuenta, on_delete=models.CASCADE, related_name='%(class)s_perfil')

    class Meta:
        abstract = True # Los campos se heredarán a las clases hijas

    def getNombreCompleto(self):
        return f"{self.nombres} {self.apellidos}"

    def actualizarDatos(self):
        pass

    def __str__(self):
        return self.getNombreCompleto()

# --- HERENCIA DE PERSONA ---

class Administrador(Persona):
    fechaInicio = models.DateField()
    fechaFin = models.DateField(null=True, blank=True)
    
    # Las clases hijas ya tienen nombres, apellidos, cedula y cuenta heredados

class Conductor(Persona):
    tipoLicencia = models.CharField(max_length=20)
    disponibilidad = models.BooleanField(default=True)

class Docente(Persona):
    facultad = models.CharField(max_length=50, choices=Facultad.choices)
    titulo = models.CharField(max_length=100)

class Estudiante(Persona):
    facultad = models.CharField(max_length=50, choices=Facultad.choices)

# --- MODELOS DE NEGOCIO ---

class Vehiculo(models.Model):
    placa = models.CharField(max_length=20, unique=True)
    modelo = models.CharField(max_length=50)
    tipoVehiculo = models.CharField(max_length=20, choices=TipoVehiculo.choices)
    disponibilidad = models.BooleanField(default=True)
    aforo = models.IntegerField()
    
    # Relación: Universidad "posee" Vehiculo (1 a muchos)
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE, related_name='vehiculos')
    
    # Relación: Conductor "conduce" Vehiculo
    # Nota: El diagrama sugiere una asociación. Puede ser un FK aquí o en Conductor.
    conductor = models.ForeignKey(Conductor, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehiculos')

    def __str__(self):
        return f"{self.tipoVehiculo} - {self.placa}"

class Reserva(models.Model):
    motivo = models.TextField()
    aforo = models.IntegerField() # Cuántas personas irán
    fechaInicio = models.DateTimeField()
    fechaFin = models.DateTimeField()
    estado = models.CharField(
        max_length=20, 
        choices=EstadoReserva.choices, 
        default=EstadoReserva.ESPERA_ACEPTACION
    )

    # Relación: Docente "solicita" Reserva
    solicitante = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name='reservas_solicitadas')
    
    # Relación: Reserva "asignada_a" Vehiculo
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas')

    def validarDisponibilidad(self):
        # Lógica para verificar si el vehículo está libre en esas fechas
        pass

    def __str__(self):
        return f"Reserva de {self.solicitante} - {self.fechaInicio}"

class Asistencia(models.Model):
    confirmacion = models.BooleanField(default=False)
    fechaRegistro = models.DateTimeField(auto_now_add=True)
    
    # Relación: Reserva "contiene" Asistencia
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='asistencias')
    
    # Relación: Estudiante "confirma" Asistencia
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='asistencias')

    class Meta:
        unique_together = ('reserva', 'estudiante') # Evita duplicados

    def registrar(self):
        self.confirmacion = True
        self.save()