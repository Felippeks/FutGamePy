import pygame
import random
import math
from typing import Tuple
from .asset_loader import AssetLoader
from .config import Config
from .head_tracker import HeadTracker


class Paddle:
    def __init__(self, image_path: str, constraints: Tuple[int, int, int, int], ball=None):
        self.image = AssetLoader.load_image(image_path, (Config.PADDLE_WIDTH, Config.PADDLE_HEIGHT))
        self.rect = pygame.Rect(0, 0, Config.PADDLE_WIDTH, Config.PADDLE_HEIGHT)
        self.constraints = constraints
        self.ball = ball

        # Configurações de movimento
        self.cpu_speed = Config.PLAYER_SPEED * 0.75
        self.prediction_error = 0
        self.head_tracker = None

        # Parâmetros para suavização e controle
        self.smoothing_factor = 0.3  # Fator de suavização (0.1-0.5)
        self.dead_zone = 0.02  # Zona morta para micro-movimentos
        self.sensitivity_x = 1.0  # Sensibilidade horizontal (ajustada para manter velocidade)
        self.sensitivity_y = 1.0  # Sensibilidade vertical (ajustada para manter velocidade)
        self.edge_margin = 50  # Margem para redução de velocidade nas bordas
        self.smoothed_x = constraints[0] + (constraints[1] - constraints[0]) // 2
        self.smoothed_y = constraints[2] + (constraints[3] - constraints[2]) // 2

    def enable_head_tracking(self):
        """Inicia o rastreamento de cabeça com webcam"""
        try:
            self.head_tracker = HeadTracker()
            self.head_tracker.start()
            print("Rastreamento de cabeça ativado com sucesso!")
        except Exception as e:
            print(f"Erro ao iniciar webcam: {e}")
            self.head_tracker = None

    def disable_head_tracking(self):
        """Desativa o rastreamento de cabeça"""
        if self.head_tracker:
            self.head_tracker.stop()
            self.head_tracker = None
            print("Rastreamento de cabeça desativado")

    def move(self, dx: int, dy: int):
        """Movimenta o paddle mantendo a velocidade consistente com o controle por teclado"""
        if self.head_tracker and self.head_tracker.running:
            try:
                head_x, head_y = self.head_tracker.get_normalized_position()

                # Aplica zona morta para micro-movimentos
                if abs(head_x - 0.5) < self.dead_zone: head_x = 0.5
                if abs(head_y - 0.5) < self.dead_zone: head_y = 0.5

                # Calcula posição alvo com constraints
                target_x = self.constraints[0] + (
                            head_x * (self.constraints[1] - self.constraints[0] - self.rect.width))
                target_y = self.constraints[2] + (
                            head_y * (self.constraints[3] - self.constraints[2] - self.rect.height))

                # Suavização com Exponential Moving Average (EMA)
                self.smoothed_x = self.smoothing_factor * target_x + (1 - self.smoothing_factor) * self.smoothed_x
                self.smoothed_y = self.smoothing_factor * target_y + (1 - self.smoothing_factor) * self.smoothed_y

                # Calcula a direção do movimento mantendo a velocidade padrão
                dx = (self.smoothed_x - self.rect.x) * Config.PLAYER_SPEED * 0.1
                dy = (self.smoothed_y - self.rect.y) * Config.PLAYER_SPEED * 0.1

                # Limita a velocidade máxima para igualar ao controle por teclado
                dx = max(min(dx, Config.PLAYER_SPEED), -Config.PLAYER_SPEED)
                dy = max(min(dy, Config.PLAYER_SPEED), -Config.PLAYER_SPEED)

                # Reduz velocidade perto das bordas
                if self.rect.x < self.constraints[0] + self.edge_margin:
                    dx *= 0.5
                elif self.rect.x > self.constraints[1] - self.edge_margin - self.rect.width:
                    dx *= 0.5

                # Modo "ancoragem" - retorno suave ao centro
                neutral_zone = 0.1
                if abs(head_x - 0.5) < neutral_zone and abs(head_y - 0.5) < neutral_zone:
                    center_x = self.constraints[0] + (self.constraints[1] - self.constraints[0]) // 2
                    dx = (center_x - self.rect.x) * 0.05

                # Aplica movimento
                self.rect.x += dx
                self.rect.y += dy

            except Exception as e:
                print(f"Erro no rastreamento: {e}")
                # Fallback para controles manuais
                self.rect.x += dx
                self.rect.y += dy
        else:
            # Movimento padrão por teclado (inalterado)
            self.rect.x += dx
            self.rect.y += dy

        # Garante que o paddle não saia dos limites
        self.rect.x = max(min(self.rect.x, self.constraints[1] - self.rect.width), self.constraints[0])
        self.rect.y = max(min(self.rect.y, self.constraints[3] - self.rect.height), self.constraints[2])

    def cpu_move(self):
        """Movimento controlado pela IA com comportamento mais orgânico"""
        if not self.ball:
            return

        # Comportamento diferente perto das paredes
        near_wall = (
                self.ball.rect.left <= Config.FIELD_OFFSET_X + 20 or
                self.ball.rect.right >= Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 20
        )

        if near_wall:
            target_x = self.rect.centerx
            target_y = self.rect.centery - 50  # Recua quando perto da parede
        else:
            # Previsão de posição com erro simulado
            ball_speed_factor = 1 + (self.ball.speed_x / Config.BALL_SPEED)
            target_x = self.ball.rect.centerx + self.ball.speed_x * ball_speed_factor
            target_y = self.ball.rect.centery + self.ball.speed_y * ball_speed_factor

            # Adiciona erro humano simulado
            prediction_error = random.randint(-int(abs(self.ball.speed_y) * 5), int(abs(self.ball.speed_y) * 5))
            target_y += prediction_error

        # Suavização com momentum variável
        momentum = random.uniform(0.7, 1.3)
        dx = (target_x - self.rect.centerx) * 0.1 * momentum
        dy = (target_y - self.rect.centery) * 0.1 * momentum

        # Limita velocidade máxima (usando cpu_speed como na versão original)
        dx = max(min(dx, self.cpu_speed), -self.cpu_speed)
        dy = max(min(dy, self.cpu_speed), -self.cpu_speed)

        # Movimento ocasionalmente errático
        if random.random() < 0.2:
            dx += random.uniform(-2, 2)
            dy += random.uniform(-2, 2)

        self.move(int(dx), int(dy))

    def check_and_reposition_ball(self):
        """Corrige colisões persistentes com a bola (mantido igual à versão original)"""
        if not self.ball or not self.rect.colliderect(self.ball.rect):
            return

        near_wall = (
                self.ball.rect.left <= Config.FIELD_OFFSET_X + 5 or
                self.ball.rect.right >= Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 5
        )

        if near_wall:
            # Reposicionamento radical perto das paredes
            self.ball.rect.center = (Config.WIDTH // 2, Config.HEIGHT // 2)
            self.ball.speed_x = Config.BALL_SPEED * (-1 if self.ball.speed_x > 0 else 1)
            self.ball.speed_y = Config.BALL_SPEED * random.uniform(-0.5, 0.5)
        else:
            # Reposicionamento normal
            overlap_x = min(self.ball.rect.right - self.rect.left, self.rect.right - self.ball.rect.left)
            overlap_y = min(self.ball.rect.bottom - self.rect.top, self.rect.bottom - self.ball.rect.top)

            if overlap_x < overlap_y:
                self.ball.speed_x *= -1.1
                self.ball.rect.x += math.copysign(overlap_x, self.ball.speed_x)
            else:
                self.ball.speed_y *= -1.1
                self.ball.rect.y += math.copysign(overlap_y, self.ball.speed_y)