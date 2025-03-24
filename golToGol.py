import pygame
import sys
import os
import random
import math
import numpy as np
import pygame.sndarray
from typing import Tuple, Optional

# Configurações principais
class Config:
    WIDTH, HEIGHT = 1600, 1000
    FIELD_OFFSET_X, FIELD_OFFSET_Y = 100, 50
    FIELD_WIDTH, FIELD_HEIGHT = 1400, 900
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GOLD = (255, 215, 0)
    DARK_GOLD = (218, 165, 32)
    BLUE = (0, 0, 255)
    PADDLE_WIDTH, PADDLE_HEIGHT = 65, 80
    PLAYER_SPEED = 7
    BALL_SIZE = 50
    BALL_SPEED = 8
    GOAL_HEIGHT = 150
    BUTTON_WIDTH, BUTTON_HEIGHT = 150, 37
    NAME_FIELD_WIDTH = 300
    FONT_SIZES = {'normal': 20, 'small': 16, 'large': 36}
    TIME_OPTIONS = [60, 180, 300]

class AssetLoader:
    @staticmethod
    def resource_path(relative_path: str) -> str:
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    @staticmethod
    def load_font(name: str, size: int) -> pygame.font.Font:
        return pygame.font.Font(AssetLoader.resource_path(name), size)

    @staticmethod
    def load_image(path: str, size: Tuple[int, int] = None) -> pygame.Surface:
        img = pygame.image.load(AssetLoader.resource_path(path))
        return pygame.transform.scale(img, size) if size else img

class GameState:
    def __init__(self):
        pygame.init()
        self.reset()
        
    def reset(self):
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


class SoundManager:
    def __init__(self):
        # Configurar canais dedicados
        pygame.mixer.set_num_channels(4)
        self.channel_start = pygame.mixer.Channel(0)
        self.channel_effects = pygame.mixer.Channel(1)
        self.channel_goal = pygame.mixer.Channel(2)


        # Modificação para acelerar os sons
        self._speed_up_sounds()

        # Configurar prioridades
        self.channel_start.set_volume(1.0)
        self.channel_effects.set_volume(0.8)

        # Carregar sons
        self.goal_sound = pygame.mixer.Sound(AssetLoader.resource_path("sons/goal.wav"))
        self.collision_sound = pygame.mixer.Sound(AssetLoader.resource_path("sons/collision.wav"))
        self.button_click_sound = pygame.mixer.Sound(AssetLoader.resource_path("sons/button_click.wav"))
        self.button_hover_sound = pygame.mixer.Sound(AssetLoader.resource_path("sons/button_hover.wav"))
        self.start_sound = pygame.mixer.Sound(AssetLoader.resource_path("sons/start.wav"))


        self.start_sound.set_volume(1.0)
        self.button_hover_sound.set_volume(0.7)
        self.button_click_sound.set_volume(0.7)
        self.goal_sound.set_volume(1.0)
        self.collision_sound.set_volume(0.5)

        # Pré-aquecer os buffers
        self.start_sound.play().stop()
        self.button_hover_sound.play().stop()
        self.button_click_sound.play().stop()
        self.goal_sound.play().stop()
        self.collision_sound.play().stop()


    def _speed_up_sounds(self):
        try:
            self.goal_sound = self._adjust_speed(self.goal_sound, 2.0)
            self.collision_sound = self._adjust_speed(self.collision_sound, 2.0)
            self.button_click_sound = self._adjust_speed(self.button_click_sound, 2.0)
            self.button_hover_sound = self._adjust_speed(self.button_hover_sound, 2.0)
            self.start_sound = self._adjust_speed(self.start_sound, 2.0)
        except Exception as e:
            print(f"Erro ao acelerar sons: {e}")

    def _adjust_speed(self, sound, speed_factor):
        array = pygame.sndarray.array(sound)
        
        # Reduz o número de samples para simular aumento de velocidade
        new_length = int(len(array) / speed_factor)
        indices = np.linspace(0, len(array), num=new_length).astype(int)
        sped_up = array[indices]
        
        return pygame.sndarray.make_sound(sped_up)


    def play_goal_sound(self):
        self.channel_goal.play(self.goal_sound)  # Usar o canal dedicado

    def play_collision_sound(self):
        self.channel_effects.play(self.collision_sound)

    def play_button_click_sound(self):
        self.channel_start.play(self.button_click_sound)

    def play_button_hover_sound(self):
        self.channel_start.play(self.button_hover_sound)

    def play_start_sound(self):  
        self.channel_start.play(self.start_sound)

class Ball:
    def __init__(self):
        self.original_image = AssetLoader.load_image("imagens/soccer_ball.png")
        self.image = self._create_circular_surface()
        self.reset()

    def _create_circular_surface(self) -> pygame.Surface:
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
        
    def _apply_circular_mask(self, surface: pygame.Surface, size: int):
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255,255,255,255), (size//2, size//2), size//2)
        surface.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

    def reset(self, direction: int = 1):
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
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y # type: ignore
        self.angle += self.rotation_speed

    def draw(self, surface: pygame.Surface):
        rotated = pygame.transform.rotate(self.image, self.angle)
        surface.blit(rotated, rotated.get_rect(center=self.rect.center))

class Paddle:
    def __init__(self, image_path: str, constraints: Tuple[int, int, int, int]):
        self.image = AssetLoader.load_image(image_path, 
            (Config.PADDLE_WIDTH, Config.PADDLE_HEIGHT))
        self.rect = pygame.Rect(0, 0, Config.PADDLE_WIDTH, Config.PADDLE_HEIGHT)
        self.constraints = constraints

    def move(self, dx: int, dy: int):
        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = max(min(self.rect.x, self.constraints[1] - self.rect.width), self.constraints[0])
        self.rect.y = max(min(self.rect.y, self.constraints[3] - self.rect.height), self.constraints[2])

class PhysicsEngine:
    @staticmethod
    def handle_collisions(ball: Ball, paddles: list[Paddle], sound_manager: SoundManager):
        if ball.rect.top <= Config.FIELD_OFFSET_Y:
            ball.rect.top = Config.FIELD_OFFSET_Y
            ball.speed_y *= -1
            sound_manager.play_collision_sound()
        elif ball.rect.bottom >= Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT:
            ball.rect.bottom = Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT
            ball.speed_y *= -1
            sound_manager.play_collision_sound()

        for paddle in paddles:
            dx = ball.rect.centerx - paddle.rect.centerx
            dy = ball.rect.centery - paddle.rect.centery
            distance = math.hypot(dx, dy)
            
            if distance < (Config.BALL_SIZE//2 + max(paddle.rect.width, paddle.rect.height)//2):
                angle = math.atan2(dy, dx)
                ball.speed_x = Config.BALL_SPEED * math.cos(angle) # type: ignore
                ball.speed_y = Config.BALL_SPEED * math.sin(angle)
                ball.rotation_speed = random.uniform(-8, 8)
                sound_manager.play_collision_sound()

        if ball.rect.left <= Config.FIELD_OFFSET_X:
            if (Config.HEIGHT - Config.GOAL_HEIGHT)//2 < ball.rect.centery < (Config.HEIGHT + Config.GOAL_HEIGHT)//2:
                sound_manager.play_goal_sound()
                return "player2"
            ball.rect.left = Config.FIELD_OFFSET_X
            ball.speed_x = abs(ball.speed_x)
        elif ball.rect.right >= Config.FIELD_OFFSET_X + Config.FIELD_WIDTH:
            if (Config.HEIGHT - Config.GOAL_HEIGHT)//2 < ball.rect.centery < (Config.HEIGHT + Config.GOAL_HEIGHT)//2:
                sound_manager.play_goal_sound()
                return "player1"
            ball.rect.right = Config.FIELD_OFFSET_X + Config.FIELD_WIDTH
            ball.speed_x = -abs(ball.speed_x)
        return None
class UIManager:
    def __init__(self, state: GameState, sound_manager: SoundManager):
        self.state = state
        self.sound_manager = sound_manager  # Adicione esta linha
        self.hovered_button = None 
        self.fonts = {
            size: AssetLoader.load_font("PressStart2P-Regular.ttf", Config.FONT_SIZES[size])
            for size in ['normal', 'small', 'large']
        }
        self.fonts['button'] = AssetLoader.load_font("PressStart2P-Regular.ttf", 10)
        self.grass = AssetLoader.load_image("imagens/grass.png", 
            (Config.FIELD_WIDTH, Config.FIELD_HEIGHT))
        
        # Carregar imagens dos cabeçalhos
        self.head1 = AssetLoader.load_image("imagens/head1.png", (35, 30))
        self.head2 = AssetLoader.load_image("imagens/head2.png", (35, 30))

    def draw_field(self, surface: pygame.Surface):
        surface.blit(self.grass, (Config.FIELD_OFFSET_X, Config.FIELD_OFFSET_Y))
        self._draw_field_markings(surface)

    def _draw_field_markings(self, surface: pygame.Surface):
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
        self._draw_scores(surface)
        self._draw_timer(surface)
        self._draw_buttons(surface)

        if self.state.is_paused:  
            self._draw_text_with_outline(surface, "PAUSADO", Config.WHITE)

    def _draw_scores(self, surface: pygame.Surface):
        name1 = self.fonts['small'].render(self.state.player1_name, True, Config.WHITE)
        name2 = self.fonts['small'].render(self.state.player2_name, True, Config.WHITE)
        score1 = self.fonts['normal'].render(str(self.state.player1_score), True, Config.WHITE)
        score2 = self.fonts['normal'].render(str(self.state.player2_score), True, Config.WHITE)
        
        # Desenhar nome e placar do Jogador 1 com imagem do cabeçalho
        surface.blit(name1, (Config.WIDTH//4 - name1.get_width()//2, 20))
        surface.blit(self.head1, (Config.WIDTH//4 + name1.get_width()//2 + 20, 10))  # Adicionar imagem do cabeçalho
        surface.blit(score1, (Config.WIDTH//4 + name1.get_width()//2 + 90, 18))  # Mais espaço
        
        # Desenhar nome e placar do Jogador 2 com imagem do cabeçalho
        surface.blit(name2, (3*Config.WIDTH//4 - name2.get_width()//2, 20))
        surface.blit(self.head2, (3*Config.WIDTH//4 + name2.get_width()//2 + 20, 10))  # Adicionar imagem do cabeçalho
        surface.blit(score2, (3*Config.WIDTH//4 + name2.get_width()//2 + 90, 18))  # Mais espaço

    def _draw_timer(self, surface: pygame.Surface):
        timer_text = self.fonts['normal'].render(
            f"{self.state.time_remaining//60}:{self.state.time_remaining%60:02d}", 
            True, Config.WHITE)
        surface.blit(timer_text, (Config.WIDTH//2 - timer_text.get_width()//2, 20))

    def _draw_buttons(self, surface: pygame.Surface):
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
        if self.state.player1_score > self.state.player2_score:
            text, color = f"{self.state.player1_name} Venceu!", Config.DARK_GOLD
        elif self.state.player2_score > self.state.player1_score:
            text, color = f"{self.state.player2_name} Venceu!", Config.DARK_GOLD
        else:
            text, color = "Empate!", Config.BLUE
        
        self._draw_text_with_outline(surface, text, color)

    def _draw_text_with_outline(self, surface: pygame.Surface, text: str, color: Tuple[int, int, int]):
        text_surf = self.fonts['large'].render(text, True, color)
        outline_surf = self.fonts['large'].render(text, True, Config.BLACK)
        pos = (Config.WIDTH//2 - text_surf.get_width()//2, Config.HEIGHT//2 - text_surf.get_height()//2)
        
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx or dy:
                    surface.blit(outline_surf, (pos[0] + dx, pos[1] + dy))
        surface.blit(text_surf, pos)

    def draw_menu(self, surface: pygame.Surface):
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

    def _draw_menu_input(self, surface, label, value, y, field_id):
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
class InputHandler:
    @staticmethod
    def _handle_game_click(pos: Tuple[int, int], state: GameState, game):
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
    def handle(event: pygame.event.Event, state: GameState, game):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state.menu_active:
                InputHandler._handle_menu_click(event.pos, state, game)
            else:
                InputHandler._handle_game_click(event.pos, state, game)
                
        elif event.type == pygame.KEYDOWN and state.menu_active:
            InputHandler._handle_menu_key_input(event, state)

    @staticmethod
    def _handle_menu_click(pos: Tuple[int, int], state: GameState, game):
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
    def _handle_mouse_click(pos: Tuple[int, int], state: GameState, game):
        start_rect = pygame.Rect(10, 10, Config.BUTTON_WIDTH, Config.BUTTON_HEIGHT)
        reset_rect = pygame.Rect(Config.WIDTH - Config.BUTTON_WIDTH - 10, 10, 
                               Config.BUTTON_WIDTH, Config.BUTTON_HEIGHT)
        
        if start_rect.collidepoint(pos):
            state.game_started = True
            state.game_over = False
            state.time_remaining = Config.GAME_DURATION
        elif reset_rect.collidepoint(pos):
            game.reset()
    

    @staticmethod
    def _handle_key_input(event: pygame.event.Event, state: GameState):
        if state.input_active == 'player1':
            InputHandler._update_name(event, state.player1_name)
        elif state.input_active == 'player2':
            InputHandler._update_name(event, state.player2_name)

    @staticmethod
    def _update_name(event: pygame.event.Event, name: str):
        if event.key == pygame.K_BACKSPACE:
            name = name[:-1]
        elif event.unicode.isprintable():
            name += event.unicode

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.window = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption("Futebol Game Desktop")
        
        self.state = GameState()
        self.sound_manager = SoundManager()
        self.ui = UIManager(self.state, self.sound_manager)
        self.ball = Ball()
        self.paddles = [
            Paddle("imagens/player1.png", (
                Config.FIELD_OFFSET_X,
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH//2,
                Config.FIELD_OFFSET_Y,
                Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT
            )),
            Paddle("imagens/player2.png", (
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH//2,
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH,
                Config.FIELD_OFFSET_Y,
                Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT
            ))
        ]
        self.paddles[0].rect.topleft = (Config.FIELD_OFFSET_X + 50, Config.HEIGHT//2 - Config.PADDLE_HEIGHT//2)
        self.paddles[1].rect.topleft = (Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 50 - Config.PADDLE_WIDTH, Config.HEIGHT//2 - Config.PADDLE_HEIGHT//2)

        self.clock = pygame.time.Clock()
        self.timer_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.timer_event, 1000)

    def reset(self):
        self.state.reset()
        self.ball.reset()
        self.paddles = [
            Paddle("imagens/player1.png", (
                Config.FIELD_OFFSET_X,
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH//2,
                Config.FIELD_OFFSET_Y,
                Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT
            )),
            Paddle("imagens/player2.png", (
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH//2,
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH,
                Config.FIELD_OFFSET_Y,
                Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT
            ))
        ]

        self.paddles[0].rect.topleft = (Config.FIELD_OFFSET_X + 50, Config.HEIGHT//2 - Config.PADDLE_HEIGHT//2)
        self.paddles[1].rect.topleft = (Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 50 - Config.PADDLE_WIDTH, Config.HEIGHT//2 - Config.PADDLE_HEIGHT//2)

    def run(self):
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(60)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            InputHandler.handle(event, self.state, self)

            if event.type == self.timer_event and self.state.game_started and not self.state.is_paused:
                self.state.time_remaining -= 1
                if self.state.time_remaining <= 0:
                    self.state.game_over = True
                    self.state.game_started = False

    
    def _update(self):
        if self.state.game_started and not self.state.game_over and not self.state.is_paused:
            self._move_players()
            self.ball.update()
            result = PhysicsEngine.handle_collisions(self.ball, self.paddles, self.sound_manager)
            if result == "player1":
                self.state.player1_score += 1
                self.ball.reset(-1)
            elif result == "player2":
                self.state.player2_score += 1
                self.ball.reset(1)

    def _move_players(self):
        if self.state.is_paused:
            return
            
        keys = pygame.key.get_pressed()
        
        # Player 1
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= Config.PLAYER_SPEED
        if keys[pygame.K_s]: dy += Config.PLAYER_SPEED
        if keys[pygame.K_a]: dx -= Config.PLAYER_SPEED
        if keys[pygame.K_d]: dx += Config.PLAYER_SPEED
        self.paddles[0].move(dx, dy)
        
        # Player 2
        dx, dy = 0, 0
        if keys[pygame.K_UP]: dy -= Config.PLAYER_SPEED
        if keys[pygame.K_DOWN]: dy += Config.PLAYER_SPEED
        if keys[pygame.K_LEFT]: dx -= Config.PLAYER_SPEED
        if keys[pygame.K_RIGHT]: dx += Config.PLAYER_SPEED
        self.paddles[1].move(dx, dy)

    def _draw(self):
        self.window.fill(Config.BLACK)
        self.ui.draw_field(self.window)
        
        for paddle in self.paddles:
            self.window.blit(paddle.image, paddle.rect)
        
        self.ball.draw(self.window)
        self.ui.draw_scoreboard(self.window)
        
        if self.state.menu_active:
            self.ui.draw_menu(self.window)
        elif self.state.game_over:
            self.ui.draw_end_game(self.window)
        
        pygame.display.flip()

if __name__ == "__main__":
    Game().run()