# Space Shooter 🚀

Jogo de nave estilo Shoot 'em Up desenvolvido em Python com PyGame para o Projeto Final de Design de Software — Insper (2026.1).

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyGame](https://img.shields.io/badge/PyGame-2.5+-green)

## Autores

- Victor Mota
- Felipe Schenkman
- Gustavo Schmidt

## Descrição

Space Shooter é um jogo arcade onde o jogador controla uma nave espacial e deve sobreviver a ondas de inimigos cada vez mais difíceis. O jogo conta com:

- **Sistema de waves** com dificuldade progressiva
- **Boss fights** a cada 5 waves, com padrões de tiro e vida escaláveis
- **3 tipos de power-ups**: tiro triplo, escudo protetor e bomba
- **Sistema de partículas** para explosões
- **Parallax scrolling** com estrelas em camadas e nebulosas
- **Efeitos sonoros** e música de fundo
- **Leaderboard** com ranking top 10 salvo em arquivo
- **Múltiplas telas**: menu, instruções, jogo, game over e ranking

## Como executar

### Pré-requisitos

- Python 3.10 ou superior
- PyGame 2.5 ou superior

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/victorbouissoumota/space-shooter.git
cd space-shooter
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o jogo:
```bash
python main.py
```

## Controles

| Tecla | Ação |
|---|---|
| Setas / WASD | Movimentar a nave |
| Espaço | Atirar |
| ESC | Voltar ao menu / Sair |
| Enter | Confirmar seleção |

## Power-ups

| Item | Efeito | Duração |
|---|---|---|
| Triângulo amarelo | Tiro triplo (dispara 3 projéteis) | 5 segundos |
| Círculo azul | Escudo protetor (absorve 1 golpe) | 6 segundos |
| Quadrado vermelho | Bomba (destrói todos os inimigos na tela) | Instantâneo |

## Estrutura do projeto

```
space-shooter/
├── main.py              # Código principal do jogo (arquivo único)
├── requirements.txt     # Dependências (pygame)
├── leaderboard.json     # Ranking de pontuações (gerado automaticamente)
├── README.md            # Este arquivo
├── .gitignore           # Arquivos ignorados pelo Git
└── assets/
    ├── sounds/          # Efeitos sonoros (.wav)
    │   ├── shoot.wav
    │   ├── explosion.wav
    │   ├── player_hit.wav
    │   ├── powerup.wav
    │   ├── bomb.wav
    │   ├── boss_hit.wav
    │   ├── boss_death.wav
    │   ├── menu_select.wav
    │   ├── menu_confirm.wav
    │   ├── game_over.wav
    │   └── wave_start.wav
    └── music/           # Música de fundo
        └── background.ogg
```

## Arquitetura do código

O jogo foi desenvolvido utilizando orientação a objetos com as seguintes classes principais:

- **Game** — Gerencia o loop principal e os estados do jogo (menu, instruções, gameplay, game over, leaderboard)
- **Player** — Nave do jogador com movimentação, tiro, invencibilidade e power-ups
- **Enemy** — Inimigos com velocidade e cores aleatórias
- **Boss** — Chefe com barra de vida, padrões de tiro e dificuldade escalável
- **Bullet / BossBullet** — Projéteis do jogador e do boss
- **PowerUp** — Itens coletáveis (tiro triplo, escudo, bomba)
- **Particle / Explosion** — Sistema de partículas para efeitos visuais
- **WaveManager** — Controla as ondas de inimigos com dificuldade progressiva
- **Background / Star / Nebula** — Fundo com parallax scrolling em camadas
- **SoundManager** — Carrega e toca efeitos sonoros e música
- **Leaderboard** — Ranking persistente salvo em JSON

## Vídeo(ainda falta adicionar)

[Link do vídeo demonstrativo](URL_DO_VIDEO)

## Uso de IA Generativa

Este projeto utilizou o Claude (Anthropic) como ferramenta de apoio no desenvolvimento. A IA auxiliou na estruturação do código, implementação de funcionalidades e resolução de bugs. Todo o código foi revisado, testado e compreendido pelos integrantes do grupo antes de ser incorporado ao projeto.
# PyGame-Mota-Sheik