from django.db import transaction
from .models import Producto, DetalleInsumo

@transaction.atomic
def procesar_insumos_orden(orden, insumos_data):
    """Procesa y guarda la lista dinámica de insumos desde un payload JSON."""
    if not insumos_data:
        return

    for insumo in insumos_data:
        nombre = insumo.get('nombre')
        precio = insumo.get('precio')
        
        prod, _ = Producto.objects.get_or_create(
            nombre=nombre,
            defaults={'precio_venta': precio, 'stock': 0}
        )
        DetalleInsumo.objects.create(
            orden=orden,
            producto=prod,
            cantidad=1,
            precio_congelado=precio
        )