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
            if state.controls_menu_active:
                InputHandler._handle_controls_menu_click(event.pos, state, game)
            elif state.menu_active:
                InputHandler._handle_menu_click(event.pos, state, game)
            else:
                InputHandler._handle_game_click(event.pos, state, game)

        elif event.type == pygame.KEYDOWN:
            if state.menu_active and not state.controls_menu_active:
                InputHandler._handle_menu_key_input(event, state)
            elif state.is_paused:
                if event.key == pygame.K_ESCAPE:
                    state.is_paused = False

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
            state.is_paused = False
        elif buttons[1].collidepoint(pos):
            state.is_paused = not state.is_paused
            game.sound_manager.play_start_sound()

    @staticmethod
    def _handle_menu_click(pos: Tuple[int, int], state: GameState, game):
        """
        Lida com cliques no menu.
        """
        # Obter a posição do container do menu igual ao UI
        menu_width = 780
        menu_height = 450
        menu_rect_y = (Config.HEIGHT - menu_height) // 2

        # Elementos do menu (coordenadas relativas ao container)
        elements_y = menu_rect_y + 70
        spacing = 60

        # Campos de nome
        name_rects = [
            pygame.Rect(Config.WIDTH // 2 - 150, elements_y, 300, 40),
            pygame.Rect(Config.WIDTH // 2 - 150, elements_y + spacing, 300, 40)
        ]

        # Botões de tempo
        time_y = elements_y + spacing * 2
        time_buttons = [
            pygame.Rect(Config.WIDTH // 2 - 55 + i * 140, time_y, 110, 40)
            for i in range(3)
        ]

        # Botão Iniciar
        start_rect = pygame.Rect(Config.WIDTH // 2 - 100, time_y + 70, 200, 50)

        # Botão Controles
        controls_button_rect = pygame.Rect(
            Config.WIDTH // 2 - 100,
            time_y + 70 + spacing,  # elements_y + spacing * 4
            200,
            50
        )

        # Botão Mute
        mute_rect = pygame.Rect(
            Config.WIDTH // 2 - 75,
            time_y + 70 + spacing * 2,  # elements_y + spacing * 5
            150,
            50
        )

        # Verificação de clique primeiro no botão Controles
        if controls_button_rect.collidepoint(pos):
            state.menu_active = False
            state.controls_menu_active = True
            game.sound_manager.play_button_click_sound()
            return

        if mute_rect.collidepoint(pos):
            game.sound_manager.toggle_mute()
            return

        # Verificação de colisão
        for i, rect in enumerate(name_rects):
            if rect.collidepoint(pos):
                state.input_active = f'player{i + 1}'
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
            game.paddles[0].rect.topleft = (Config.FIELD_OFFSET_X + 50, Config.HEIGHT // 2 - Config.PADDLE_HEIGHT // 2)
            game.paddles[1].rect.topleft = (Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 50 - Config.PADDLE_WIDTH,
                                            Config.HEIGHT // 2 - Config.PADDLE_HEIGHT // 2)
            game.ball.reset()

            # Verificar se clicou no botão Controles
            controls_button_rect = pygame.Rect(
                Config.WIDTH // 2 - 100,
                elements_y + spacing * 4,  # Ajustar conforme posição do novo botão
                200,
                50
            )
            if controls_button_rect.collidepoint(pos):
                state.menu_active = False
                state.controls_menu_active = True
                return

            # Verificar se está no menu de controles
            if state.controls_menu_active:
                InputHandler._handle_controls_menu_click(pos, state, game)
                return

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

    @staticmethod
    def _handle_controls_menu_click(pos: Tuple[int, int], state: GameState, game):
        # Calcular posições relativas igual ao UI
        menu_width = 780
        menu_height = 450
        menu_rect_y = (Config.HEIGHT - menu_height) // 2

        # Player 1
        player1_y = menu_rect_y + 100
        for i in range(2):
            rect = pygame.Rect(
                Config.WIDTH // 2 - 90 + i * 180,
                player1_y + 5,
                170,
                30
            )
            if rect.collidepoint(pos):
                new_control = ["wasd", "virtual"][i]
                if new_control == "virtual":
                    game.paddles[0].enable_head_tracking()
                else:
                    game.paddles[0].disable_head_tracking()
                state.player1_control = new_control
                game.sound_manager.play_button_click_sound()

            # Verificar clique no botão de calibração
            if state.player1_control == "virtual":
                calibration_rect = pygame.Rect(
                    Config.WIDTH // 2 - 100,
                    player1_y + 50,
                    200,
                    40
                )

                if calibration_rect.collidepoint(pos):
                    if not state.is_calibrating:
                        # Verificar se o head_tracker foi criado
                        if game.paddles[0].head_tracker is None:
                            game.paddles[0].enable_head_tracking()

                        # Só inicia calibração se o head_tracker estiver ativo
                        if game.paddles[0].head_tracker and game.paddles[0].head_tracker.running:
                            game.paddles[0].head_tracker.start_calibration()
                            state.is_calibrating = True
                    else:
                        if game.paddles[0].head_tracker and game.paddles[0].head_tracker.end_calibration():
                            state.is_calibrating = False
                    game.sound_manager.play_button_click_sound()
                    return

        # Player 2
        player2_y = menu_rect_y + 250
        for i in range(2):
            rect = pygame.Rect(
                Config.WIDTH // 2 - 90 + i * 180,
                player2_y + 5,
                170,
                30
            )
            if rect.collidepoint(pos):
                state.player2_control = ["arrows", "cpu"][i]
                game.sound_manager.play_button_click_sound()

        # Botão Voltar
        back_rect = pygame.Rect(
            Config.WIDTH // 2 - 100,
            menu_rect_y + 380,
            200,
            50
        )
        if back_rect.collidepoint(pos):
            state.controls_menu_active = False
            state.menu_active = True
            game.sound_manager.play_button_click_sound()