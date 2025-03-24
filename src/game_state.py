import pygame
from typing import Optional
from .config import Config

class GameState:
    def __init__(self):
        pygame.init()
        self.reset()
        
    def reset(self):
        """
        Reseta o estado do jogo para os valores iniciais.
        """
        self.player1_score = 0
        self.player2_score = 0
        self.selected_duration = Config.TIME_OPTIONS[0]  # Tempo padrão 1 minuto
        self.time_remaining = self.selected_duration  # Usar a duração selecionada
        self.game_started = False
        self.game_over = False
        self.player1_name = ""
        self.player2_name = ""
        self.input_active: Optional[str] = None
        self.menu_active = True
        self.is_paused = False