from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from gestion.models import Cliente, Equipo, OrdenReparacion
from datetime import datetime, timedelta


@override_settings(DEBUG=True, DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'test'}})
class GestionTests(TestCase):
    """Tests mínimos para los flujos críticos de gestión."""

    def setUp(self):
        """Crear un usuario técnico para las pruebas."""
        self.user = User.objects.create_user(username='tecnico', password='clave12345')
        self.client.login(username='tecnico', password='clave12345')

    def test_ingreso_equipo_flow(self):
        """Test que el flujo completo de ingreso de equipo funcione."""
        response = self.client.post('/ingresar/', {
            'nombre': 'Cliente Test', 'telefono': '3410000000',
            'tipo': 'SPLIT', 'marca': 'Samsung', 'modelo': 'Inverter 4500',
            'capacidad': '3000', 'tipo_gas': 'R410a', 'ubicacion': 'Living',
            'falla_declarada': 'No enfría correctamente',
        })
        self.assertEqual(response.status_code, 302)  # Redirige al tablero
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(Equipo.objects.count(), 1)
        self.assertGreater(OrdenReparacion.objects.count(), 0)

    def test_detalle_orden_post(self):
        """Test que guardar detalle de orden funciona."""
        # Primero crear una orden
        from gestion.models import Cliente, Equipo, OrdenReparacion
        cliente = Cliente.objects.create(nombre='Test', telefono='1234')
        equipo = Equipo.objects.create(cliente=cliente, marca='Test', modelo='M', tipo='SPLIT')
        orden = OrdenReparacion.objects.create(equipo=equipo, estado='PENDIENTE', falla_declarada='Test')
        
        response = self.client.post(
            reverse('detalle_orden', args=[orden.id]),
            data={'diagnostico_tecnico': 'Fallo el compresor', 'reparacion_realizada': 'Cambiar compresor', 'costo_mano_obra': '5000', 'estado': 'REPARACION'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')

    def test_api_evento_fecha_pasada(self):
        """Test que el API de calendario rechaza fechas pasadas."""
        from gestion.models import EventoCalendario
        response = self.client.post(
            reverse('crear_evento_api'),
            data={'tipo': 'TURNO', 'fecha_hora': '2020-01-15T10:00:00', 'titulo': 'Passado', 'descripcion': 'Test'},
            content_type='application/json'
        )
        self.assertNotEqual(response.status_code, 200)  # Debe fallar por fecha pasada

    def test_lista_clientes_con_busqueda(self):
        """Test que el buscador de clientes funciona."""
        response = self.client.get('/clientes/', {'q': 'Juan'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Juan')