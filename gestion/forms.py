from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Cliente, Equipo, OrdenReparacion, FichaTecnica, EventoCalendario, ConfiguracionSistema

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
        fields = ['nombre', 'telefono', 'direccion', 'email', 'cuit', 'contacto', 'notas']
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 3}),
            'cuit': forms.TextInput(attrs={'placeholder': '30-12345678-9'}),
            'contacto': forms.TextInput(attrs={'placeholder': 'Nombre de la persona encargada'}),
        }

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
        fields = ['tipo', 'marca', 'modelo', 'capacidad', 'tipo_gas', 'ubicacion'] # Datos de identidad del equipo

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
        fields = ['tipo', 'fecha_hora', 'titulo', 'descripcion', 'orden', 'tag', 'completado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
            'tag': forms.TextInput(attrs={'placeholder': 'Ej: TR-102'}),
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

class ConfiguracionSistemaForm(IndustrialForm):
    rol_posicion = forms.ChoiceField(
        choices=[
            ('Administrador del Sistema', 'Administrador del Sistema'),
            ('Jefe de Taller Frigorífico', 'Jefe de Taller Frigorífico'),
            ('Técnico Especialista SCADA', 'Técnico Especialista SCADA'),
            ('Ingeniero de Mantenimiento', 'Ingeniero de Mantenimiento'),
        ]
    )

    class Meta:
        model = ConfiguracionSistema
        fields = '__all__'
        widgets = {
            'pin_firma_digital': forms.PasswordInput(render_value=True),
            'id_operador': forms.HiddenInput,
            'nivel_acceso': forms.HiddenInput,
            'token_valido_horas': forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- UMBRALES CRÍTICOS: estilo de alerta roja ---
        for name in ('temp_max_crit', 'pres_max_crit'):
            self.fields[name].widget.attrs.update({
                'class': 'bg-[#ffdad6] border border-[#ba1a1a] border-r-0 text-[#93000a] p-2 font-bold w-full rounded-none focus:outline-none',
            })

        # --- UMBRALES DE ADVERTENCIA: borde negro fino ---
        for name in ('temp_max_adv', 'pres_max_adv'):
            self.fields[name].widget.attrs.update({
                'class': 'bg-white border border-[#1a1a1a] border-r-0 p-2 font-bold w-full rounded-none focus:outline-none',
            })

        # --- CAMPOS MONETARIOS CON PREFIJO $ ---
        for name in ('valor_hora_tecnica_usd', 'tipo_cambio_usd_ars'):
            self.fields[name].widget.attrs.update({
                'class': 'bg-white border border-[#1a1a1a] border-l-0 p-2 font-bold w-full rounded-none focus:outline-none',
                'step': '0.5',
            })

        # --- MARGEN DE GANANCIA SUGERIDO (sufijo %) ---
        self.fields['margen_ganancia_sugerido'].widget.attrs.update({
            'class': 'bg-white border border-[#1a1a1a] border-r-0 p-2 font-bold w-full rounded-none focus:outline-none',
        })

        # --- TARIFAS DE SERVICIO ---
        for name in ('tarifa_diagnostico_usd', 'tarifa_mantenimiento_usd'):
            self.fields[name].widget.attrs.update({
                'class': 'bg-white border border-[#1a1a1a] p-1 font-bold text-right w-full rounded-none focus:outline-none',
            })

        # --- MULTIPLICADOR DE URGENCIA (rojo) ---
        self.fields['multiplicador_urgencia'].widget.attrs.update({
            'class': 'bg-white border border-[#ba1a1a] border-r-0 p-1 font-bold text-right text-[#ba1a1a] w-full rounded-none focus:outline-none',
            'step': '0.1',
        })

        # --- PIN DE FIRMA DIGITAL: espacio para el botón ojo ---
        self.fields['pin_firma_digital'].widget.attrs.update({
            'class': 'bg-white border-2 border-[#1a1a1a] p-2 w-full pr-10 font-mono text-sm tracking-widest rounded-none focus:outline-none focus:border-[#00f900]',
        })

class RegistroUsuarioForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'input-industrial', 'autocomplete': 'new-password'}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'input-industrial', 'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input-industrial', 'autocomplete': 'username'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user