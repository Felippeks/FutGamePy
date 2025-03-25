import pygame
from typing import Optional
from .config import Config

class GameState:
    def __init__(self):
        pygame.init()
        self.reset()

        self.controls_menu_active = False
        self.player1_control = "wasd"
        self.player2_control = "arrows"
        self.is_calibrating = False

    def reset(self):
        """
        Reseta o estado do jogo para os valores iniciais.
        """
        self.player1_control = "wasd"
        self.player2_control = "arrows"
        self.player1_score = 0
        self.player2_score = 0
        self.selected_duration = Config.TIME_OPTIONS[0]
        self.time_remaining = self.selected_duration
        self.game_started = False
        self.game_over = False
        self.player1_name = ""
        self.player2_name = ""
        self.input_active: Optional[str] = None
        self.menu_active = True
        self.is_paused = False
        self.controls_menu_active = False
        self.is_calibrating = False