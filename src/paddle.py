import pygame
from typing import Tuple
from .config import Config
from .asset_loader import AssetLoader

class Paddle:
    def __init__(self, image_path: str, constraints: Tuple[int, int, int, int]):
        """
        Inicializa a raquete com a imagem e as restrições de movimento.
        """
        self.image = AssetLoader.load_image(image_path, 
            (Config.PADDLE_WIDTH, Config.PADDLE_HEIGHT))
        self.rect = pygame.Rect(0, 0, Config.PADDLE_WIDTH, Config.PADDLE_HEIGHT)
        self.constraints = constraints

    def move(self, dx: int, dy: int):
        """
        Move a raquete de acordo com os deslocamentos dx e dy, respeitando as restrições.
        """
        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = max(min(self.rect.x, self.constraints[1] - self.rect.width), self.constraints[0])
        self.rect.y = max(min(self.rect.y, self.constraints[3] - self.rect.height), self.constraints[2])