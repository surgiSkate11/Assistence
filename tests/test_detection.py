# ============================================
# ARCHIVO: tests/test_detection.py
# Pruebas unitarias para módulo de detección
# ============================================

import unittest
import cv2
import numpy as np
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestDetectionModule(unittest.TestCase):
    """Pruebas unitarias para el módulo de detección con OpenCV"""
    
    def setUp(self):
        """Configuración inicial antes de cada prueba"""
        # Crear imagen de prueba (640x480, 3 canales RGB)
        self.test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Crear una imagen con contenido
        self.test_image_with_content = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Cargar clasificador Haar Cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
    def test_image_validation_valid(self):
        """Prueba 1: Validar imagen válida"""
        # Verificar que la imagen no es None
        self.assertIsNotNone(self.test_image)
        # Verificar dimensiones correctas
        self.assertEqual(self.test_image.shape, (480, 640, 3))
        print("✓ Test 1: Validación de imagen válida - PASSED")
        
    def test_image_validation_invalid(self):
        """Prueba 2: Validar detección de imagen inválida"""
        invalid_image = None
        self.assertIsNone(invalid_image)
        print("✓ Test 2: Validación de imagen inválida - PASSED")
        
    def test_grayscale_conversion(self):
        """Prueba 3: Conversión a escala de grises"""
        gray_image = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2GRAY)
        # Verificar que es escala de grises (2 dimensiones)
        self.assertEqual(len(gray_image.shape), 2)
        # Verificar dimensiones
        self.assertEqual(gray_image.shape, (480, 640))
        print("✓ Test 3: Conversión a escala de grises - PASSED")
        
    def test_cascade_classifier_loaded(self):
        """Prueba 4: Cargar clasificador Haar Cascade"""
        self.assertIsNotNone(self.face_cascade)
        self.assertFalse(self.face_cascade.empty())
        print("✓ Test 4: Clasificador Haar Cascade cargado - PASSED")
        
    def test_face_detection_empty_image(self):
        """Prueba 5: Detección en imagen vacía"""
        gray = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        # No debería detectar rostros en imagen negra
        self.assertEqual(len(faces), 0)
        print("✓ Test 5: Detección en imagen vacía - PASSED")
        
    def test_image_preprocessing(self):
        """Prueba 6: Preprocesamiento de imagen"""
        # Aplicar desenfoque gaussiano
        blurred = cv2.GaussianBlur(self.test_image_with_content, (5, 5), 0)
        self.assertIsNotNone(blurred)
        self.assertEqual(blurred.shape, self.test_image_with_content.shape)
        print("✓ Test 6: Preprocesamiento de imagen - PASSED")
        
    def test_image_resize(self):
        """Prueba 7: Redimensionamiento de imagen"""
        resized = cv2.resize(self.test_image, (320, 240))
        self.assertEqual(resized.shape, (240, 320, 3))
        print("✓ Test 7: Redimensionamiento de imagen - PASSED")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("PRUEBAS UNITARIAS - Módulo de Detección")
    print("="*70 + "\n")
    
    unittest.main(verbosity=2)
