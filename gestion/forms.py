from django import forms
from django.utils import timezone
from .models import Cliente, Equipo, OrdenReparacion, FichaTecnica, EventoCalendario

class IndustrialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'input-industrial',
                'style': 'border-radius: 0 !important;'
            })

class ClienteForm(IndustrialForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'direccion', 'email']

class OrdenIngresoForm(IndustrialForm):
    class Meta:
        model = OrdenReparacion
        fields = ['falla_declarada']
        widgets = {
            'falla_declarada': forms.Textarea(attrs={'rows': 2, 'placeholder': '¿Qué dice el cliente?'}),
        }

class EquipoForm(IndustrialForm):
    class Meta:
        model = Equipo
        fields = ['tipo_gas', 'capacidad', 'modelo'] # Datos de identidad del equipo

class EspecificacionesForm(IndustrialForm):
    class Meta:
        model = FichaTecnica
        fields = ['gas_cantidad', 'datos_electricos'] # Datos de ingeniería
        widgets = {
                    # Esto lo convierte en un input de una sola línea (bajito)
                    'datos_electricos': forms.TextInput(attrs={'placeholder': 'Ej: 220V - 1.5A'}),
                }

class OrdenTecnicaForm(IndustrialForm):
    class Meta:
        model = OrdenReparacion
        fields = ['diagnostico_tecnico', 'reparacion_realizada', 'costo_mano_obra', 'estado']
        widgets = {
                    # Bajamos la cantidad de filas a 2 para que no ocupen media pantalla
                    'diagnostico_tecnico': forms.Textarea(attrs={'rows': 2}),
                    'reparacion_realizada': forms.Textarea(attrs={'rows': 2}),
                }

class EventoCalendarioForm(IndustrialForm): # O forms.ModelForm
    # Definimos el campo manualmente para agregarle los formatos de entrada permitidos
    fecha_hora = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'max': '9999-12-31T23:59', # Limita el año a 4 dígitos
            'min': '2000-01-01T00:00'
        }),
        label="Fecha y Hora"
    )

    class Meta:
        model = EventoCalendario
        fields = ['tipo', 'fecha_hora', 'titulo', 'descripcion', 'orden']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_fecha_hora(self):
        fecha = self.cleaned_data.get('fecha_hora')
        if not fecha:
            return fecha
        
        if fecha < timezone.now():
            raise ValidationError("No podés agendar un turno en el pasado.")
            
        if timezone.is_naive(fecha):
            return timezone.make_aware(fecha, timezone.get_current_timezone())
            
        return fecha