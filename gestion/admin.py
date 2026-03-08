from django.contrib import admin
from django.utils.html import mark_safe
from .models import Cliente, Equipo, FichaTecnica, Producto, OrdenReparacion, DetalleInsumo, NotaTecnica, FotoEquipo

# --- 1. CONFIGURACIÓN DE INLINES (Tablas dentro de otras) ---

class FotoEquipoInline(admin.TabularInline):
    model = FotoEquipo
    extra = 1
    readonly_fields = ['miniatura']

    def miniatura(self, obj):
        if obj.imagen:
            return mark_safe(f'<img src="{obj.imagen.url}" width="100" height="auto" />')
        return "Sin imagen"

class FichaTecnicaInline(admin.StackedInline):
    """ Muestra la ficha técnica verticalmente dentro del equipo """
    model = FichaTecnica
    can_delete = False
    verbose_name_plural = 'Ficha Técnica (Gas, Electricidad)'

class DetalleInsumoInline(admin.TabularInline):
    """ Permite cargar repuestos directamente dentro de la Orden """
    model = DetalleInsumo
    extra = 1

class NotaTecnicaInline(admin.StackedInline):
    """ Permite escribir notas directamente dentro de la Orden """
    model = NotaTecnica
    extra = 0

# --- 2. CONFIGURACIÓN DE PANTALLAS PRINCIPALES ---

class EquipoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'tipo', 'modelo', 'cliente')
    search_fields = ('marca', 'cliente__nombre')
    # AQUI ESTÁ LA CLAVE: Agregamos Ficha Técnica Y Fotos juntas
    inlines = [FichaTecnicaInline, FotoEquipoInline]

class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipo', 'estado_color', 'fecha_ingreso', 'tecnico')
    list_filter = ('estado', 'tecnico')
    search_fields = ('equipo__marca', 'equipo__cliente__nombre')
    # Agregamos Insumos y Notas dentro de la Orden para trabajar cómodo
    inlines = [DetalleInsumoInline, NotaTecnicaInline]
    
    def estado_color(self, obj):
        colores = {
            'PENDIENTE': 'red',
            'DIAGNOSTICO': 'orange',
            'ESPERA': 'orange',
            'REPARACION': 'blue',
            'TERMINADO': 'green',
            'ENTREGADO': 'gray',
        }
        color = colores.get(obj.estado, 'black')
        return mark_safe(f'<span style="color: {color}; font-weight: bold;">{obj.get_estado_display()}</span>')
    estado_color.short_description = 'Estado'

# --- 3. REGISTRO OFICIAL (Lo que se ve en el menú) ---
admin.site.register(Cliente)
admin.site.register(Equipo, EquipoAdmin)
admin.site.register(Producto)
admin.site.register(OrdenReparacion, OrdenAdmin)

# Los volvemos a habilitar por si quieres verlos sueltos en el menú:
admin.site.register(FichaTecnica)
admin.site.register(DetalleInsumo)
admin.site.register(NotaTecnica)