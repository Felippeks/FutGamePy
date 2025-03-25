import cv2
import mediapipe as mp
import threading

class HeadTracker:
    def __init__(self):
        self.mp_face = mp.solutions.face_detection
        self.face = self.mp_face.FaceDetection(min_detection_confidence=0.5)
        self.cap = None
        self.current_x = 0.5  # Novo: posição X normalizada
        self.current_y = 0.5
        self.running = False
        self.thread = None

    def start(self):
        if not self.cap:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.running = True
        self.thread = threading.Thread(target=self._update_loop)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        self.cap = None

    def _update_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face.process(rgb)

            if results.detections:
                detection = results.detections[0]
                box = detection.location_data.relative_bounding_box
                # Atualiza ambas as coordenadas
                self.current_x = box.xmin + box.width/2
                self.current_y = box.ymin + box.height/2

        self.face.close()

    def get_normalized_position(self):
        inverted_x = 1.0 - self.current_x
        return (inverted_x, self.current_y)