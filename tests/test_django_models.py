# ============================================
# ARCHIVO: tests/test_django_models.py
# Pruebas unitarias para modelos Django
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

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime, timedelta
from core.models import UserProfile, Asistencia
import time


class UserProfileModelTest(TestCase):
    """Pruebas unitarias para el modelo UserProfile"""
    
    def setUp(self):
        """Crear datos de prueba"""
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@test.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        
    def test_user_profile_auto_creation(self):
        """Prueba 1: Perfil se crea automáticamente al crear usuario"""
        # Verificar que el perfil fue creado automáticamente por la señal
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsNotNone(self.user.profile)
        self.assertIsInstance(self.user.profile, UserProfile)
        print("✓ Test 1: Perfil creado automáticamente - PASSED")
        
    def test_user_profile_str_method(self):
        """Prueba 2: Método __str__ del perfil"""
        expected = self.user.username
        self.assertEqual(str(self.user.profile), expected)
        print("✓ Test 2: Método __str__ del perfil - PASSED")
        
    def test_user_profile_one_to_one_relationship(self):
        """Prueba 3: Relación OneToOne con User"""
        profile = self.user.profile
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.user.username, "testuser")
        print("✓ Test 3: Relación OneToOne correcta - PASSED")
        
    def test_user_profile_foto_perfil_null(self):
        """Prueba 4: Foto de perfil puede ser nula"""
        profile = self.user.profile
        self.assertIsNone(profile.foto_perfil.name)
        print("✓ Test 4: Foto de perfil puede ser nula - PASSED")
        
    def test_user_profile_foto_perfil_upload(self):
        """Prueba 5: Subir foto de perfil"""
        # Crear un archivo de imagen simulado
        image_content = b'GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;'
        uploaded_file = SimpleUploadedFile(
            name='test_image.gif',
            content=image_content,
            content_type='image/gif'
        )
        
        profile = self.user.profile
        profile.foto_perfil = uploaded_file
        profile.save()
        
        # Verificar que se guardó
        self.assertIsNotNone(profile.foto_perfil)
        self.assertTrue(profile.foto_perfil.name.startswith('fotos_perfil/'))
        print("✓ Test 5: Foto de perfil subida correctamente - PASSED")
        
        # Limpiar archivo creado
        if profile.foto_perfil:
            if os.path.isfile(profile.foto_perfil.path):
                os.remove(profile.foto_perfil.path)
        
    def test_user_profile_deletion_cascade(self):
        """Prueba 6: Eliminar usuario elimina perfil (CASCADE)"""
        profile_id = self.user.profile.id
        self.user.delete()
        
        # Verificar que el perfil también fue eliminado
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(id=profile_id)
        print("✓ Test 6: Cascada de eliminación funciona - PASSED")


class AsistenciaModelTest(TestCase):
    """Pruebas unitarias para el modelo Asistencia"""
    
    def setUp(self):
        """Crear datos de prueba"""
        # Crear usuarios de prueba
        self.user1 = User.objects.create_user(
            username="estudiante1",
            email="estudiante1@unemi.edu.ec",
            password="pass123"
        )
        
        self.user2 = User.objects.create_user(
            username="estudiante2",
            email="estudiante2@unemi.edu.ec",
            password="pass123"
        )
        
    def test_asistencia_creation(self):
        """Prueba 7: Crear registro de asistencia"""
        asistencia = Asistencia.objects.create(user=self.user1)
        
        self.assertIsNotNone(asistencia.id)
        self.assertEqual(asistencia.user, self.user1)
        self.assertIsNotNone(asistencia.fecha_hora)
        print("✓ Test 7: Registro de asistencia creado - PASSED")
        
    def test_asistencia_str_method(self):
        """Prueba 8: Método __str__ de asistencia"""
        asistencia = Asistencia.objects.create(user=self.user1)
        str_representation = str(asistencia)
        
        self.assertIn(self.user1.username, str_representation)
        self.assertIn(asistencia.fecha_hora.strftime('%Y-%m-%d'), str_representation)
        print("✓ Test 8: Método __str__ de asistencia - PASSED")
        
    def test_asistencia_auto_now_add(self):
        """Prueba 9: Fecha y hora se agregan automáticamente"""
        antes = timezone.now()
        asistencia = Asistencia.objects.create(user=self.user1)
        despues = timezone.now()
        
        self.assertGreaterEqual(asistencia.fecha_hora, antes)
        self.assertLessEqual(asistencia.fecha_hora, despues)
        print("✓ Test 9: Fecha/hora automática funciona - PASSED")
        
    def test_asistencia_foreign_key_relationship(self):
        """Prueba 10: Relación ForeignKey con User"""
        asistencia = Asistencia.objects.create(user=self.user1)
        
        self.assertEqual(asistencia.user, self.user1)
        self.assertEqual(asistencia.user.username, "estudiante1")
        print("✓ Test 10: Relación ForeignKey correcta - PASSED")
        
    def test_asistencia_multiple_records_same_user(self):
        """Prueba 11: Múltiples registros para el mismo usuario"""
        asistencia1 = Asistencia.objects.create(user=self.user1)
        
        # Esperar 1 segundo para evitar conflicto de unique_together
        time.sleep(1)
        
        asistencia2 = Asistencia.objects.create(user=self.user1)
        
        asistencias = Asistencia.objects.filter(user=self.user1)
        self.assertEqual(asistencias.count(), 2)
        print("✓ Test 11: Múltiples registros por usuario - PASSED")
        
    def test_asistencia_user_deletion_cascade(self):
        """Prueba 12: Eliminar usuario elimina asistencias (CASCADE)"""
        asistencia = Asistencia.objects.create(user=self.user1)
        asistencia_id = asistencia.id
        
        self.user1.delete()
        
        # Verificar que la asistencia fue eliminada
        with self.assertRaises(Asistencia.DoesNotExist):
            Asistencia.objects.get(id=asistencia_id)
        print("✓ Test 12: Cascada de eliminación de asistencias - PASSED")
        
    def test_asistencia_ordering(self):
        """Prueba 13: Ordenamiento de registros de asistencia"""
        # Crear varios registros con pausas para evitar unique constraint
        asistencia1 = Asistencia.objects.create(user=self.user1)
        time.sleep(1)
        
        asistencia2 = Asistencia.objects.create(user=self.user2)
        time.sleep(1)
        
        asistencia3 = Asistencia.objects.create(user=self.user1)
        
        # Obtener todas las asistencias ordenadas por fecha
        asistencias = Asistencia.objects.all().order_by('-fecha_hora')
        
        self.assertEqual(asistencias.count(), 3)
        # La más reciente debe ser primero
        self.assertEqual(asistencias[0], asistencia3)
        print("✓ Test 13: Ordenamiento de asistencias - PASSED")
        
    def test_asistencia_filter_by_date(self):
        """Prueba 14: Filtrar asistencias por fecha"""
        asistencia = Asistencia.objects.create(user=self.user1)
        
        # Filtrar por fecha de hoy
        hoy = timezone.now().date()
        asistencias_hoy = Asistencia.objects.filter(
            fecha_hora__date=hoy
        )
        
        self.assertGreater(asistencias_hoy.count(), 0)
        self.assertIn(asistencia, asistencias_hoy)
        print("✓ Test 14: Filtrado por fecha - PASSED")
        
    def test_asistencia_count_by_user(self):
        """Prueba 15: Contar asistencias por usuario"""
        # Crear múltiples asistencias con pausas para evitar unique constraint
        Asistencia.objects.create(user=self.user1)
        time.sleep(1)
        
        Asistencia.objects.create(user=self.user1)
        time.sleep(1)
        
        Asistencia.objects.create(user=self.user1)
        time.sleep(1)
        
        Asistencia.objects.create(user=self.user2)
        
        # Contar asistencias
        count_user1 = Asistencia.objects.filter(user=self.user1).count()
        count_user2 = Asistencia.objects.filter(user=self.user2).count()
        
        self.assertEqual(count_user1, 3)
        self.assertEqual(count_user2, 1)
        print("✓ Test 15: Conteo de asistencias por usuario - PASSED")


class ModelIntegrationTest(TestCase):
    """Pruebas de integración entre modelos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username="integration_test",
            email="integration@test.com",
            password="testpass123"
        )
        
    def test_user_profile_and_asistencia_integration(self):
        """Prueba 16: Integración entre UserProfile y Asistencia"""
        # Verificar que el usuario tiene perfil
        self.assertTrue(hasattr(self.user, 'profile'))
        
        # Crear asistencia
        asistencia = Asistencia.objects.create(user=self.user)
        
        # Verificar relaciones
        self.assertEqual(asistencia.user, self.user)
        self.assertEqual(asistencia.user.profile.user, self.user)
        print("✓ Test 16: Integración UserProfile-Asistencia - PASSED")
        
    def test_complete_workflow(self):
        """Prueba 17: Flujo completo de registro de asistencia"""
        # 1. Usuario ya tiene perfil (creado automáticamente)
        profile = self.user.profile
        self.assertIsNotNone(profile)
        
        # 2. Registrar asistencia
        asistencia = Asistencia.objects.create(user=self.user)
        
        # 3. Verificar todo el flujo
        self.assertEqual(asistencia.user, self.user)
        self.assertEqual(str(profile), self.user.username)
        self.assertIn(self.user.username, str(asistencia))
        
        # 4. Verificar que se pueden obtener todas las asistencias del usuario
        asistencias_usuario = Asistencia.objects.filter(user=self.user)
        self.assertEqual(asistencias_usuario.count(), 1)
        self.assertEqual(asistencias_usuario.first(), asistencia)
        
        print("✓ Test 17: Flujo completo de asistencia - PASSED")


if __name__ == '__main__':
    import unittest
    
    print("\n" + "="*70)
    print("PRUEBAS UNITARIAS - Modelos Django")
    print("Sistema de Asistencia - CONSOF")
    print("="*70 + "\n")
    
    # Crear suite de pruebas
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todas las clases de pruebas
    suite.addTests(loader.loadTestsFromTestCase(UserProfileModelTest))
    suite.addTests(loader.loadTestsFromTestCase(AsistenciaModelTest))
    suite.addTests(loader.loadTestsFromTestCase(ModelIntegrationTest))
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    print(f"Total de pruebas ejecutadas: {result.testsRun}")
    print(f"Pruebas exitosas: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Pruebas fallidas: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    print("="*70 + "\n")
    
    # Exit code
    sys.exit(0 if result.wasSuccessful() else 1)
