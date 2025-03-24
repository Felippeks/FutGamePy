import pygame
import numpy as np
from .asset_loader import AssetLoader

class SoundManager:
    def __init__(self):
        # Configurar canais dedicados
        pygame.mixer.set_num_channels(4)
        self.channel_start = pygame.mixer.Channel(0)
        self.channel_effects = pygame.mixer.Channel(1)
        self.channel_goal = pygame.mixer.Channel(2)
        self.background_channel = pygame.mixer.Channel(3)
        self.is_muted = False

        # Primeiro carregar todos os sons
        self._load_sounds()
        
        # Depois acelerar
        self._speed_up_sounds()

        # Configurar prioridades
        self.channel_start.set_volume(1.0)
        self.channel_effects.set_volume(0.8)
        
        # Iniciar som de fundo
        self.background_channel.play(self.background_sound, loops=-1)

    def toggle_mute(self):
        """
        Alterna o estado de mute (mudo) do som.
        """
        self.is_muted = not self.is_muted
        self.set_volume(0 if self.is_muted else 1.0)

    def set_volume(self, volume: float):
        """
        Define o volume dos canais de som.
        """
        self.channel_start.set_volume(volume)
        self.channel_effects.set_volume(volume * 0.8)
        self.channel_goal.set_volume(volume)
        self.background_channel.set_volume(volume * 0.3)

    def _load_sounds(self):
        """
        Carrega todos os recursos de áudio.
        """
        try:
            # Carregar sons
            self.goal_sound = pygame.mixer.Sound(AssetLoader.resource_path("assets/sons/goal.wav"))
            self.collision_sound = pygame.mixer.Sound(AssetLoader.resource_path("assets/sons/collision.wav"))
            self.button_click_sound = pygame.mixer.Sound(AssetLoader.resource_path("assets/sons/button_click.wav"))
            self.button_hover_sound = pygame.mixer.Sound(AssetLoader.resource_path("assets/sons/button_hover.wav"))
            self.start_sound = pygame.mixer.Sound(AssetLoader.resource_path("assets/sons/start.wav"))
            self.background_sound = pygame.mixer.Sound(AssetLoader.resource_path("assets/sons/background.wav"))

            # Configurar volumes
            self.start_sound.set_volume(1.0)
            self.button_hover_sound.set_volume(0.7)
            self.button_click_sound.set_volume(0.7)
            self.goal_sound.set_volume(1.0)
            self.collision_sound.set_volume(0.5)
            self.background_sound.set_volume(0.3)
            
        except Exception as e:
            print(f"Erro ao carregar sons: {e}")
            raise SystemExit  # Encerra o jogo se não carregar os sons

        # Pré-aquecer os buffers
        self.start_sound.play().stop()
        self.button_hover_sound.play().stop()
        self.button_click_sound.play().stop()
        self.goal_sound.play().stop()
        self.collision_sound.play().stop()

    def _speed_up_sounds(self):
        """
        Acelera os sons carregados.
        """
        try:
            self.goal_sound = self._adjust_speed(self.goal_sound, 2.0)
            self.collision_sound = self._adjust_speed(self.collision_sound, 2.0)
            self.button_click_sound = self._adjust_speed(self.button_click_sound, 2.0)
            self.button_hover_sound = self._adjust_speed(self.button_hover_sound, 2.0)
            self.start_sound = self._adjust_speed(self.start_sound, 2.0)
        except Exception as e:
            print(f"Erro ao acelerar sons: {e}")

    def _adjust_speed(self, sound, speed_factor):
        """
        Ajusta a velocidade de reprodução de um som.
        """
        array = pygame.sndarray.array(sound)
        
        # Reduz o número de samples para simular aumento de velocidade
        new_length = int(len(array) / speed_factor)
        if new_length == 0:
            new_length = 1  # Evitar divisão por zero
        indices = np.linspace(0, len(array) - 1, num=new_length).astype(int)
        sped_up = array[indices]
        
        return pygame.sndarray.make_sound(sped_up)

    def play_goal_sound(self):
        """
        Reproduz o som de gol.
        """
        self.channel_goal.play(self.goal_sound)  # Usar o canal dedicado

    def play_collision_sound(self):
        """
        Reproduz o som de colisão.
        """
        self.channel_effects.play(self.collision_sound)

    def play_button_click_sound(self):
        """
        Reproduz o som de clique de botão.
        """
        self.channel_start.play(self.button_click_sound)

    def play_button_hover_sound(self):
        """
        Reproduz o som de hover de botão.
        """
        self.channel_start.play(self.button_hover_sound)

    def play_start_sound(self):
        """
        Reproduz o som de início de jogo.
        """
        self.channel_start.play(self.start_sound)