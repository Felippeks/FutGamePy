import pygame
import sys
import random
import math

# Inicialização do Pygame
pygame.init()
pygame.font.init()

# Configurações da janela
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Futebol Game Desktop")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 100, 0)
GOLD = (255, 215, 0)

# Constantes do jogo
PADDLE_WIDTH = 65
PADDLE_HEIGHT = 80
BALL_SIZE = 40
GOAL_HEIGHT = 150
BALL_SPEED = 5
HITBOX_SCALE = 0.8

# Tamanho dos botões
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 37

class Game:
    def __init__(self):
        # Carregar recursos
        self.soccer_ball = self.load_image("imagens/soccer_ball.png", (BALL_SIZE, BALL_SIZE))
        self.grass = self.load_image("imagens/grass.png", (WIDTH, HEIGHT))
        self.player1_img = self.load_image("imagens/player1.png", (PADDLE_WIDTH, PADDLE_HEIGHT))
        self.player2_img = self.load_image("imagens/player2.png", (PADDLE_WIDTH, PADDLE_HEIGHT))
        
        # Definir o tempo de jogo antes de resetar o jogo
        self.game_time = 60
        
        # Estados do jogo
        self.reset_game()
        
        # UI e fontes
        self.font = pygame.font.Font("PressStart2P-Regular.ttf", 24) if pygame.font.get_init() else None
        self.button_font = pygame.font.Font("PressStart2P-Regular.ttf", 14) if pygame.font.get_init() else None
        self.time_remaining = self.game_time
        self.timer_event = pygame.USEREVENT + 1
        self.player1_name = ""
        self.player2_name = ""
        self.input_active = None
        
        # Controles
        self.keys = {
            'w': False, 's': False, 'a': False, 'd': False,
            'up': False, 'down': False, 'left': False, 'right': False
        }

    def load_image(self, path, size=None):
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size) if size else img

    def reset_game(self):
        # Posições iniciais
        self.paddle1 = pygame.Rect(0, (HEIGHT - PADDLE_HEIGHT)//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.paddle2 = pygame.Rect(WIDTH - PADDLE_WIDTH, (HEIGHT - PADDLE_HEIGHT)//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
        
        # Velocidades e ângulos
        self.ball_speed_x = BALL_SPEED * random.choice([-1, 1])
        self.ball_speed_y = BALL_SPEED * random.uniform(-1, 1)
        self.ball_angle = 0
        self.ball_rotation_speed = random.uniform(-0.1, 0.1)
        
        # Estados do jogo
        self.player1_score = 0
        self.player2_score = 0
        self.game_started = False
        self.time_remaining = self.game_time
        self.game_over = False

    def draw_field(self):
        # Fundo e linhas do campo
        WIN.blit(self.grass, (0, 0))
        
        # Linhas brancas
        pygame.draw.line(WIN, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
        pygame.draw.rect(WIN, WHITE, (0, 0, WIDTH, HEIGHT), 2)
        
        # Gols
        pygame.draw.rect(WIN, GOLD, (0, (HEIGHT - GOAL_HEIGHT)//2, 10, GOAL_HEIGHT))
        pygame.draw.rect(WIN, GOLD, (WIDTH-10, (HEIGHT - GOAL_HEIGHT)//2, 10, GOAL_HEIGHT))
        
        # Áreas de penalidade
        pygame.draw.rect(WIN, WHITE, (0, (HEIGHT - GOAL_HEIGHT)//2 - 50, 100, GOAL_HEIGHT + 100), 2)
        pygame.draw.rect(WIN, WHITE, (WIDTH - 100, (HEIGHT - GOAL_HEIGHT)//2 - 50, 100, GOAL_HEIGHT + 100), 2)
        
        # Círculo central
        pygame.draw.circle(WIN, WHITE, (WIDTH//2, HEIGHT//2), 80, 2)
        pygame.draw.circle(WIN, WHITE, (WIDTH//2, HEIGHT//2), 8)

    def handle_collisions(self):
        hitbox_width = BALL_SIZE * HITBOX_SCALE
        hitbox_height = BALL_SIZE * HITBOX_SCALE
        half_hitbox_w = hitbox_width / 2
        half_hitbox_h = hitbox_height / 2

        # Colisão com bordas
        if self.ball.top <= 0 or self.ball.bottom >= HEIGHT:
            self.ball_speed_y *= -1
            self.ball_rotation_speed = random.uniform(-0.2, 0.2)

        # Colisão com paddles
        for paddle in [self.paddle1, self.paddle2]:
            if self.ball.colliderect(paddle):
                # Cálculo de sobreposição detalhado
                overlap_left = self.ball.right - paddle.left
                overlap_right = paddle.right - self.ball.left
                overlap_top = self.ball.bottom - paddle.top
                overlap_bottom = paddle.bottom - self.ball.top
                
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                
                if min_overlap == overlap_left:
                    self.ball_speed_x = -abs(self.ball_speed_x)
                elif min_overlap == overlap_right:
                    self.ball_speed_x = abs(self.ball_speed_x)
                elif min_overlap == overlap_top:
                    self.ball_speed_y = -abs(self.ball_speed_y)
                else:
                    self.ball_speed_y = abs(self.ball_speed_y)
                
                # Ajuste de velocidade
                self.ball_speed_y += random.uniform(-1, 1)
                self.ball_rotation_speed = random.uniform(-0.2, 0.2)

        # Verificação de gols
        if self.ball.left <= 0:
            if (HEIGHT - GOAL_HEIGHT)//2 < self.ball.centery < (HEIGHT + GOAL_HEIGHT)//2:
                self.player2_score += 1
                self.reset_ball(False)
            else:
                self.ball_speed_x = abs(self.ball_speed_x)
        elif self.ball.right >= WIDTH:
            if (HEIGHT - GOAL_HEIGHT)//2 < self.ball.centery < (HEIGHT + GOAL_HEIGHT)//2:
                self.player1_score += 1
                self.reset_ball(True)
            else:
                self.ball_speed_x = -abs(self.ball_speed_x)

    def reset_ball(self, player1_scored):
        self.ball.center = (WIDTH//2, HEIGHT//2)
        self.ball_speed_x = BALL_SPEED if player1_scored else -BALL_SPEED
        self.ball_speed_y = BALL_SPEED * random.uniform(-1, 1)
        self.ball_angle = 0
        self.ball_rotation_speed = random.uniform(-0.1, 0.1)

    def draw_ui(self):
        # Placar
        score1 = self.font.render(str(self.player1_score), True, WHITE)
        score2 = self.font.render(str(self.player2_score), True, WHITE)
        WIN.blit(score1, (WIDTH//4 - score1.get_width()//2, 20))
        WIN.blit(score2, (3*WIDTH//4 - score2.get_width()//2, 20))

        # Timer
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        timer_text = self.font.render(f"{minutes}:{seconds:02d}", True, WHITE)
        WIN.blit(timer_text, (WIDTH//2 - timer_text.get_width()//2, 20))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Movimento Player 1
        if keys[pygame.K_w] and self.paddle1.top > 0:
            self.paddle1.y -= 7
        if keys[pygame.K_s] and self.paddle1.bottom < HEIGHT:
            self.paddle1.y += 7
        if keys[pygame.K_a] and self.paddle1.left > 0:
            self.paddle1.x -= 7
        if keys[pygame.K_d] and self.paddle1.right < WIDTH//2:
            self.paddle1.x += 7
            
        # Movimento Player 2
        if keys[pygame.K_UP] and self.paddle2.top > 0:
            self.paddle2.y -= 7
        if keys[pygame.K_DOWN] and self.paddle2.bottom < HEIGHT:
            self.paddle2.y += 7
        if keys[pygame.K_LEFT] and self.paddle2.left > WIDTH//2:
            self.paddle2.x -= 7
        if keys[pygame.K_RIGHT] and self.paddle2.right < WIDTH:
            self.paddle2.x += 7

    def draw_buttons(self):
        # Desenhar botão de iniciar
        start_button_rect = pygame.Rect(10, 10, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(WIN, WHITE, start_button_rect)
        start_text = self.button_font.render("Iniciar", True, BLACK)
        WIN.blit(start_text, (start_button_rect.centerx - start_text.get_width()//2, start_button_rect.centery - start_text.get_height()//2))

        # Desenhar botão de reiniciar
        reset_button_rect = pygame.Rect(WIDTH - BUTTON_WIDTH - 10, 10, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(WIN, WHITE, reset_button_rect)
        reset_text = self.button_font.render("Reiniciar", True, BLACK)
        WIN.blit(reset_text, (reset_button_rect.centerx - reset_text.get_width()//2, reset_button_rect.centery - reset_text.get_height()//2))

    def check_button_click(self, pos):
        start_button_rect = pygame.Rect(10, 10, BUTTON_WIDTH, BUTTON_HEIGHT)
        reset_button_rect = pygame.Rect(WIDTH - BUTTON_WIDTH - 10, 10, BUTTON_WIDTH, BUTTON_HEIGHT)
        if start_button_rect.collidepoint(pos):
            self.start_game()
        elif reset_button_rect.collidepoint(pos):
            self.reset_game()

    def draw_end_game_message(self):
        if self.player1_score > self.player2_score:
            winner_text = "Jogador 1 Venceu!"
        elif self.player2_score > self.player1_score:
            winner_text = "Jogador 2 Venceu!"
        else:
            winner_text = "Empate!"

        end_game_text = self.font.render(winner_text, True, WHITE)
        WIN.blit(end_game_text, (WIDTH//2 - end_game_text.get_width()//2, HEIGHT//2 - end_game_text.get_height()//2))

    def run(self):
        clock = pygame.time.Clock()
        pygame.time.set_timer(self.timer_event, 1000)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.check_button_click(event.pos)
                elif event.type == self.timer_event and self.game_started:
                    self.time_remaining -= 1
                    if self.time_remaining <= 0:
                        self.end_game()

            self.handle_input()

            if self.game_started:
                # Movimento da bola
                self.ball.x += self.ball_speed_x
                self.ball.y += self.ball_speed_y
                self.ball_angle += self.ball_rotation_speed
                self.handle_collisions()

            # Renderização
            WIN.fill(BLACK)
            self.draw_field()
            
            # Desenhar elementos
            WIN.blit(self.player1_img, self.paddle1)
            WIN.blit(self.player2_img, self.paddle2)
            
            rotated_ball = pygame.transform.rotate(self.soccer_ball, self.ball_angle)
            WIN.blit(rotated_ball, self.ball.topleft)
            
            self.draw_ui()
            self.draw_buttons()
            if self.game_over:
                self.draw_end_game_message()
            pygame.display.flip()
            clock.tick(60)

    def start_game(self):
        self.reset_game()
        self.game_started = True
        self.time_remaining = self.game_time
        self.game_over = False

    def end_game(self):
        self.game_started = False
        self.game_over = True

if __name__ == "__main__":
    game = Game()
    game.run()