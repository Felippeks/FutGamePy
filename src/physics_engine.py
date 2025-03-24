import math
import random
from typing import List, Optional
from .config import Config
from .ball import Ball
from .paddle import Paddle
from .sound_manager import SoundManager

class PhysicsEngine:
    @staticmethod
    def handle_collisions(ball: Ball, paddles: List[Paddle], sound_manager: SoundManager) -> Optional[str]:
        """
        Lida com as colisões da bola com as bordas do campo e com as raquetes.
        Retorna o jogador que marcou um gol, se houver.
        """
        # Colisão com as bordas superior e inferior do campo
        if ball.rect.top <= Config.FIELD_OFFSET_Y:
            ball.rect.top = Config.FIELD_OFFSET_Y
            ball.speed_y *= -1
            sound_manager.play_collision_sound()
        elif ball.rect.bottom >= Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT:
            ball.rect.bottom = Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT
            ball.speed_y *= -1
            sound_manager.play_collision_sound()

        # Colisão com as raquetes
        for paddle in paddles:
            dx = ball.rect.centerx - paddle.rect.centerx
            dy = ball.rect.centery - paddle.rect.centery
            distance = math.hypot(dx, dy)
            
            if distance < (Config.BALL_SIZE // 2 + max(paddle.rect.width, paddle.rect.height) // 2):
                angle = math.atan2(dy, dx)
                ball.speed_x = Config.BALL_SPEED * math.cos(angle)
                ball.speed_y = Config.BALL_SPEED * math.sin(angle)
                ball.rotation_speed = random.uniform(-8, 8)
                sound_manager.play_collision_sound()

        # Colisão com as bordas laterais do campo
        if ball.rect.left <= Config.FIELD_OFFSET_X:
            if (Config.HEIGHT - Config.GOAL_HEIGHT) // 2 < ball.rect.centery < (Config.HEIGHT + Config.GOAL_HEIGHT) // 2:
                sound_manager.play_goal_sound()
                return "player2"
            ball.rect.left = Config.FIELD_OFFSET_X
            ball.speed_x = abs(ball.speed_x)
            sound_manager.play_collision_sound()
        elif ball.rect.right >= Config.FIELD_OFFSET_X + Config.FIELD_WIDTH:
            if (Config.HEIGHT - Config.GOAL_HEIGHT) // 2 < ball.rect.centery < (Config.HEIGHT + Config.GOAL_HEIGHT) // 2:
                sound_manager.play_goal_sound()
                return "player1"
            ball.rect.right = Config.FIELD_OFFSET_X + Config.FIELD_WIDTH
            ball.speed_x = -abs(ball.speed_x)
            sound_manager.play_collision_sound()
        
        return None