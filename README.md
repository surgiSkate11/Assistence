# Sistema de Asistencia Facial UNEMI

Este proyecto es un sistema de control de asistencia basado en reconocimiento facial y prueba de movimiento, desarrollado con Django, OpenCV y MediaPipe.

## Características
- Registro de asistencia con validación biométrica (detección y movimiento de rostro)
- Panel de métricas en tiempo real
- Tabla de asistencias recientes
- Autenticación de usuarios
- Soporte para fotos de perfil
- Interfaz moderna y responsiva

## Requisitos
- Python 3.10+
- Django 5+
- OpenCV
- MediaPipe

## Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/ofdaniOnfire/Assitence.git
   cd Assitence
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   source venv/bin/activate  # En Linux/Mac
   ```
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Realiza migraciones:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Ejecuta el servidor:
   ```bash
   python manage.py runserver
   ```

## Uso
- Accede a `http://localhost:8000/` y autentícate.
- Permite el acceso a la cámara para registrar tu asistencia.
- Consulta tus registros y métricas en el dashboard.

## Configuración
- El sistema está configurado para el timezone de Ecuador (`America/Guayaquil`).
- Las fotos de perfil se almacenan en la carpeta `media/`.

## Licencia
MIT

## Autor
- ofdaniOnfire
