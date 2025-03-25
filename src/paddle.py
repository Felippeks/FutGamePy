import pygame
import random
from typing import Tuple
from .asset_loader import AssetLoader
from .config import Config
import math
from .head_tracker import HeadTracker

class Paddle:
    def __init__(self, image_path: str, constraints: Tuple[int, int, int, int], ball=None):
        self.image = AssetLoader.load_image(image_path, (Config.PADDLE_WIDTH, Config.PADDLE_HEIGHT))
        self.rect = pygame.Rect(0, 0, Config.PADDLE_WIDTH, Config.PADDLE_HEIGHT)
        self.constraints = constraints
        self.ball = ball
        self.cpu_speed = Config.PLAYER_SPEED * 0.75  # Reduce CPU speed
        self.prediction_error = 0  # Simulate human inaccuracy
        self.head_tracker = None  # Add this line

    def enable_head_tracking(self):
        try:
            self.head_tracker = HeadTracker()
            self.head_tracker.start()
        except Exception as e:
            print(f"Erro ao iniciar webcam: {e}")
            self.head_tracker = None

    def disable_head_tracking(self):
        if self.head_tracker:
            self.head_tracker.stop()
            self.head_tracker = None

    def move(self, dx: int, dy: int):
        if self.head_tracker and self.head_tracker.running:
            try:
                head_x, head_y = self.head_tracker.get_normalized_position()

                # Calcular posição alvo com base nos constraints
                target_x = self.constraints[0] + (
                        head_x * (self.constraints[1] - self.constraints[0] - self.rect.width))
                target_y = self.constraints[2] + (
                        head_y * (self.constraints[3] - self.constraints[2] - self.rect.height))

                # Calcular direção do movimento
                dx = (target_x - self.rect.x) * Config.PLAYER_SPEED * 0.1  # Fator de suavização
                dy = (target_y - self.rect.y) * Config.PLAYER_SPEED * 0.1

                # Limitar a velocidade máxima
                dx = max(min(dx, Config.PLAYER_SPEED), -Config.PLAYER_SPEED)
                dy = max(min(dy, Config.PLAYER_SPEED), -Config.PLAYER_SPEED)

                # Aplicar movimento
                self.rect.x += dx
                self.rect.y += dy

                # Garantir limites
                self.rect.x = max(min(self.rect.x, self.constraints[1] - self.rect.width), self.constraints[0])
                self.rect.y = max(min(self.rect.y, self.constraints[3] - self.rect.height), self.constraints[2])

            except Exception as e:
                print(f"Erro no rastreamento: {e}")
                # Fallback para controles manuais se o rastreamento falhar
                self.rect.x += dx
                self.rect.y += dy
        else:
            self.rect.x += dx
            self.rect.y += dy

        # Garantir limites em qualquer caso
        self.rect.x = max(min(self.rect.x, self.constraints[1] - self.rect.width), self.constraints[0])
        self.rect.y = max(min(self.rect.y, self.constraints[3] - self.rect.height), self.constraints[2])

    def cpu_move(self):
        if self.ball:
            # Nova verificação de parede próxima
            near_wall = (
                self.ball.rect.left <= Config.FIELD_OFFSET_X + 20 or
                self.ball.rect.right >= Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 20
            )

            if near_wall:
                # Comportamento diferente perto das paredes
                target_x = self.rect.centerx
                target_y = self.rect.centery - 50  # Recuar
                reaction_delay_chance = 0.3  # Aumentar chance de atraso
            else:
                # Configurações de comportamento
                skill_level = 0.5  # Reduzir o nível de habilidade
                reaction_delay_chance = 0.1  # Aumentar a chance de atraso na reação
                max_anticipation = 1.0  # Reduzir a antecipação máxima

                # Calcular posição futura
                ball_speed_factor = 1 + (self.ball.speed_x / Config.BALL_SPEED)
                target_x = self.ball.rect.centerx + self.ball.speed_x * ball_speed_factor
                target_y = self.ball.rect.centery + self.ball.speed_y * ball_speed_factor

                # Aumentar o erro de previsão
                prediction_error = random.randint(
                    -int(abs(self.ball.speed_y) * 5),  # Aumentar a margem de erro
                    int(abs(self.ball.speed_y) * 5)
                )

                if self.ball.speed_x > 0:
                    # Movimento ofensivo
                    target_x = min(target_x + prediction_error, self.constraints[1])
                    target_y += self.ball.speed_y * max_anticipation
                else:
                    # Movimento defensivo
                    target_x = self.rect.centerx  # Manter a posição atual
                    target_y = self.rect.centery + prediction_error * 0.5

            # Suavização de movimento com momentum
            dx = (target_x - self.rect.centerx) * 0.1  # Reduzir o fator de suavização
            dy = (target_y - self.rect.centery) * 0.1

            # Variação mais orgânica no movimento
            momentum = random.uniform(0.75, 1.25)  # Aumentar a variabilidade
            dx *= momentum
            dy *= momentum

            # Limitar velocidade e aplicar movimento
            dx = max(min(dx, self.cpu_speed), -self.cpu_speed)
            dy = max(min(dy, self.cpu_speed), -self.cpu_speed)
            self.move(int(dx), int(dy))

            # Comportamentos especiais
            if random.random() < 0.2:  # Aumentar a chance de movimento errático
                self.move(random.randint(-2, 2), random.randint(-2, 2))

            if random.random() < reaction_delay_chance:
                self.move(0, 0)  # Pular frame ao invés de usar wait()

    def check_and_reposition_ball(self):
        if self.ball:
            # Verificar colisão persistente
            if self.rect.colliderect(self.ball.rect):
                # Verificar se está próximo das bordas
                near_wall = (
                    self.ball.rect.left <= Config.FIELD_OFFSET_X + 5 or
                    self.ball.rect.right >= Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 5
                )

                # Reposicionamento mais assertivo
                if near_wall:
                    # Empurrar a bola para o centro
                    self.ball.rect.center = (
                        Config.WIDTH // 2,
                        Config.HEIGHT // 2
                    )
                    self.ball.speed_x = Config.BALL_SPEED * (-1 if self.ball.speed_x > 0 else 1)
                    self.ball.speed_y = Config.BALL_SPEED * random.uniform(-0.5, 0.5)
                else:
                    # Reposicionamento padrão
                    overlap_x = min(
                        self.ball.rect.right - self.rect.left,
                        self.rect.right - self.ball.rect.left
                    )

                    overlap_y = min(
                        self.ball.rect.bottom - self.rect.top,
                        self.rect.bottom - self.ball.rect.top
                    )

                    if overlap_x < overlap_y:
                        self.ball.speed_x *= -1.1  # Aumentar velocidade horizontal
                        self.ball.rect.x += math.copysign(overlap_x, self.ball.speed_x)
                    else:
                        self.ball.speed_y *= -1.1  # Aumentar velocidade vertical
                        self.ball.rect.y += math.copysign(overlap_y, self.ball.speed_y)