from django import forms
from .models import Cliente, Equipo, OrdenReparacion

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'direccion', 'email']

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['tipo', 'marca', 'modelo', 'ubicacion']

class OrdenIngresoForm(forms.ModelForm):
    class Meta:
        model = OrdenReparacion
        fields = ['falla_declarada']