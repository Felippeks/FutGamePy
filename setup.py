from cx_Freeze import setup, Executable

# Inclua os arquivos de dados necessários
include_files = [
    ('assets/imagens', 'assets/imagens'),
    ('assets/sons', 'assets/sons'),
    ('assets/fonts', 'assets/fonts')
]

# Especificar os pacotes ocultos
packages = ['mediapipe', 'cv2', 'pygame._sdl2']

# Configuração do cx_Freeze
setup(
    name="SeuProjeto",
    version="1.0",
    description="Descrição do seu projeto",
    options={
        'build_exe': {
            'packages': packages,
            'include_files': include_files,
        }
    },
    executables=[Executable('src/main.py', base='Win32GUI')]
)