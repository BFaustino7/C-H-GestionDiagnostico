from django.db import models
# Importamos la Orden desde la otra app para vincular los datos
from gestion.models import OrdenReparacion 

class RegistroMedicion(models.Model):
    orden = models.ForeignKey(OrdenReparacion, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    
    sensor = models.CharField(max_length=50, help_text="Ej: temp_salida, amperaje_compresor")
    valor = models.FloatField()
    unidad = models.CharField(max_length=10) # ºC, A, V

    def __str__(self):
        return f"{self.sensor}: {self.valor}{self.unidad} (Orden #{self.orden.id})"