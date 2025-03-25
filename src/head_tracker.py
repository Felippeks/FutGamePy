import cv2
import mediapipe as mp
import threading
import numpy as np
from typing import Tuple, Optional


class HeadTracker:
    def __init__(self):
        self.mp_face = mp.solutions.face_detection
        self.face = self.mp_face.FaceDetection(
            min_detection_confidence=0.7,  # Aumentar confiança mínima
            model_selection=1  # Usar modelo mais preciso
        )
        self.cap = None
        self.current_x = 0.5
        self.current_y = 0.5
        self.running = False
        self.thread = None

        # Parâmetros de calibração
        self.calibration_data = {
            'min_x': 0.0,
            'max_x': 1.0,
            'min_y': 0.0,
            'max_y': 1.0,
            'center_x': 0.5,
            'center_y': 0.5
        }
        self.is_calibrating = False
        self.calibration_samples = []

        # Configurações ajustáveis
        self.smoothing_factor = 0.7
        self.min_movement = 0.005
        self.movement_threshold = 0.02  # Threshold para considerar movimento válido

    def start(self):
        if not self.cap:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Aumentar resolução
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
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

    def start_calibration(self):
        """Inicia o processo de calibração"""
        self.is_calibrating = True
        self.calibration_samples = []
        print("Calibração iniciada - Mova sua cabeça em todas as direções")

    def end_calibration(self):
        """Finaliza a calibração e calcula os parâmetros"""
        if len(self.calibration_samples) < 10:  # Mínimo de amostras
            print("Calibração falhou - movimentos insuficientes")
            return False

        samples = np.array(self.calibration_samples)
        self.calibration_data['min_x'] = np.min(samples[:, 0])
        self.calibration_data['max_x'] = np.max(samples[:, 0])
        self.calibration_data['min_y'] = np.min(samples[:, 1])
        self.calibration_data['max_y'] = np.max(samples[:, 1])
        self.calibration_data['center_x'] = np.median(samples[:, 0])
        self.calibration_data['center_y'] = np.median(samples[:, 1])

        print("Calibração concluída com sucesso!")
        print(f"Range X: {self.calibration_data['min_x']:.2f}-{self.calibration_data['max_x']:.2f}")
        print(f"Range Y: {self.calibration_data['min_y']:.2f}-{self.calibration_data['max_y']:.2f}")
        self.is_calibrating = False
        return True

    def _normalize_position(self, x: float, y: float) -> Tuple[float, float]:
        """Normaliza a posição com base nos dados de calibração"""
        # Aplica calibração
        x_norm = (x - self.calibration_data['center_x']) / \
                 (self.calibration_data['max_x'] - self.calibration_data['min_x']) * 2.0
        y_norm = (y - self.calibration_data['center_y']) / \
                 (self.calibration_data['max_y'] - self.calibration_data['min_y']) * 2.0

        # Limita aos valores 0-1
        x_norm = max(0.0, min(1.0, 0.5 + x_norm))
        y_norm = max(0.0, min(1.0, 0.5 + y_norm))

        return x_norm, y_norm

    def _update_loop(self):
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                # Pré-processamento da imagem
                frame = cv2.flip(frame, 1)  # Espelhar a imagem
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Detecção de rosto
                results = self.face.process(rgb)

                if results.detections:
                    detection = results.detections[0]
                    box = detection.location_data.relative_bounding_box

                    # Nova posição detectada
                    new_x = box.xmin + box.width / 2
                    new_y = box.ymin + box.height / 2

                    # Durante calibração, apenas colete amostras
                    if self.is_calibrating:
                        self.calibration_samples.append((new_x, new_y))
                        continue

                    # Suavização de movimento
                    if abs(new_x - self.current_x) > self.min_movement:
                        self.current_x += (new_x - self.current_x) * self.smoothing_factor
                    if abs(new_y - self.current_y) > self.min_movement:
                        self.current_y += (new_y - self.current_y) * self.smoothing_factor
            except Exception as e:
                print(f"Erro na captura de vídeo: {e}")
                self.running = False
                break

    def get_normalized_position(self) -> Tuple[float, float]:
        """Retorna a posição normalizada e calibrada"""
        if self.is_calibrating:
            return 0.5, 0.5  # Posição central durante calibração

        x, y = self._normalize_position(self.current_x, self.current_y)
        return (x, y)  # Inverte o eixo X para movimento mais intuitivo

    def get_calibration_status(self) -> str:
        """Retorna o status da calibração"""
        if self.is_calibrating:
            return f"Calibrando... {len(self.calibration_samples)} amostras"
        return "Calibração concluída"