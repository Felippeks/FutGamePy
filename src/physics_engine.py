import math
import random
from typing import List, Optional
from .config import Config
from .ball import Ball
from .paddle import Paddle
from .sound_manager import SoundManager


class PhysicsEngine:
    @staticmethod
    def handle_collisions(ball: Ball, paddles: List[Paddle], sound_manager: SoundManager, game) -> Optional[str]:
        """
        Versão melhorada com prevenção de travamento e física mais estável
        """

        # Novo método para verificar colisões persistentes nas paredes
        def _check_wall_collision_stuck():
            if (ball.rect.left <= Config.FIELD_OFFSET_X + 5 or
                    ball.rect.right >= Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 5):
                if abs(ball.speed_x) < 2:
                    ball.speed_x *= 1.5
                    ball.speed_y *= 1.2
                    # Dar leve impulso vertical
                    ball.speed_y += random.uniform(-1, 1) * Config.BALL_SPEED / 2

        # Colisão com as bordas superior/inferior
        if ball.rect.top <= Config.FIELD_OFFSET_Y:
            ball.rect.top = Config.FIELD_OFFSET_Y + 1
            ball.speed_y = abs(ball.speed_y) * 1.1
            sound_manager.play_collision_sound()
        elif ball.rect.bottom >= Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT:
            ball.rect.bottom = Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT - 1
            ball.speed_y = -abs(ball.speed_y) * 1.1
            sound_manager.play_collision_sound()

        # Colisão com raquetes
        for paddle in paddles:
            dx = ball.rect.centerx - paddle.rect.centerx
            dy = ball.rect.centery - paddle.rect.centery
            distance = math.hypot(dx, dy)
            min_distance = (Config.BALL_SIZE // 2 + max(paddle.rect.width, paddle.rect.height) // 2)

            if distance < min_distance:
                angle = math.atan2(dy, dx)

                near_wall = (
                        ball.rect.left <= Config.FIELD_OFFSET_X + 15 or
                        ball.rect.right >= Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 15
                )

                if near_wall:
                    angle = math.radians(random.choice([75, 105, 255, 285]))

                ball.speed_x = Config.BALL_SPEED * math.cos(angle)
                ball.speed_y = Config.BALL_SPEED * math.sin(angle)

                # Empurrar a bola para fora se colada
                if distance < min_distance / 2:
                    push_force = 1 + (min_distance - distance) / min_distance
                    ball.rect.x += math.cos(angle) * push_force
                    ball.rect.y += math.sin(angle) * push_force

                ball.rotation_speed = random.uniform(-8, 8)
                sound_manager.play_collision_sound()

        # Colisão com laterais + verificação de travamento
        result = None
        if ball.rect.left <= Config.FIELD_OFFSET_X:
            if (Config.HEIGHT - Config.GOAL_HEIGHT) // 2 < ball.rect.centery < (
                    Config.HEIGHT + Config.GOAL_HEIGHT) // 2:
                sound_manager.play_goal_sound()
                result = "player2"
            else:
                ball.rect.left = Config.FIELD_OFFSET_X + 1
                ball.speed_x = abs(ball.speed_x)
                _check_wall_collision_stuck()
                sound_manager.play_collision_sound()

        elif ball.rect.right >= Config.FIELD_OFFSET_X + Config.FIELD_WIDTH:
            if (Config.HEIGHT - Config.GOAL_HEIGHT) // 2 < ball.rect.centery < (
                    Config.HEIGHT + Config.GOAL_HEIGHT) // 2:
                sound_manager.play_goal_sound()
                result = "player1"
            else:
                ball.rect.right = Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 1
                ball.speed_x = -abs(ball.speed_x)
                _check_wall_collision_stuck()
                sound_manager.play_collision_sound()

        return result