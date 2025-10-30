


from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Asistencia
import cv2
import threading
import mediapipe as mp
from datetime import date

# --- Variables Globales para Métricas ---
metrics_lock = threading.Lock()
global_metrics = {
    "face_count": 0,
    "status": "Iniciando...",
    "liveness_step": 1, # 1: Buscando, 2: Mover rostro, 3: Quedarse quieto
}
# ----------------------------------------
camera_lock = threading.Lock()

mp_face_detection = mp.solutions.face_detection

@login_required
def index(request):
    with metrics_lock:
        global_metrics["face_count"] = 0
        global_metrics["status"] = "Buscando tu rostro..."
        global_metrics["liveness_step"] = 1
    # Obtener asistencias recientes del usuario
    asistencias = Asistencia.objects.filter(user=request.user).order_by('-fecha_hora')[:10]
    return render(request, 'core.html', {
        'user': request.user,
        'asistencias': asistencias
    })

def stream_generator(user):
    global global_metrics
    with camera_lock:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            with metrics_lock:
                global_metrics["status"] = "Error: Cámara no disponible"
            return

        liveness_step = 1 # 1: Buscando, 2: Mover rostro, 3: Quedarse quieto
        last_face_center = None
        still_frames_count = 0
        today = date.today()
        asistencia_registrada = Asistencia.objects.filter(user=user, fecha_hora__date=today).exists()
        if asistencia_registrada:
            with metrics_lock:
                global_metrics["status"] = "Asistencia ya registrada hoy"

        with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
            while True:
                success, frame = cap.read()
                if not success:
                    with metrics_lock:
                        global_metrics["status"] = "Stream finalizado"
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detection.process(rgb_frame)

                face_count = 0
                user_face_found = False
                status_text = "Buscando tu rostro..."
                color = (255, 165, 0)

                if results.detections:
                    face_count = len(results.detections)
                    user_face_found = True
                    detection = results.detections[0]
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x = int(bboxC.xmin * iw)
                    y = int(bboxC.ymin * ih)
                    w = int(bboxC.width * iw)
                    h = int(bboxC.height * ih)
                    face_center = (x + w // 2, y + h // 2)

                    if asistencia_registrada:
                        status_text = "Asistencia ya registrada"
                        color = (0, 128, 0)
                    else:
                        if liveness_step == 1:
                            status_text = "¡Hola! Por favor, gira tu rostro"
                            liveness_step = 2
                            last_face_center = face_center
                        elif liveness_step == 2:
                            if last_face_center:
                                move_distance = abs(face_center[0] - last_face_center[0]) + abs(face_center[1] - last_face_center[1])
                                if move_distance > 20:
                                    status_text = "¡Genial! Ahora quédate quieto"
                                    liveness_step = 3
                                    still_frames_count = 0
                                else:
                                    status_text = "Por favor, mueve un poco tu rostro"
                            last_face_center = face_center
                        elif liveness_step == 3:
                            still_frames_count += 1
                            status_text = f"Validando... ({still_frames_count}/30)"
                            if still_frames_count > 30:
                                Asistencia.objects.get_or_create(user=user, fecha_hora__date=today)
                                asistencia_registrada = True
                                liveness_step = 4
                                status_text = "Asistencia Registrada"
                                with metrics_lock:
                                    global_metrics["status"] = "Asistencia Registrada"
                        elif liveness_step == 4:
                            status_text = "Asistencia Registrada"
                            color = (0, 255, 0)

                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, status_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                    with metrics_lock:
                        global_metrics["face_count"] = face_count
                        global_metrics["status"] = status_text
                        global_metrics["liveness_step"] = liveness_step
                else:
                    with metrics_lock:
                        global_metrics["face_count"] = 0
                        global_metrics["status"] = "Buscando tu rostro..."
                        global_metrics["liveness_step"] = 1

                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        cap.release()
        with metrics_lock:
            global_metrics["status"] = "Cámara desconectada"

@login_required
def video_feed(request):
    return StreamingHttpResponse(stream_generator(request.user),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

@login_required
def get_metrics(request):
    with metrics_lock:
        data = global_metrics.copy()
    return JsonResponse(data)