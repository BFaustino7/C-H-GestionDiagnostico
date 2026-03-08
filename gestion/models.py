from django.db import models
from django.contrib.auth.models import User # Importamos la tabla de usuarios/técnicos

# --- 1. PERSONAS ---
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=50)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.telefono})"

# --- 2. EL PACIENTE (EQUIPO) ---
class Equipo(models.Model):
    TIPOS = [
        ('SPLIT', 'Aire Acondicionado Split'),
        ('VENTANA', 'Aire Acondicionado Ventana'),
        ('HELADERA', 'Heladera Familiar'),
        ('COMERCIAL', 'Heladera Comercial/Exhibidora'),
        ('LAVARROPAS', 'Lavarropas'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50, blank=True)
    ubicacion = models.CharField(max_length=100, help_text="Ej: Dormitorio Principal")

    def __str__(self):
        return f"{self.get_tipo_display()} {self.marca} - {self.cliente.nombre}"

class FichaTecnica(models.Model):
    """ Datos de ingeniería separados del equipo físico """
    equipo = models.OneToOneField(Equipo, on_delete=models.CASCADE, related_name='ficha')
    gas_tipo = models.CharField(max_length=20, help_text="Ej: R410a")
    gas_cantidad = models.IntegerField(help_text="Carga en gramos")
    datos_electricos = models.TextField(blank=True, help_text="Datos del compresor, capacitor, etc.")
    
    def __str__(self):
        return f"Ficha de {self.equipo}"

class FotoEquipo(models.Model):
    """ Permite subir múltiples fotos por equipo """
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='equipos/%Y/%m/') # Las organiza por año/mes
    descripcion = models.CharField(max_length=100, blank=True, help_text="Ej: Frente, Etiqueta, Daño lateral")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.equipo} ({self.descripcion})"

# --- 3. ALMACÉN ---
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ($ {self.precio_venta})"

# --- 4. TALLER Y REPARACIONES ---
class OrdenReparacion(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('DIAGNOSTICO', 'En Diagnóstico'),
        ('ESPERA', 'Esperando Repuesto/Aprobación'),
        ('REPARACION', 'En Reparación'),
        ('TERMINADO', 'Terminado (Listo p/ entregar)'),
        ('ENTREGADO', 'Entregado al Cliente'),
    ]

    equipo = models.ForeignKey(Equipo, on_delete=models.PROTECT)
    tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    
    falla_declarada = models.TextField(help_text="Qué dijo el cliente que pasa")
    diagnostico_tecnico = models.TextField(blank=True)
    
    costo_mano_obra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Relación M-to-M con Productos usando la tabla intermedia
    insumos = models.ManyToManyField(Producto, through='DetalleInsumo')

    def __str__(self):
        return f"Orden #{self.id} - {self.equipo}"

class NotaTecnica(models.Model):
    """ Bitácora del día a día """
    orden = models.ForeignKey(OrdenReparacion, on_delete=models.CASCADE, related_name='notas')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    texto = models.TextField()

    def __str__(self):
        return f"Nota {self.fecha.strftime('%d/%m %H:%M')} por {self.autor.username}"

class DetalleInsumo(models.Model):
    """ Tabla intermedia para congelar precios """
    orden = models.ForeignKey(OrdenReparacion, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_congelado = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio al momento de usarlo")

    def save(self, *args, **kwargs):
        # Si no tiene precio, tomamos el actual del producto
        if not self.precio_congelado:
            self.precio_congelado = self.producto.precio_venta
        super().save(*args, **kwargs)