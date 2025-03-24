import pygame
from typing import Tuple
from .config import Config
from .game_state import GameState
from .sound_manager import SoundManager

class InputHandler:
    @staticmethod
    def handle(event: pygame.event.Event, state: GameState, game):
        """
        Lida com os eventos de entrada do usuário.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state.menu_active:
                InputHandler._handle_menu_click(event.pos, state, game)
            else:
                InputHandler._handle_game_click(event.pos, state, game)
                
        elif event.type == pygame.KEYDOWN and state.menu_active:
            InputHandler._handle_menu_key_input(event, state)

    @staticmethod
    def _handle_game_click(pos: Tuple[int, int], state: GameState, game):
        """
        Lida com cliques no jogo.
        """
        buttons = [
            pygame.Rect(10, 10, Config.BUTTON_WIDTH - 50, Config.BUTTON_HEIGHT - 10),  # Menu
            pygame.Rect(Config.WIDTH - Config.BUTTON_WIDTH + 50 - 10, 10,
                       Config.BUTTON_WIDTH - 50, Config.BUTTON_HEIGHT - 10)  # Pausar/Continuar
        ]
        
        if buttons[0].collidepoint(pos):
            state.menu_active = True
            state.game_started = False
            state.is_paused = False  # Resetar pausa ao voltar ao menu
        elif buttons[1].collidepoint(pos):
            state.is_paused = not state.is_paused  # Alternar estado de pausa
            game.sound_manager.play_start_sound()

    @staticmethod
    def _handle_menu_click(pos: Tuple[int, int], state: GameState, game):
        """
        Lida com cliques no menu.
        """
        # Campos de nome
        name_rects = [
            pygame.Rect(Config.WIDTH//2 - 150, Config.HEIGHT//2 - 150, 300, 40),  # Ajustado para posição correta
            pygame.Rect(Config.WIDTH//2 - 150, Config.HEIGHT//2 - 90, 300, 40)  # Adicionado espaçamento correto
        ]
        
        # Botões de tempo
        time_y = Config.HEIGHT//2 - 30  # Posição Y calculada
        time_buttons = [
            pygame.Rect(Config.WIDTH//2 - 55 + i*140, time_y, 110, 40)  # Ajustado para centralizar melhor
            for i in range(3)
        ]
        
        # Botão Iniciar
        start_rect = pygame.Rect(Config.WIDTH//2 - 100, time_y + 70, 200, 50)

        # Botões de mute
        mute_rect = pygame.Rect(Config.WIDTH//2 - 75, time_y + 130, 150, 50)
        
        if mute_rect.collidepoint(pos):
            game.sound_manager.toggle_mute()
            return
        
        # Verificação de colisão
        for i, rect in enumerate(name_rects):
            if rect.collidepoint(pos):
                state.input_active = f'player{i+1}'
                return
                
        for i, rect in enumerate(time_buttons):
            if rect.collidepoint(pos):
                state.selected_duration = Config.TIME_OPTIONS[i]
                return
                
        if start_rect.collidepoint(pos):
            if not state.player1_name.strip():
                state.player1_name = "Player 1"
            if not state.player2_name.strip():
                state.player2_name = "Player 2"

            # Tocar som de início
            game.sound_manager.play_start_sound()
            
            # Resetar estado do jogo
            state.player1_score = 0
            state.player2_score = 0
            state.time_remaining = state.selected_duration
            state.game_started = True
            state.game_over = False
            state.menu_active = False
            state.is_paused = False
            
            # Resetar posições físicas
            game.paddles[0].rect.topleft = (Config.FIELD_OFFSET_X + 50, Config.HEIGHT//2 - Config.PADDLE_HEIGHT//2)
            game.paddles[1].rect.topleft = (Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 50 - Config.PADDLE_WIDTH, Config.HEIGHT//2 - Config.PADDLE_HEIGHT//2)
            game.ball.reset()

    @staticmethod
    def _handle_menu_key_input(event: pygame.event.Event, state: GameState):
        """
        Lida com a entrada de texto nos campos de nome do menu.
        """
        if state.input_active == 'player1':
            if event.key == pygame.K_BACKSPACE:
                if state.player1_name:  
                    state.player1_name = state.player1_name[:-1]
            elif event.unicode.isprintable() and len(state.player1_name) < 15:
                state.player1_name += event.unicode
        elif state.input_active == 'player2':
            if event.key == pygame.K_BACKSPACE:
                if state.player2_name:  
                    state.player2_name = state.player2_name[:-1]
            elif event.unicode.isprintable() and len(state.player2_name) < 15:
                state.player2_name += event.unicode