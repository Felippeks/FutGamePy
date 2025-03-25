import pygame
import cv2
from typing import Tuple
from .config import Config
from .asset_loader import AssetLoader
from .game_state import GameState
from .sound_manager import SoundManager

class UIManager:
    def __init__(self, state: GameState, sound_manager: SoundManager):
        self.state = state
        self.sound_manager = sound_manager
        self.hovered_button = None
        self.fonts = {
            size: AssetLoader.load_font("assets/fonts/PressStart2P-Regular.ttf", Config.FONT_SIZES[size])
            for size in ['normal', 'small', 'large']
        }
        self.fonts['button'] = AssetLoader.load_font("assets/fonts/PressStart2P-Regular.ttf", 10)
        self.grass = AssetLoader.load_image("assets/imagens/grass.png",
            (Config.FIELD_WIDTH, Config.FIELD_HEIGHT))

        # Carregar imagens dos cabeçalhos
        self.head1 = AssetLoader.load_image("assets/imagens/head1.png", (35, 30))
        self.head2 = AssetLoader.load_image("assets/imagens/head2.png", (35, 30))

    def draw_field(self, surface: pygame.Surface):
        """
        Desenha o campo de jogo.
        """
        surface.blit(self.grass, (Config.FIELD_OFFSET_X, Config.FIELD_OFFSET_Y))
        self._draw_field_markings(surface)

    def _draw_field_markings(self, surface: pygame.Surface):
        """
        Desenha as marcações do campo.
        """
        pygame.draw.line(surface, Config.WHITE,
            (Config.WIDTH//2, Config.FIELD_OFFSET_Y),
            (Config.WIDTH//2, Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT), 2)
        pygame.draw.rect(surface, Config.WHITE,
            (Config.FIELD_OFFSET_X, Config.FIELD_OFFSET_Y,
             Config.FIELD_WIDTH, Config.FIELD_HEIGHT), 2)

        pygame.draw.rect(surface, Config.GOLD,
            (Config.FIELD_OFFSET_X, (Config.HEIGHT - Config.GOAL_HEIGHT)//2,
             10, Config.GOAL_HEIGHT), border_radius=5)
        pygame.draw.rect(surface, Config.GOLD,
            (Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 10,
             (Config.HEIGHT - Config.GOAL_HEIGHT)//2, 10, Config.GOAL_HEIGHT), border_radius=5)

        area_width = 100
        area_height = Config.GOAL_HEIGHT + 100
        y_pos = (Config.HEIGHT - area_height)//2

        pygame.draw.rect(surface, Config.WHITE,
            (Config.FIELD_OFFSET_X, y_pos, area_width, area_height), 2)
        pygame.draw.rect(surface, Config.WHITE,
            (Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - area_width,
             y_pos, area_width, area_height), 2)

        pygame.draw.circle(surface, Config.WHITE,
            (Config.WIDTH//2, Config.HEIGHT//2), 80, 2)
        pygame.draw.circle(surface, Config.WHITE,
            (Config.WIDTH//2, Config.HEIGHT//2), 8)

    def draw_scoreboard(self, surface: pygame.Surface):
        """
        Desenha o placar do jogo.
        """
        self._draw_scores(surface)
        self._draw_timer(surface)
        self._draw_buttons(surface)

        if self.state.is_paused:
            self._draw_text_with_outline(surface, "PAUSADO", Config.WHITE)

    def _draw_scores(self, surface: pygame.Surface):
        """
        Desenha os nomes e pontuações dos jogadores.
        """
        name1 = self.fonts['small'].render(self.state.player1_name, True, Config.WHITE)
        name2 = self.fonts['small'].render(self.state.player2_name, True, Config.WHITE)
        score1 = self.fonts['normal'].render(str(self.state.player1_score), True, Config.WHITE)
        score2 = self.fonts['normal'].render(str(self.state.player2_score), True, Config.WHITE)

        # Desenhar nome e placar do Jogador 1 com imagem do cabeçalho
        surface.blit(name1, (Config.WIDTH//4 - name1.get_width()//2, 20))
        surface.blit(self.head1, (Config.WIDTH//4 + name1.get_width()//2 + 20, 10))
        surface.blit(score1, (Config.WIDTH//4 + name1.get_width()//2 + 90, 18))

        # Desenhar nome e placar do Jogador 2 com imagem do cabeçalho
        surface.blit(name2, (3*Config.WIDTH//4 - name2.get_width()//2, 20))
        surface.blit(self.head2, (3*Config.WIDTH//4 + name2.get_width()//2 + 20, 10))
        surface.blit(score2, (3*Config.WIDTH//4 + name2.get_width()//2 + 90, 18))

    def _draw_timer(self, surface: pygame.Surface):
        """
        Desenha o temporizador do jogo.
        """
        timer_text = self.fonts['normal'].render(
            f"{self.state.time_remaining//60}:{self.state.time_remaining%60:02d}",
            True, Config.WHITE)
        surface.blit(timer_text, (Config.WIDTH//2 - timer_text.get_width()//2, 20))

    def _draw_buttons(self, surface: pygame.Surface):
        """
        Desenha os botões de menu e pausa.
        """
        pause_text = "Continuar" if self.state.is_paused else "Pausar"
        buttons = [
            (10, 10, "Menu"),
            (Config.WIDTH - Config.BUTTON_WIDTH + 50 - 10, 10, pause_text)
        ]

        mouse_pos = pygame.mouse.get_pos()

        for x, y, text in buttons:
            rect = pygame.Rect(x, y, Config.BUTTON_WIDTH - 50, Config.BUTTON_HEIGHT - 10)

            if rect.collidepoint(mouse_pos):
                if self.hovered_button != rect:
                    self.sound_manager.play_button_hover_sound()
                    self.hovered_button = rect
                pygame.draw.rect(surface, Config.GOLD, rect, border_radius=15)
            else:
                if self.hovered_button == rect:
                    self.hovered_button = None
                pygame.draw.rect(surface, Config.WHITE, rect, border_radius=15)

            pygame.draw.rect(surface, Config.BLACK, rect, 2, border_radius=15)
            text_surf = self.fonts['button'].render(text, True, Config.BLACK)
            surface.blit(text_surf, (x + (Config.BUTTON_WIDTH - 50)//2 - text_surf.get_width()//2,
                                y + (Config.BUTTON_HEIGHT - 10)//2 - text_surf.get_height()//2))

    def draw_end_game(self, surface: pygame.Surface):
        """
        Desenha a tela de fim de jogo.
        """
        if self.state.player1_score > self.state.player2_score:
            text, color = f"{self.state.player1_name} Venceu!", Config.DARK_GOLD
        elif self.state.player2_score > self.state.player1_score:
            text, color = f"{self.state.player2_name} Venceu!", Config.DARK_GOLD
        else:
            text, color = "Empate!", Config.BLUE

        self._draw_text_with_outline(surface, text, color)

    def _draw_text_with_outline(self, surface: pygame.Surface, text: str, color: Tuple[int, int, int]):
        """
        Desenha texto com contorno.
        """
        text_surf = self.fonts['large'].render(text, True, color)
        outline_surf = self.fonts['large'].render(text, True, Config.BLACK)
        pos = (Config.WIDTH//2 - text_surf.get_width()//2, Config.HEIGHT//2 - text_surf.get_height()//2)

        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx or dy:
                    surface.blit(outline_surf, (pos[0] + dx, pos[1] + dy))
        surface.blit(text_surf, pos)

    def draw_menu(self, surface: pygame.Surface):
        """
        Desenha o menu principal.
        """
        # Fundo semi-transparente
        overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Container do menu
        menu_width = 780
        menu_height = 450
        menu_rect = pygame.Rect(
            (Config.WIDTH - menu_width) // 2,
            (Config.HEIGHT - menu_height) // 2,
            menu_width,
            menu_height
        )
        pygame.draw.rect(surface, Config.DARK_GOLD, menu_rect, border_radius=20)
        pygame.draw.rect(surface, Config.GOLD, menu_rect, 3, border_radius=20)

        # Título
        title = self.fonts['large'].render("GOL A GOL", True, Config.WHITE)
        surface.blit(title, (
            Config.WIDTH//2 - title.get_width()//2,
            menu_rect.y + 15
        ))

        # Elementos do menu
        elements_y = menu_rect.y + 70
        spacing = 60

        # Nome Jogador 1
        self._draw_menu_input(surface, "Player 1:", self.state.player1_name,
                            elements_y, 'player1')
        # Nome Jogador 2
        self._draw_menu_input(surface, "Player 2:", self.state.player2_name,
                            elements_y + spacing, 'player2')
        # Tempo de Jogo
        self._draw_time_buttons(surface, elements_y + spacing * 2)

        # Botão Iniciar
        self._draw_menu_button(surface, "GAME START", elements_y + spacing * 3)

        # Botão Controles
        self._draw_controls_button(surface, elements_y + spacing * 4)

        # Botão Mute
        self.mute_rect = self._draw_mute_button(surface, elements_y + spacing * 5)

    def _draw_mute_button(self, surface, y):
        button_rect = pygame.Rect(
            Config.WIDTH // 2 - 100,
            y,
            200,
            50
        )

        pygame.draw.rect(surface, Config.GOLD, button_rect, border_radius=20)
        pygame.draw.rect(surface, Config.WHITE, button_rect, 3, border_radius=20)
        mute_text = self.fonts['small'].render("MUTE", True, Config.WHITE)
        mute_text_rect = mute_text.get_rect(center=button_rect.center)
        surface.blit(mute_text, mute_text_rect)

        if button_rect.collidepoint(pygame.mouse.get_pos()):
            if self.hovered_button != button_rect:
                self.sound_manager.play_button_hover_sound()
                self.hovered_button = button_rect
        elif self.hovered_button == button_rect:
            self.hovered_button = None

        return button_rect

    def _draw_controls_button(self, surface, y):
        button_rect = pygame.Rect(
            Config.WIDTH // 2 - 100,
            y,
            200,
            50
        )
        pygame.draw.rect(surface, Config.GOLD, button_rect, border_radius=20)
        pygame.draw.rect(surface, Config.WHITE, button_rect, 3, border_radius=20)
        text_surf = self.fonts['small'].render("CONTROLS", True, Config.WHITE)
        text_rect = text_surf.get_rect(center=button_rect.center)
        surface.blit(text_surf, text_rect)

        if button_rect.collidepoint(pygame.mouse.get_pos()):
            if self.hovered_button != button_rect:
                self.sound_manager.play_button_hover_sound()
                self.hovered_button = button_rect
        elif self.hovered_button == button_rect:
            self.hovered_button = None

        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            if self.hovered_button != button_rect:
                self.sound_manager.play_button_hover_sound()
                self.hovered_button = button_rect
        elif self.hovered_button == button_rect:
            self.hovered_button = None

    def draw_controls_menu(self, surface: pygame.Surface):
        # Fundo semi-transparente
        overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Container do menu
        menu_width = 780
        menu_height = 450
        menu_rect = pygame.Rect(
            (Config.WIDTH - menu_width) // 2,
            (Config.HEIGHT - menu_height) // 2,
            menu_width,
            menu_height
        )
        pygame.draw.rect(surface, Config.DARK_GOLD, menu_rect, border_radius=20)
        pygame.draw.rect(surface, Config.GOLD, menu_rect, 3, border_radius=20)

        # Título
        title = self.fonts['large'].render("CONTROLS", True, Config.WHITE)
        title_y = menu_rect.y + 30  # Posição ajustada
        surface.blit(title, (Config.WIDTH // 2 - title.get_width() // 2, title_y))

        # Configurações Player 1
        self._draw_control_option(
            surface, "Player 1:",
            [("WASD", "wasd"), ("Virtual", "virtual")],
            self.state.player1_control,
            menu_rect.y + 100
        )

        # Botão de calibração (só aparece se virtual estiver selecionado)
        if self.state.player1_control == "virtual":
            self._draw_calibration_button(surface, menu_rect.y + 150)

        # Configurações Player 2
        self._draw_control_option(
            surface, "Player 2:",
            [("Setas", "arrows"), ("CPU", "cpu")],
            self.state.player2_control,
            menu_rect.y + 250
        )

        # Botão Voltar
        self._draw_back_button(surface, menu_rect.y + 380)

    def _draw_control_option(self, surface, label, options, current, y):
        font = self.fonts['small']
        # Centralizar verticalmente com os botões
        label_y = y + 20 - font.get_height() // 2
        label_text = font.render(label, True, Config.WHITE)
        surface.blit(label_text, (Config.WIDTH // 2 - 350, label_y))

        for i, (display_text, value) in enumerate(options):
            # Ajuste fino no posicionamento
            rect = pygame.Rect(
                Config.WIDTH // 2 - 90 + i * 180,
                y + 5,
                170,
                30
            )
            # Comparar com o valor (value) em vez do texto exibido
            color = Config.GOLD if current == value else Config.WHITE
            pygame.draw.rect(surface, color, rect, border_radius=8)
            text = font.render(display_text, True, Config.BLACK)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)

    def _draw_back_button(self, surface, y):
        button_rect = pygame.Rect(
            Config.WIDTH // 2 - 100,
            y + 10,
            200,
            50
        )
        pygame.draw.rect(surface, Config.GOLD, button_rect, border_radius=20)
        pygame.draw.rect(surface, Config.WHITE, button_rect, 3, border_radius=20)
        text_surf = self.fonts['small'].render("BACK", True, Config.WHITE)
        text_rect = text_surf.get_rect(center=button_rect.center)
        surface.blit(text_surf, text_rect)

        if button_rect.collidepoint(pygame.mouse.get_pos()):
            if self.hovered_button != button_rect:
                self.sound_manager.play_button_hover_sound()
                self.hovered_button = button_rect
        elif self.hovered_button == button_rect:
            self.hovered_button = None

    def _draw_menu_input(self, surface, label, value, y, field_id):
        """
        Desenha um campo de entrada no menu.
        """
        font = self.fonts['small']
        label_text = font.render(label, True, Config.WHITE)
        label_y = y + 20 - label_text.get_height() // 2
        surface.blit(label_text, (Config.WIDTH//2 - 300, label_y))

        input_rect = pygame.Rect(
            Config.WIDTH//2 - 50,
            y,
            300,
            40
        )
        color = Config.GOLD if self.state.input_active == field_id else Config.WHITE
        pygame.draw.rect(surface, color, input_rect, 2, border_radius=10)

        # Exibe "Insira seu nome" se o campo estiver vazio e não estiver ativo
        displayed_text = value if (self.state.input_active == field_id or value) else "Insert name"
        text = font.render(displayed_text, True, Config.WHITE)
        text_rect = text.get_rect(center=input_rect.center)
        surface.blit(text, text_rect)

    def _draw_time_buttons(self, surface, y):
        """
        Desenha os botões de seleção de tempo de jogo.
        """
        font = self.fonts['small']
        label_text = font.render("Time Game:", True, Config.WHITE)
        label_y = y + 20 - label_text.get_height() // 2  # Centralizar verticalmente
        surface.blit(label_text, (Config.WIDTH//2 - 300, label_y))

        options = ['1 MIN', '3 MIN', '5 MIN']
        x_pos = Config.WIDTH//2 - 50
        for i, opt in enumerate(options):
            rect = pygame.Rect(x_pos + i*140, y, 110, 40)
            color = Config.GOLD if Config.TIME_OPTIONS[i] == self.state.selected_duration else Config.WHITE
            pygame.draw.rect(surface, color, rect, 2, border_radius=10)
            text = font.render(opt, True, Config.WHITE)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)

    def _draw_menu_button(self, surface, text, y):
        button_rect = pygame.Rect(
            Config.WIDTH//2 - 100,
            y,
            200,
            50
        )
        pygame.draw.rect(surface, Config.GOLD, button_rect, border_radius=20)
        pygame.draw.rect(surface, Config.WHITE, button_rect, 3, border_radius=20)
        text_surf = self.fonts['small'].render(text, True, Config.WHITE)
        text_rect = text_surf.get_rect(center=button_rect.center)
        surface.blit(text_surf, text_rect)

        if button_rect.collidepoint(pygame.mouse.get_pos()):
            if self.hovered_button != button_rect:
                self.sound_manager.play_button_hover_sound()
                self.hovered_button = button_rect
        elif self.hovered_button == button_rect:
            self.hovered_button = None

    def _draw_calibration_button(self, surface, y):
        button_rect = pygame.Rect(
            Config.WIDTH // 2 - 100,
            y,
            200,
            40
        )

        # Cor diferente para indicar estado
        if hasattr(self.state, 'is_calibrating') and self.state.is_calibrating:
            color = Config.BLUE
            text = "CALIBRANDO..."
        else:
            color = Config.GOLD
            text = "CALIBRAR"

        pygame.draw.rect(surface, color, button_rect, border_radius=10)
        pygame.draw.rect(surface, Config.WHITE, button_rect, 2, border_radius=10)
        text_surf = self.fonts['small'].render(text, True, Config.WHITE)
        text_rect = text_surf.get_rect(center=button_rect.center)
        surface.blit(text_surf, text_rect)

        # Mostrar status da calibração
        if hasattr(self.state, 'head_tracker') and self.state.head_tracker:
            status_text = self.state.head_tracker.get_calibration_status()
            status_surf = self.fonts['small'].render(status_text, True, Config.WHITE)
            surface.blit(status_surf, (button_rect.x, button_rect.y + 45))

        # Verificar hover/clique
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            if self.hovered_button != button_rect:
                self.sound_manager.play_button_hover_sound()
                self.hovered_button = button_rect
        elif self.hovered_button == button_rect:
            self.hovered_button = None

        return button_rect

    # Adicione este método à classe UIManager
    def draw_calibration_screen(self, surface: pygame.Surface, frame):
        """Mostra a tela de calibração com feedback visual"""
        # Fundo escuro semi-transparente
        overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Converter frame OpenCV para superficie pygame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (640, 480))
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

        # Posicionar a visualização da câmera
        surface.blit(frame_surface, (Config.WIDTH // 2 - 320, Config.HEIGHT // 2 - 240))

        # Instruções
        font = self.fonts['large']
        text = font.render("Mova sua cabeça em todas as direções", True, Config.WHITE)
        surface.blit(text, (Config.WIDTH // 2 - text.get_width() // 2, Config.HEIGHT // 2 - 300))

        # Botão para finalizar
        button_rect = pygame.Rect(Config.WIDTH // 2 - 100, Config.HEIGHT // 2 + 260, 200, 50)
        pygame.draw.rect(surface, Config.GOLD, button_rect, border_radius=10)
        pygame.draw.rect(surface, Config.WHITE, button_rect, 2, border_radius=10)
        text = self.fonts['small'].render("FINALIZAR", True, Config.WHITE)
        surface.blit(text, (button_rect.centerx - text.get_width() // 2, button_rect.centery - text.get_height() // 2))

        return button_rect