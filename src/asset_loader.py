import pygame
import sys
import os
from typing import Tuple

class AssetLoader:
    @staticmethod
    def resource_path(relative_path: str) -> str:
        """
        Retorna o caminho absoluto do recurso, considerando se o jogo está empacotado com PyInstaller.
        """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    @staticmethod
    def load_font(name: str, size: int) -> pygame.font.Font:
        """
        Carrega uma fonte com o nome e tamanho especificados.
        """
        return pygame.font.Font(AssetLoader.resource_path(name), size)

    @staticmethod
    def load_image(path: str, size: Tuple[int, int] = None) -> pygame.Surface:
        """
        Carrega uma imagem do caminho especificado e a redimensiona se necessário.
        """
        img = pygame.image.load(AssetLoader.resource_path(path))
        return pygame.transform.scale(img, size) if size else img