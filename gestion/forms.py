from django import forms
from .models import Cliente, Equipo, OrdenReparacion, FichaTecnica

# 1. Clase base para aplicar la estética "Hard" (bordes rectos e industrial)
class IndustrialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'input-industrial',
                'style': 'border-radius: 0 !important;'
            })

# 2. Formulario para Datos del Cliente
class ClienteForm(IndustrialForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'direccion', 'email']

# 3. Formulario para Datos del Equipo (Atributos fijos)
class EquipoForm(IndustrialForm):
    class Meta:
        model = Equipo
        fields = ['tipo', 'marca', 'modelo', 'ubicacion', 'tipo_gas']

# 4. Formulario de Ingreso (Solo falla inicial)
class OrdenIngresoForm(IndustrialForm):
    class Meta:
        model = OrdenReparacion
        fields = ['falla_declarada']
        widgets = {
            'falla_declarada': forms.Textarea(attrs={'rows': 2, 'placeholder': '¿Qué dice el cliente?'}),
        }

# 5. Formulario de Reparación (Lo técnico de la orden actual)
class OrdenTecnicaForm(IndustrialForm):
    class Meta:
        model = OrdenReparacion
        fields = ['diagnostico_tecnico', 'reparacion_realizada', 'costo_mano_obra', 'estado']
        widgets = {
            'diagnostico_tecnico': forms.Textarea(attrs={'rows': 3}),
            'reparacion_realizada': forms.Textarea(attrs={'rows': 3}),
        }
        
# 6. Formulario de Especificaciones Hardware (Datos que quedan en el equipo)
class EspecificacionesForm(IndustrialForm):
    class Meta:
        model = FichaTecnica
        fields = ['gas_tipo', 'gas_cantidad', 'datos_electricos']
        widgets = {
            'datos_electricos': forms.TextInput(attrs={'placeholder': 'Ej: 220V - 1.5A'}),
        }
