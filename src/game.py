import pygame
import sys
from .config import Config
from .game_state import GameState
from .sound_manager import SoundManager
from .ui_manager import UIManager
from .ball import Ball
from .paddle import Paddle
from .physics_engine import PhysicsEngine
from .input_handler import InputHandler


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
            Paddle("assets/imagens/player1.png", (
                Config.FIELD_OFFSET_X,
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH // 2,
                Config.FIELD_OFFSET_Y,
                Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT
            )),
            Paddle("assets/imagens/player2.png", (
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH // 2,
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH,
                Config.FIELD_OFFSET_Y,
                Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT
            ),  ball=self.ball)
        ]
        self.paddles[0].rect.topleft = (Config.FIELD_OFFSET_X + 50, Config.HEIGHT//2 - Config.PADDLE_HEIGHT//2)
        self.paddles[1].rect.topleft = (Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 50 - Config.PADDLE_WIDTH, Config.HEIGHT//2 - Config.PADDLE_HEIGHT//2)

        self.clock = pygame.time.Clock()
        self.timer_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.timer_event, 1000)

    def reset(self):
        """
        Reseta o estado do jogo.
        """
        self.state.reset()
        self.ball.reset()
        self.paddles = [
            Paddle("assets/imagens/player1.png", (
                Config.FIELD_OFFSET_X,
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH//2,
                Config.FIELD_OFFSET_Y,
                Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT
            )),
            Paddle("assets/imagens/player2.png", (
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH//2,
                Config.FIELD_OFFSET_X + Config.FIELD_WIDTH,
                Config.FIELD_OFFSET_Y,
                Config.FIELD_OFFSET_Y + Config.FIELD_HEIGHT
            ), ball=self.ball)
        ]

        self.paddles[0].rect.topleft = (Config.FIELD_OFFSET_X + 50, Config.HEIGHT//2 - Config.PADDLE_HEIGHT//2)
        self.paddles[1].rect.topleft = (Config.FIELD_OFFSET_X + Config.FIELD_WIDTH - 50 - Config.PADDLE_WIDTH, Config.HEIGHT//2 - Config.PADDLE_HEIGHT//2)

    def run(self):
        """
        Inicia o loop principal do jogo.
        """
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(60)

    def _handle_events(self):
        """
        Lida com os eventos do jogo.
        """
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
        """
        Atualiza o estado do jogo.
        """
        if self.state.game_started and not self.state.game_over and not self.state.is_paused:
            self._move_players()
            self.ball.update()
            result = PhysicsEngine.handle_collisions(self.ball, self.paddles, self.sound_manager, self)
            if result == "player1":
                self.state.player1_score += 1
                self.ball.reset(-1)
            elif result == "player2":
                self.state.player2_score += 1
                self.ball.reset(1)

    def _move_players(self):
        """
        Move os jogadores de acordo com as teclas pressionadas.
        """
        if self.state.is_paused:
            return

        keys = pygame.key.get_pressed()

        # Player 1
        dx, dy = 0, 0
        if self.state.player1_control == "wasd":
            if keys[pygame.K_w]: dy -= Config.PLAYER_SPEED
            if keys[pygame.K_s]: dy += Config.PLAYER_SPEED
            if keys[pygame.K_a]: dx -= Config.PLAYER_SPEED
            if keys[pygame.K_d]: dx += Config.PLAYER_SPEED

        self.paddles[0].move(dx, dy)

        # Player 2
        if self.state.player2_control == "arrows":
            dx, dy = 0, 0
            if keys[pygame.K_UP]: dy -= Config.PLAYER_SPEED
            if keys[pygame.K_DOWN]: dy += Config.PLAYER_SPEED
            if keys[pygame.K_LEFT]: dx -= Config.PLAYER_SPEED
            if keys[pygame.K_RIGHT]: dx += Config.PLAYER_SPEED
            self.paddles[1].move(dx, dy)
        elif self.state.player2_control == "cpu":
            self.paddles[1].cpu_move()

    def _draw(self):
        """
        Desenha todos os elementos do jogo na tela.
        """
        self.window.fill(Config.BLACK)
        self.ui.draw_field(self.window)

        for paddle in self.paddles:
            self.window.blit(paddle.image, paddle.rect)

        self.ball.draw(self.window)
        self.ui.draw_scoreboard(self.window)

        # Corrigir aqui todas as referências para self.state
        if self.state.controls_menu_active:
            self.ui.draw_controls_menu(self.window)
        elif self.state.menu_active:
            self.ui.draw_menu(self.window)
        elif self.state.game_over:
            self.ui.draw_end_game(self.window)

        pygame.display.flip()

    def __del__(self):
        for paddle in self.paddles:
            paddle.disable_head_tracking()