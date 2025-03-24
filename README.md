# Gol a Gol - 2 Player Soccer Game

Um jogo de futebol multiplayer local desenvolvido em Pygame, onde dois jogadores competem para marcar o máximo de gols dentro de um tempo determinado.


## 🎮 Funcionalidades

- **Modo 2 jogadores** (com controles independentes)
- **Sistema de menus interativo**:
  - Personalização de nomes dos jogadores
  - Seleção de duração do jogo (1, 3 ou 5 minutos)
  - Botão de mudo para áudio
- **Física realista**:
  - Colisões dinâmicas entre bola e jogadores
  - Rebote angular da bola
- **Sistema de pontuação e cronômetro**
- **Efeitos sonoros imersivos**:
  - Sons de colisão
  - Comemoração de gol
  - Música de fundo
- **Pausa e retorno ao menu**

## ⚙️ Requisitos

- Python 3.8+
- Pygame 2.1.3+
- NumPy

## 🛠 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/Felippeks/FutGamePy.git
   cd gamePython
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o jogo:
   ```bash
   python -m src.main
   ```
   
4. Estrutura de arquivos necessária:
   ```
   .
    ├── assets/
    │   ├── fonts/
    │   │   └── PressStart2P-Regular.ttf
    │   ├── imagens/
    │   │   ├── soccer_ball.png
    │   │   ├── player1.png
    │   │   ├── player2.png
    │   │   ├── head1.png
    │   │   ├── head2.png
    │   │   └── grass.png
    │   └── sons/
    │       ├── goal.wav
    │       ├── collision.wav
    │       ├── button_click.wav
    │       ├── button_hover.wav
    │       ├── start.wav
    │       └── background.wav
    ├── src/
    │   ├── asset_loader.py
    │   ├── ball.py
    │   ├── config.py
    │   ├── game.py
    │   ├── game_state.py
    │   ├── input_handler.py
    │   ├── paddle.py
    │   ├── physics_engine.py
    │   ├── sound_manager.py
    │   ├── ui_manager.py
    │   ├── __init__.py
    │   └── main.py
   ```

## 🕹 Como Jogar

**Controles:**
- **Jogador 1**:
  - W: Mover para cima
  - S: Mover para baixo
  - A: Mover para esquerda
  - D: Mover para direita

- **Jogador 2**:
  - ↑: Mover para cima
  - ↓: Mover para baixo
  - ←: Mover para esquerda
  - →: Mover para direita

**Objetivo:**  
Marque mais gols que o oponente antes do tempo acabar! A bola deve passar pela área dourada no lado adversário.

**Menu:**
- Insira nomes dos jogadores
- Selecione o tempo de jogo
- Use o botão "Mute" para controlar o áudio
- Clique em "GAME START" para iniciar

## 🎛 Personalização

Edite o arquivo `Config` para ajustar:
- Dimensões da tela
- Velocidades dos jogadores/bola
- Cores e elementos visuais
- Parâmetros de física

Exemplo:
```python
class Config:
    PLAYER_SPEED = 7  # Aumente para movimento mais rápido
    BALL_SPEED = 8    # Altere a velocidade inicial da bola
    TIME_OPTIONS = [60, 180, 300]  # Opções de tempo em segundos
```

**Observações importantes:**
1. Os arquivos de som (.wav) e imagens (.png) precisam ser obtidos separadamente
2. A fonte PressStart2P pode ser baixada gratuitamente em: https://fonts.google.com/specimen/Press+Start+2P
3. Recomendo usar sprites de futebol gratuitos de sites como:
   - https://opengameart.org/
   - https://itch.io/game-assets

**Sugestão de assets gratuitos:**
- Bola de futebol: https://opengameart.org/content/football-ball
- Sons: https://freesound.org/ (busque por "soccer sounds")

**Para criar o executável (opcional):**
Instale o pyinstaller:
```bash
pip install pyinstaller
```

Crie o executável:
```bash
pyinstaller --onefile --windowed --add-data "imagens;imagens" --add-data "sons;sons" --add-data "PressStart2P-Regular.ttf;." main.py
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
