from django.db import models
from django.contrib.auth.models import User # Importamos la tabla de usuarios/técnicos
from .constants import ESTADOS_ORDEN, ESTADOS_ORDEN_DICT, ESTADOS_EN_PROCESO, ESTADOS_PARA_ENTREGAR, TIPOS_EQUIPO

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
    TIPOS = TIPOS_EQUIPO
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50, blank=True)
    capacidad = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: 3000 Frigorías, 400 Litros")
    tipo_gas = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo de Gas (Solo si aplica)")
    ubicacion = models.CharField(max_length=100, help_text="Ej: Dormitorio Principal")

    @property
    def total_reparaciones(self):
        return self.ordenreparacion_set.count()

    @property
    def ultimo_service(self):
        ultima_orden = self.ordenreparacion_set.order_by('-fecha_ingreso').first()
        return ultima_orden.fecha_ingreso if ultima_orden else None

    @property
    def dias_desde_service(self):
        from django.utils import timezone
        ultimo = self.ultimo_service
        if ultimo:
            return (timezone.now() - ultimo).days
        return 999 # Valor alto si nunca tuvo service

    def __str__(self):
        return f"{self.get_tipo_display()} {self.marca} - {self.cliente.nombre}"

class FichaTecnica(models.Model):
    """ Datos de ingeniería separados del equipo físico """
    equipo = models.OneToOneField(Equipo, on_delete=models.CASCADE, related_name='ficha')
    gas_tipo = models.CharField(max_length=20, help_text="Ej: R410a")
    gas_cantidad = models.IntegerField(help_text="Carga en gramos", null = True, blank = True)
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

class ConfiguracionSistema(models.Model):
    """Configuración global del sistema (singleton)."""
    # --- 1. DATOS DE PERFIL ---
    nombre_operador = models.CharField(max_length=100, default='')
    pin_firma_digital = models.CharField(max_length=50, default='', blank=True)
    rol_posicion = models.CharField(max_length=100, default='Administrador del Sistema')
    id_operador = models.CharField(max_length=50, default='OP-001')
    nivel_acceso = models.CharField(max_length=50, default='SUPERUSUARIO')
    token_valido_horas = models.IntegerField(default=24)
    # --- 2. MÉTRICAS Y PREFERENCIAS ---
    unidades_presion = models.CharField(max_length=20, choices=[('PSI','PSI'),('Bar','Bar'),('kPa','kPa'),('kg/cm²','kg/cm²')], default='PSI')
    unidades_temperatura = models.CharField(max_length=20, choices=[('°C','°C'),('°F','°F'),('K','K')], default='°C')
    temp_max_adv = models.DecimalField(max_digits=6, decimal_places=1, default=35.0)
    temp_max_crit = models.DecimalField(max_digits=6, decimal_places=1, default=45.0)
    pres_max_adv = models.DecimalField(max_digits=6, decimal_places=1, default=350.0)
    pres_max_crit = models.DecimalField(max_digits=6, decimal_places=1, default=450.0)
    # --- 3. CÁLCULOS Y TARIFAS ---
    valor_hora_tecnica_usd = models.DecimalField(max_digits=8, decimal_places=2, default=15.00)
    tipo_cambio_usd_ars = models.DecimalField(max_digits=10, decimal_places=2, default=1200.00)
    margen_ganancia_sugerido = models.DecimalField(max_digits=5, decimal_places=1, default=30.0)
    tarifa_diagnostico_usd = models.DecimalField(max_digits=8, decimal_places=2, default=25.00)
    tarifa_mantenimiento_usd = models.DecimalField(max_digits=8, decimal_places=2, default=40.00)
    multiplicador_urgencia = models.DecimalField(max_digits=4, decimal_places=2, default=1.50)
    # --- META ---
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración del sistema'
        verbose_name_plural = 'Configuración del sistema'

    @classmethod
    def obtener(cls):
        """Devuelve la configuración global creándola si no existe (singleton)."""
        config, _ = cls.objects.get_or_create(pk=1)
        return config

    def __str__(self):
        return f'Configuración del sistema (v{self.pk})'

# --- 4. TALLER Y REPARACIONES ---
class OrdenReparacion(models.Model):
    # --- 1. CONSTANTES (CHOICES) ---
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('DIAGNOSTICO', 'Diagnóstico'),
        ('REPARACION', 'Reparación'),
        ('COMPLETADO', 'Completado'),
        ('ENTREGADO', 'Entregado'),
    ]
    
    ESTADOS_PAGO = [
        ('DEBE', 'Impago'),
        ('SENA', 'Seña / Anticipo'),
        ('PAGADO', 'Pagado Totalmente'),
    ]

    # --- 2. RELACIONES (CLAVES FORÁNEAS Y M2M) ---
    equipo = models.ForeignKey(Equipo, on_delete=models.PROTECT)
    tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    insumos = models.ManyToManyField(Producto, through='DetalleInsumo')

    # --- 3. ESTADO Y METADATOS ---
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='DEBE') 
    en_banco_pruebas = models.BooleanField(default=False, help_text="Activa el panel SCADA para este equipo") 
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    
    # --- 4. TEXTOS (DESCRIPCIONES Y DIAGNÓSTICOS) ---
    falla_declarada = models.TextField(help_text="Qué dijo el cliente que pasa")
    diagnostico_tecnico = models.TextField(blank=True)
    reparacion_realizada = models.TextField(blank=True)
    detalle_insumos_extra = models.TextField(blank=True, help_text="Detalle rápido de insumos sin stock")
    
    # --- 5. FINANCIERO (PRECIOS Y COSTOS) ---
    costo_mano_obra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sena_monto = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monto dejado a cuenta para comprar insumo o repuesto")
    costo_insumos_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # --- 6. PROPIEDADES CALCULADAS ---
    @property
    def total_calculado(self):
        total_repuestos = sum(item.precio_congelado * item.cantidad for item in self.detalleinsumo_set.all())
        return self.costo_mano_obra + total_repuestos
    
    # --- 7. MÉTODOS MÁGICOS ---
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

class EventoCalendario(models.Model):
    TIPOS = [
        ('TURNO', 'Turno / Visita'),
        ('ENTREGA', 'Entrega de Equipo'),
        ('ALERTA', 'Alerta / Recordatorio'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPOS)
    fecha_hora = models.DateTimeField()
    titulo = models.CharField(max_length=100, help_text="Ej: Visita a domicilio, Entrega Heladera")
    descripcion = models.TextField(blank=True, null=True)
    
    # Opcional: Relacionar el evento con una reparación en curso
    orden = models.ForeignKey('OrdenReparacion', on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos')

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titulo}"