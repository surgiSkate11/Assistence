# ============================================
# ARCHIVO: tests/test_integration.py
# Pruebas de integración
# ============================================

import os
import sys
import django

# Configurar Django antes de importar modelos
if __name__ == '__main__':
    # Agregar el directorio raíz al path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Configurar settings de Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asistencia_project.settings')
    django.setup()

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import UserProfile, Asistencia
from django.utils import timezone
import json


@override_settings(ALLOWED_HOSTS=['*'])
class URLIntegrationTests(TestCase):
    """Pruebas de integración para URLs y vistas"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
    def test_admin_page_accessible(self):
        """Prueba 1: Página de admin accesible"""
        response = self.client.get('/admin/')
        # Debe redirigir a login (302) o mostrar login (200)
        self.assertIn(response.status_code, [200, 302])
        print("✓ Test 1: Página admin accesible - PASSED")
        
    def test_home_page_requires_login(self):
        """Prueba 2: Página principal requiere autenticación"""
        response = self.client.get('/')
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        # Verificar que redirige a alguna página de login
        self.assertIn('/login', response.url.lower())
        print("✓ Test 2: Página principal requiere login - PASSED")
        
    def test_home_page_loads_when_authenticated(self):
        """Prueba 3: Página principal carga con autenticación"""
        # Autenticar usuario
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        print("✓ Test 3: Página principal carga con autenticación - PASSED")
        
    def test_video_feed_requires_login(self):
        """Prueba 4: Video feed requiere autenticación"""
        response = self.client.get('/video_feed/')
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        print("✓ Test 4: Video feed requiere login - PASSED")
        
    def test_get_metrics_requires_login(self):
        """Prueba 5: Get metrics requiere autenticación"""
        response = self.client.get('/get_metrics/')
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        print("✓ Test 5: Get metrics requiere login - PASSED")
        
    def test_get_metrics_returns_json_when_authenticated(self):
        """Prueba 6: Get metrics retorna JSON con autenticación"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/get_metrics/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Verificar estructura del JSON
        data = json.loads(response.content)
        self.assertIn('face_count', data)
        self.assertIn('status', data)
        self.assertIn('liveness_step', data)
        print("✓ Test 6: Get metrics retorna JSON válido - PASSED")


@override_settings(ALLOWED_HOSTS=['*'])
class AuthenticationIntegrationTests(TestCase):
    """Pruebas de integración para autenticación"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='authuser',
            email='auth@test.com',
            password='authpass123'
        )
        
    def test_login_functionality(self):
        """Prueba 7: Funcionalidad de login"""
        # Intentar login
        logged_in = self.client.login(username='authuser', password='authpass123')
        self.assertTrue(logged_in)
        
        # Verificar que puede acceder a página protegida
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print("✓ Test 7: Login funciona correctamente - PASSED")
        
    def test_login_with_wrong_password(self):
        """Prueba 8: Login con contraseña incorrecta"""
        logged_in = self.client.login(username='authuser', password='wrongpass')
        self.assertFalse(logged_in)
        print("✓ Test 8: Login rechaza contraseña incorrecta - PASSED")
        
    def test_logout_functionality(self):
        """Prueba 9: Funcionalidad de logout"""
        # Login primero
        self.client.login(username='authuser', password='authpass123')
        
        # Logout
        self.client.logout()
        
        # Verificar que no puede acceder a página protegida
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirige a login
        print("✓ Test 9: Logout funciona correctamente - PASSED")


@override_settings(ALLOWED_HOSTS=['*'])
class AsistenciaIntegrationTests(TestCase):
    """Pruebas de integración para registro de asistencia"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='student',
            email='student@unemi.edu.ec',
            password='studentpass123'
        )
        
    def test_asistencias_shown_in_homepage(self):
        """Prueba 10: Asistencias se muestran en la página principal"""
        # Crear asistencias
        Asistencia.objects.create(user=self.user)
        
        # Login y acceder a la página
        self.client.login(username='student', password='studentpass123')
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        # Verificar que el contexto existe y contiene asistencias
        if response.context is not None:
            self.assertIn('asistencias', response.context)
            self.assertGreater(len(response.context['asistencias']), 0)
        print("✓ Test 10: Asistencias mostradas en homepage - PASSED")
        
    def test_user_profile_created_on_user_creation(self):
        """Prueba 11: Perfil de usuario creado automáticamente"""
        new_user = User.objects.create_user(
            username='newstudent',
            email='new@test.com',
            password='newpass123'
        )
        
        # Verificar que el perfil existe
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertIsInstance(new_user.profile, UserProfile)
        print("✓ Test 11: Perfil creado automáticamente - PASSED")


class StaticFilesIntegrationTests(TestCase):
    """Pruebas de integración para archivos estáticos"""
    
    def test_static_files_configuration(self):
        """Prueba 12: Configuración de archivos estáticos"""
        from django.conf import settings
        
        self.assertTrue(hasattr(settings, 'STATIC_URL'))
        self.assertTrue(hasattr(settings, 'MEDIA_URL'))
        self.assertTrue(hasattr(settings, 'MEDIA_ROOT'))
        print("✓ Test 12: Configuración de archivos estáticos - PASSED")
        
    def test_installed_apps_configuration(self):
        """Prueba 13: Apps instaladas correctamente"""
        from django.conf import settings
        
        required_apps = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'core'
        ]
        
        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS)
        print("✓ Test 13: Apps requeridas instaladas - PASSED")


class DatabaseIntegrationTests(TestCase):
    """Pruebas de integración para base de datos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user1 = User.objects.create_user(
            username='dbuser1',
            email='db1@test.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='dbuser2',
            email='db2@test.com',
            password='pass123'
        )
        
    def test_multiple_users_can_have_asistencias(self):
        """Prueba 14: Múltiples usuarios pueden tener asistencias"""
        # Crear asistencias para ambos usuarios
        asist1 = Asistencia.objects.create(user=self.user1)
        asist2 = Asistencia.objects.create(user=self.user2)
        
        # Verificar que cada uno tiene su asistencia
        self.assertEqual(Asistencia.objects.filter(user=self.user1).count(), 1)
        self.assertEqual(Asistencia.objects.filter(user=self.user2).count(), 1)
        self.assertEqual(Asistencia.objects.all().count(), 2)
        print("✓ Test 14: Múltiples usuarios con asistencias - PASSED")
        
    def test_database_transactions(self):
        """Prueba 15: Transacciones de base de datos"""
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # Crear asistencia
                Asistencia.objects.create(user=self.user1)
                # Verificar que existe
                self.assertEqual(Asistencia.objects.filter(user=self.user1).count(), 1)
        except Exception as e:
            self.fail(f"Transacción falló: {e}")
            
        print("✓ Test 15: Transacciones de BD funcionan - PASSED")


@override_settings(ALLOWED_HOSTS=['*'])
class EndToEndIntegrationTests(TestCase):
    """Pruebas de integración de extremo a extremo"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='e2euser',
            email='e2e@test.com',
            password='e2epass123'
        )
        
    def test_complete_user_workflow(self):
        """Prueba 16: Flujo completo de usuario"""
        # 1. Usuario no autenticado intenta acceder
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirige a login
        
        # 2. Usuario hace login
        logged_in = self.client.login(username='e2euser', password='e2epass123')
        self.assertTrue(logged_in)
        
        # 3. Usuario accede a página principal
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'e2euser')
        
        # 4. Verificar que tiene perfil
        self.assertTrue(hasattr(self.user, 'profile'))
        
        # 5. Verificar que puede obtener métricas
        response = self.client.get('/get_metrics/')
        self.assertEqual(response.status_code, 200)
        
        print("✓ Test 16: Flujo completo de usuario - PASSED")
        
    def test_asistencia_registration_flow(self):
        """Prueba 17: Flujo de registro de asistencia"""
        # 1. Login
        self.client.login(username='e2euser', password='e2epass123')
        
        # 2. Verificar que no tiene asistencias
        asistencias_antes = Asistencia.objects.filter(user=self.user).count()
        self.assertEqual(asistencias_antes, 0)
        
        # 3. Simular registro de asistencia
        Asistencia.objects.create(user=self.user)
        
        # 4. Verificar que ahora tiene asistencia
        asistencias_despues = Asistencia.objects.filter(user=self.user).count()
        self.assertEqual(asistencias_despues, 1)
        
        # 5. Acceder a homepage y verificar que se muestra
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        if response.context is not None:
            self.assertIn('asistencias', response.context)
            self.assertEqual(len(response.context['asistencias']), 1)
        
        print("✓ Test 17: Flujo de registro de asistencia - PASSED")


if __name__ == '__main__':
    import unittest
    
    print("\n" + "="*70)
    print("PRUEBAS DE INTEGRACIÓN - Sistema de Asistencia")
    print("="*70 + "\n")
    
    # Crear suite de pruebas
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todas las clases de pruebas
    suite.addTests(loader.loadTestsFromTestCase(URLIntegrationTests))
    suite.addTests(loader.loadTestsFromTestCase(AuthenticationIntegrationTests))
    suite.addTests(loader.loadTestsFromTestCase(AsistenciaIntegrationTests))
    suite.addTests(loader.loadTestsFromTestCase(StaticFilesIntegrationTests))
    suite.addTests(loader.loadTestsFromTestCase(DatabaseIntegrationTests))
    suite.addTests(loader.loadTestsFromTestCase(EndToEndIntegrationTests))
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS DE INTEGRACIÓN")
    print("="*70)
    print(f"Total de pruebas ejecutadas: {result.testsRun}")
    print(f"Pruebas exitosas: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Pruebas fallidas: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    print("="*70 + "\n")
    
    # Exit code
    sys.exit(0 if result.wasSuccessful() else 1)

