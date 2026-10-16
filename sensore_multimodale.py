import cv2
import mediapipe as mp
import socket
import math

# --- 1. CONFIGURAZIONE RETE UDP ---
UDP_IP = "127.0.0.1"
UDP_PORT = 5006
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- 2. INIZIALIZZAZIONE MEDIAPIPE E GRAFICA ---
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

marker_spec = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3)
line_spec = mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
face_line_spec = mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)

cap = cv2.VideoCapture(0)

print("[INFO] Test Standalone Sensore Multi-Modale Avviato.")
print("[INFO] Premi 'ESC' sulla finestra del video per uscire.")

with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("[ERRORE] Impossibile leggere il fotogramma dalla webcam.")
            break

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = holistic.process(image_rgb)

        strain_L1 = 0.0
        indice_stress = 0.0
        dist_tronco = 0.0

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=marker_spec, connection_drawing_spec=line_spec
            )
            pose = results.pose_landmarks.landmark
            spalla_y = pose[mp_holistic.PoseLandmark.LEFT_SHOULDER.value].y
            anca_y = pose[mp_holistic.PoseLandmark.LEFT_HIP.value].y
            dist_tronco = abs(anca_y - spalla_y)
            baseline_eretta = 0.634 
            if dist_tronco < baseline_eretta:
                strain_L1 = (baseline_eretta - dist_tronco) * 0.08
            strain_L1 = min(max(strain_L1, 0.0), 0.020)

        if results.face_landmarks:
            mp_drawing.draw_landmarks(
                image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
                landmark_drawing_spec=None, connection_drawing_spec=face_line_spec
            )
            face = results.face_landmarks.landmark
            sopracciglio_sx = face[107]
            sopracciglio_dx = face[336]
            dist_fronte = math.hypot(sopracciglio_sx.x - sopracciglio_dx.x, sopracciglio_sx.y - sopracciglio_dx.y)
            stress_raw = (0.055 - dist_fronte) * 4000
            indice_stress = min(max(stress_raw, 0.0), 100.0)

        # Trasmissione UDP
        payload = f"{strain_L1:.5f},{indice_stress:.1f}"
        sock.sendto(payload.encode(), (UDP_IP, UDP_PORT))

        # Dashboard visiva nativa OpenCV
        cv2.putText(image, f"Strain L1: {strain_L1:.5f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(image, f"Sforzo Viso: {indice_stress:.1f} %", (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(image, f"Dist Raw Tronco: {dist_tronco:.3f}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow('AeroSport - Sensore Standalone', image)

        # Premi ESC per uscire
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
