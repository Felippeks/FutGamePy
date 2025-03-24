import pygame
import random
from .config import Config
from .asset_loader import AssetLoader

class Ball:
    def __init__(self):
        self.original_image = AssetLoader.load_image("assets/imagens/soccer_ball.png")
        self.image = self._create_circular_surface()
        self.reset()

    def _create_circular_surface(self) -> pygame.Surface:
        """
        Cria uma superfície circular para a bola.
        """
        size = Config.BALL_SIZE
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Redimensionar mantendo proporções
        img_width, img_height = self.original_image.get_size()
        scale = min(size/img_width, size/img_height)
        new_size = (int(img_width * scale), int(img_height * scale))
        scaled_img = pygame.transform.smoothscale(self.original_image, new_size)
        
        # Centralizar na superfície
        x_pos = (size - new_size[0]) // 2
        y_pos = (size - new_size[1]) // 2
        surface.blit(scaled_img, (x_pos, y_pos))
        
        # Aplicar máscara circular
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255,255,255,255), (size//2, size//2), size//2)
        surface.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        
        return surface

    def reset(self, direction: int = 1):
        """
        Reseta a posição e velocidade da bola.
        """
        self.rect = pygame.Rect(
            Config.WIDTH//2 - Config.BALL_SIZE//2,
            Config.HEIGHT//2 - Config.BALL_SIZE//2,
            Config.BALL_SIZE, Config.BALL_SIZE
        )
        self.speed_x = Config.BALL_SPEED * direction
        self.speed_y = Config.BALL_SPEED * random.uniform(-1, 1)
        self.angle = 0
        self.rotation_speed = random.uniform(-5, 5)

    def update(self):
        """
        Atualiza a posição e rotação da bola.
        """
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.angle += self.rotation_speed

    def draw(self, surface: pygame.Surface):
        """
        Desenha a bola na superfície fornecida.
        """
        rotated = pygame.transform.rotate(self.image, self.angle)
        surface.blit(rotated, rotated.get_rect(center=self.rect.center))