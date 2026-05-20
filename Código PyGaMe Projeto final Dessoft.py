"""
Space Shooter - Jogo de nave estilo Shoot 'em Up.

Desenvolvido em Python com PyGame para o Projeto Final de Design de Software - Insper.

Execute este arquivo para iniciar o jogo:
    python main.py
"""

import pygame
import random
import math
import os
import json

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 700
TITLE = "Space Shooter"
FPS = 60

# Cores (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
DARK_GRAY = (40, 40, 40)
ORANGE = (255, 165, 0)
MAGENTA = (255, 0, 200)
LIGHT_BLUE = (100, 200, 255)
GRAY = (150, 150, 150)
DARK_RED = (150, 0, 0)
PURPLE = (150, 0, 255)

# Jogador
PLAYER_SPEED = 5
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 50
PLAYER_LIVES = 3
PLAYER_INVINCIBLE_TIME = 1500

# Tiros
BULLET_SPEED = -8
BULLET_WIDTH = 4
BULLET_HEIGHT = 12
BULLET_COLOR = YELLOW
SHOOT_DELAY = 250

# Inimigos
ENEMY_WIDTH = 36
ENEMY_HEIGHT = 36

# Explosões
EXPLOSION_PARTICLES = 15
PARTICLE_MIN_SPEED = 1
PARTICLE_MAX_SPEED = 5
PARTICLE_LIFETIME = 500

# Power-ups
POWERUP_SPEED = 2
POWERUP_SIZE = 24
POWERUP_SPAWN_CHANCE = 25
TRIPLE_SHOT_DURATION = 5000
SHIELD_DURATION = 6000
BOMB_FLASH_DURATION = 300

# Waves
WAVE_TRANSITION_DURATION = 3000
BOSS_EVERY_N_WAVES = 5

# Boss
BOSS_WIDTH = 80
BOSS_HEIGHT = 60
BOSS_BASE_HP = 20
BOSS_HP_PER_LEVEL = 10
BOSS_SPEED = 2
BOSS_SHOOT_DELAY = 800
BOSS_BULLET_SPEED = 5

# Estados do jogo
STATE_MENU = "menu"
STATE_INSTRUCTIONS = "instructions"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_LEADERBOARD = "leaderboard"
STATE_INPUT_NAME = "input_name"

# Parallax / Estrelas
STAR_COUNT = 80
PARALLAX_LAYERS = 3

# Leaderboard
LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")
LEADERBOARD_MAX_ENTRIES = 10

# Caminhos de áudio
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "assets", "sounds")
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "assets", "music")


# =============================================================================
# SISTEMA DE LEADERBOARD
# =============================================================================

class Leaderboard:
    """Gerencia o ranking de pontuações salvo em arquivo JSON.

    As pontuações são salvas em um arquivo local e persistem entre
    sessões do jogo. Mantém no máximo as 10 melhores pontuações.

    Attributes:
        filepath: Caminho do arquivo JSON.
        entries: Lista de dicionários com nome, pontuação e wave.
    """

    def __init__(self, filepath=LEADERBOARD_FILE):
        """Inicializa o leaderboard carregando do arquivo.

        Args:
            filepath: Caminho do arquivo de leaderboard.
        """
        self.filepath = filepath
        self.entries = self._load()

    def _load(self):
        """Carrega as pontuações do arquivo JSON.

        Returns:
            list: Lista de entradas do leaderboard.
        """
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data[:LEADERBOARD_MAX_ENTRIES]
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save(self):
        """Salva as pontuações no arquivo JSON."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=2)
        except IOError:
            print("Aviso: não foi possível salvar o leaderboard")

    def add_entry(self, name, score, wave):
        """Adiciona uma nova entrada ao leaderboard.

        A entrada é inserida na posição correta (ordenada por pontuação
        decrescente) e o arquivo é salvo automaticamente.

        Args:
            name: Nome do jogador.
            score: Pontuação obtida.
            wave: Wave alcançada.
        """
        entry = {"name": name, "score": score, "wave": wave}
        self.entries.append(entry)
        self.entries.sort(key=lambda e: e["score"], reverse=True)
        self.entries = self.entries[:LEADERBOARD_MAX_ENTRIES]
        self._save()

    def is_high_score(self, score):
        """Verifica se a pontuação entra no ranking.

        Args:
            score: Pontuação a verificar.

        Returns:
            bool: True se a pontuação entra no top 10.
        """
        if len(self.entries) < LEADERBOARD_MAX_ENTRIES:
            return True
        return score > self.entries[-1]["score"]

    def get_entries(self):
        """Retorna a lista de entradas do leaderboard.

        Returns:
            list: Lista de dicionários com nome, score e wave.
        """
        return self.entries


# =============================================================================
# SISTEMA DE ÁUDIO
# =============================================================================

class SoundManager:
    """Gerencia todos os sons e músicas do jogo.

    Carrega os arquivos de áudio da pasta assets/sounds/ e assets/music/.
    Se algum arquivo não for encontrado, o jogo continua sem aquele som.

    Attributes:
        sounds: Dicionário com os efeitos sonoros carregados.
        music_loaded: Flag que indica se a música foi carregada.
    """

    def __init__(self):
        """Inicializa o gerenciador de sons carregando os arquivos."""
        self.sounds = {}
        self.music_loaded = False

        # Lista de sons esperados: (nome_interno, nome_arquivo)
        sound_files = [
            ("shoot", "shoot.wav"),
            ("explosion", "explosion.wav"),
            ("player_hit", "player_hit.wav"),
            ("powerup", "powerup.wav"),
            ("bomb", "bomb.wav"),
            ("boss_hit", "boss_hit.wav"),
            ("boss_death", "boss_death.wav"),
            ("menu_select", "menu_select.wav"),
            ("menu_confirm", "menu_confirm.wav"),
            ("game_over", "game_over.wav"),
            ("wave_start", "wave_start.wav"),
        ]

        for name, filename in sound_files:
            path = os.path.join(SOUNDS_DIR, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    # Ajusta volumes padrão
                    if name == "shoot":
                        self.sounds[name].set_volume(0.3)
                    elif name == "explosion":
                        self.sounds[name].set_volume(0.4)
                    elif name == "bomb":
                        self.sounds[name].set_volume(0.6)
                    elif name in ("menu_select", "menu_confirm"):
                        self.sounds[name].set_volume(0.5)
                    else:
                        self.sounds[name].set_volume(0.5)
                except pygame.error:
                    print(f"Aviso: não foi possível carregar {filename}")

        # Tenta carregar música de fundo
        music_path = os.path.join(MUSIC_DIR, "background.ogg")
        if not os.path.exists(music_path):
            music_path = os.path.join(MUSIC_DIR, "background.wav")
        if not os.path.exists(music_path):
            music_path = os.path.join(MUSIC_DIR, "background.mp3")

        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.3)
                self.music_loaded = True
            except pygame.error:
                print("Aviso: não foi possível carregar a música de fundo")

    def play(self, name):
        """Toca um efeito sonoro pelo nome.

        Args:
            name: Nome interno do som (ex: 'shoot', 'explosion').
        """
        if name in self.sounds:
            self.sounds[name].play()

    def play_music(self):
        """Inicia a música de fundo em loop."""
        if self.music_loaded:
            pygame.mixer.music.play(-1)  # -1 = loop infinito

    def stop_music(self):
        """Para a música de fundo."""
        if self.music_loaded:
            pygame.mixer.music.stop()

    def pause_music(self):
        """Pausa a música de fundo."""
        if self.music_loaded:
            pygame.mixer.music.pause()

    def unpause_music(self):
        """Retoma a música de fundo."""
        if self.music_loaded:
            pygame.mixer.music.unpause()


# =============================================================================
# SISTEMA DE FUNDO (PARALLAX + ESTRELAS)
# =============================================================================

class Star:
    """Estrela animada para o fundo.

    Attributes:
        x: Posição horizontal.
        y: Posição vertical.
        speed: Velocidade de descida.
        size: Tamanho.
        brightness: Brilho (0-255).
        layer: Camada de parallax.
    """

    def __init__(self, layer=None):
        """Cria uma estrela.

        Args:
            layer: Camada de parallax (None = aleatória).
        """
        self.layer = layer if layer is not None else random.randint(0, PARALLAX_LAYERS - 1)
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        layer_ratio = (self.layer + 1) / PARALLAX_LAYERS
        self.speed = 0.3 + layer_ratio * 2.0
        self.size = max(1, int(layer_ratio * 3))
        self.brightness = int(80 + layer_ratio * 175)

    def update(self):
        """Move a estrela."""
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = random.randint(-10, 0)
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        """Desenha a estrela.

        Args:
            screen: Superfície de desenho.
        """
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class Nebula:
    """Nuvem de nebulosa no fundo.

    Attributes:
        x: Posição horizontal.
        y: Posição vertical.
        width: Largura.
        height: Altura.
        speed: Velocidade de descida.
        color: Cor base.
        surface: Superfície pré-renderizada.
    """

    COLORS = [
        (30, 0, 60), (0, 20, 50), (40, 0, 20),
        (0, 30, 30), (20, 20, 0),
    ]

    def __init__(self):
        """Cria uma nebulosa."""
        self.width = random.randint(100, 250)
        self.height = random.randint(60, 150)
        self.x = random.randint(-50, SCREEN_WIDTH)
        self.y = random.randint(-self.height, SCREEN_HEIGHT)
        self.speed = random.uniform(0.1, 0.4)
        self.color = random.choice(self.COLORS)
        self.surface = self._create_surface()

    def _create_surface(self):
        """Cria superfície da nebulosa.

        Returns:
            pygame.Surface: Superfície com transparência.
        """
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for _ in range(random.randint(3, 6)):
            blob_x = random.randint(10, self.width - 10)
            blob_y = random.randint(10, self.height - 10)
            blob_w = random.randint(30, self.width // 2)
            blob_h = random.randint(20, self.height // 2)
            alpha = random.randint(15, 40)
            blob_color = (*self.color, alpha)
            blob_surface = pygame.Surface((blob_w, blob_h), pygame.SRCALPHA)
            pygame.draw.ellipse(blob_surface, blob_color, (0, 0, blob_w, blob_h))
            surface.blit(blob_surface, (blob_x - blob_w // 2, blob_y - blob_h // 2))
        return surface

    def update(self):
        """Move a nebulosa."""
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = random.randint(-self.height * 2, -self.height)
            self.x = random.randint(-50, SCREEN_WIDTH)
            self.color = random.choice(self.COLORS)
            self.surface = self._create_surface()

    def draw(self, screen):
        """Desenha a nebulosa.

        Args:
            screen: Superfície de desenho.
        """
        screen.blit(self.surface, (int(self.x), int(self.y)))


class Background:
    """Fundo com parallax scrolling.

    Attributes:
        stars: Estrelas em camadas.
        nebulae: Nebulosas.
    """

    def __init__(self):
        """Inicializa o fundo."""
        self.stars = []
        stars_per_layer = STAR_COUNT // PARALLAX_LAYERS
        for layer in range(PARALLAX_LAYERS):
            for _ in range(stars_per_layer):
                self.stars.append(Star(layer))
        self.nebulae = [Nebula() for _ in range(4)]

    def update(self):
        """Atualiza estrelas e nebulosas."""
        for nebula in self.nebulae:
            nebula.update()
        for star in self.stars:
            star.update()

    def draw(self, screen):
        """Desenha o fundo.

        Args:
            screen: Superfície de desenho.
        """
        for nebula in self.nebulae:
            nebula.draw(screen)
        for layer in range(PARALLAX_LAYERS):
            for star in self.stars:
                if star.layer == layer:
                    star.draw(screen)


# =============================================================================
# SISTEMA DE WAVES
# =============================================================================

class WaveManager:
    """Gerencia ondas de inimigos.

    Attributes:
        wave_number: Wave atual.
        enemies_to_spawn: Inimigos para spawnar.
        enemies_alive: Inimigos vivos.
        spawn_delay: Intervalo entre spawns.
        last_spawn: Timestamp do último spawn.
        enemy_min_speed: Velocidade mínima.
        enemy_max_speed: Velocidade máxima.
        max_enemies: Máximo simultâneo.
        transitioning: Flag de transição.
        transition_start: Timestamp da transição.
        is_boss_wave: Flag de boss.
        boss_spawned: Boss criado.
        boss_defeated: Boss derrotado.
    """

    def __init__(self):
        """Inicializa o gerenciador."""
        self.wave_number = 0
        self.enemies_to_spawn = 0
        self.enemies_alive = 0
        self.spawn_delay = 0
        self.last_spawn = 0
        self.enemy_min_speed = 0
        self.enemy_max_speed = 0
        self.max_enemies = 0
        self.transitioning = False
        self.transition_start = 0
        self.is_boss_wave = False
        self.boss_spawned = False
        self.boss_defeated = False

    def start_next_wave(self):
        """Inicia próxima wave."""
        self.wave_number += 1
        self.transitioning = True
        self.transition_start = pygame.time.get_ticks()
        self.last_spawn = pygame.time.get_ticks()
        self.is_boss_wave = (self.wave_number % BOSS_EVERY_N_WAVES == 0)
        self.boss_spawned = False
        self.boss_defeated = False
        if self.is_boss_wave:
            self.enemies_to_spawn = 0
            self.enemies_alive = 1
        else:
            self.enemies_to_spawn = 5 + (self.wave_number * 3)
            self.enemies_alive = self.enemies_to_spawn
            self.spawn_delay = max(300, 800 - (self.wave_number * 50))
            self.enemy_min_speed = min(2 + (self.wave_number * 0.3), 6)
            self.enemy_max_speed = min(5 + (self.wave_number * 0.4), 10)
            self.max_enemies = min(8 + self.wave_number, 15)

    def is_wave_complete(self):
        """Verifica se wave acabou.

        Returns:
            bool: True se completa.
        """
        if self.is_boss_wave:
            return self.boss_defeated
        return self.enemies_to_spawn <= 0 and self.enemies_alive <= 0

    def is_transitioning(self):
        """Verifica transição.

        Returns:
            bool: True se em transição.
        """
        if self.transitioning:
            if pygame.time.get_ticks() - self.transition_start >= WAVE_TRANSITION_DURATION:
                self.transitioning = False
        return self.transitioning

    def enemy_killed(self):
        """Registra inimigo eliminado."""
        self.enemies_alive -= 1

    def enemy_escaped(self):
        """Registra inimigo que escapou."""
        self.enemies_alive -= 1

    def should_spawn(self, current_enemy_count):
        """Verifica se deve spawnar.

        Args:
            current_enemy_count: Inimigos na tela.

        Returns:
            bool: True se deve spawnar.
        """
        if self.is_boss_wave or self.transitioning or self.enemies_to_spawn <= 0:
            return False
        if current_enemy_count >= self.max_enemies:
            return False
        now = pygame.time.get_ticks()
        if now - self.last_spawn >= self.spawn_delay:
            self.last_spawn = now
            self.enemies_to_spawn -= 1
            return True
        return False

    def should_spawn_boss(self):
        """Verifica se deve spawnar boss.

        Returns:
            bool: True se deve spawnar.
        """
        if self.is_boss_wave and not self.boss_spawned and not self.transitioning:
            self.boss_spawned = True
            return True
        return False

    def get_boss_level(self):
        """Retorna nível do boss.

        Returns:
            int: Nível.
        """
        return self.wave_number // BOSS_EVERY_N_WAVES


# =============================================================================
# SPRITES
# =============================================================================

class Player(pygame.sprite.Sprite):
    """Nave do jogador.

    Attributes:
        speed: Velocidade.
        lives: Vidas.
        invincible: Invencibilidade.
        triple_shot: Tiro triplo.
        shield: Escudo.
    """

    def __init__(self, bullet_group, all_sprites_group, sound_manager):
        """Inicializa a nave.

        Args:
            bullet_group: Grupo de tiros.
            all_sprites_group: Grupo geral.
            sound_manager: Gerenciador de sons.
        """
        super().__init__()
        self.original_image = self._create_ship_image()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = PLAYER_SPEED
        self.bullet_group = bullet_group
        self.all_sprites_group = all_sprites_group
        self.sound_manager = sound_manager
        self.last_shot = 0
        self.lives = PLAYER_LIVES
        self.invincible = False
        self.invincible_timer = 0
        self.triple_shot = False
        self.triple_shot_timer = 0
        self.shield = False
        self.shield_timer = 0

    def _create_ship_image(self):
        """Cria sprite da nave.

        Returns:
            pygame.Surface: Superfície da nave.
        """
        surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        body_points = [
            (PLAYER_WIDTH // 2, 0),
            (0, PLAYER_HEIGHT),
            (PLAYER_WIDTH, PLAYER_HEIGHT),
        ]
        pygame.draw.polygon(surface, CYAN, body_points)
        detail_points = [
            (PLAYER_WIDTH // 2, 8),
            (PLAYER_WIDTH // 2 - 8, PLAYER_HEIGHT - 5),
            (PLAYER_WIDTH // 2 + 8, PLAYER_HEIGHT - 5),
        ]
        pygame.draw.polygon(surface, DARK_GRAY, detail_points)
        pygame.draw.circle(surface, WHITE, (PLAYER_WIDTH // 2, 20), 5)
        pygame.draw.rect(surface, YELLOW, (PLAYER_WIDTH // 2 - 5, PLAYER_HEIGHT - 8, 10, 8))
        return surface

    def update(self):
        """Atualiza posição, invencibilidade e power-ups."""
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
        self.rect.x += dx
        self.rect.y += dy
        self._clamp_to_screen()
        self._update_invincibility()
        self._update_powerups()

    def _update_invincibility(self):
        """Gerencia invencibilidade."""
        if self.invincible:
            elapsed = pygame.time.get_ticks() - self.invincible_timer
            if elapsed >= PLAYER_INVINCIBLE_TIME:
                self.invincible = False
                self.image = self.original_image.copy()
            else:
                if (elapsed // 100) % 2 == 0:
                    self.image = self.original_image.copy()
                else:
                    self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)

    def _update_powerups(self):
        """Verifica expiração de power-ups."""
        now = pygame.time.get_ticks()
        if self.triple_shot and now - self.triple_shot_timer >= TRIPLE_SHOT_DURATION:
            self.triple_shot = False
        if self.shield and now - self.shield_timer >= SHIELD_DURATION:
            self.shield = False

    def activate_triple_shot(self):
        """Ativa tiro triplo."""
        self.triple_shot = True
        self.triple_shot_timer = pygame.time.get_ticks()

    def activate_shield(self):
        """Ativa escudo."""
        self.shield = True
        self.shield_timer = pygame.time.get_ticks()

    def hit(self):
        """Processa dano.

        Returns:
            bool: True se ainda vivo.
        """
        if self.invincible:
            return True
        if self.shield:
            self.shield = False
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            self.sound_manager.play("player_hit")
            return True
        self.lives -= 1
        self.invincible = True
        self.invincible_timer = pygame.time.get_ticks()
        self.sound_manager.play("player_hit")
        return self.lives > 0

    def shoot(self):
        """Dispara tiros."""
        now = pygame.time.get_ticks()
        if now - self.last_shot >= SHOOT_DELAY:
            self.last_shot = now
            self.sound_manager.play("shoot")
            if self.triple_shot:
                b1 = Bullet(self.rect.centerx, self.rect.top, 0)
                b2 = Bullet(self.rect.left + 5, self.rect.top + 10, -2)
                b3 = Bullet(self.rect.right - 5, self.rect.top + 10, 2)
                for b in [b1, b2, b3]:
                    self.bullet_group.add(b)
                    self.all_sprites_group.add(b)
            else:
                bullet = Bullet(self.rect.centerx, self.rect.top, 0)
                self.bullet_group.add(bullet)
                self.all_sprites_group.add(bullet)

    def draw_shield(self, screen):
        """Desenha escudo visual.

        Args:
            screen: Superfície de desenho.
        """
        if self.shield:
            pulse = int(3 * math.sin(pygame.time.get_ticks() / 150))
            radius = max(PLAYER_WIDTH // 2, PLAYER_HEIGHT // 2) + 8 + pulse
            pygame.draw.circle(screen, LIGHT_BLUE, self.rect.center, radius, 2)

    def _clamp_to_screen(self):
        """Limita nave à tela."""
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Bullet(pygame.sprite.Sprite):
    """Projétil do jogador."""

    def __init__(self, x, y, speed_x=0):
        """Inicializa tiro.

        Args:
            x: Posição X.
            y: Posição Y.
            speed_x: Velocidade horizontal.
        """
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.image, BULLET_COLOR, (0, 0, BULLET_WIDTH, BULLET_HEIGHT))
        pygame.draw.rect(self.image, WHITE, (1, 1, BULLET_WIDTH - 2, BULLET_HEIGHT - 2))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = BULLET_SPEED
        self.speed_x = speed_x

    def update(self):
        """Move e remove se fora da tela."""
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    """Nave inimiga."""

    COLORS = [RED, ORANGE, MAGENTA, GREEN]

    def __init__(self, min_speed, max_speed, wave_manager):
        """Inicializa inimigo.

        Args:
            min_speed: Velocidade mínima.
            max_speed: Velocidade máxima.
            wave_manager: WaveManager.
        """
        super().__init__()
        self.color = random.choice(self.COLORS)
        self.image = self._create_enemy_image()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
        self.rect.y = random.randint(-80, -ENEMY_HEIGHT)
        self.speed = random.uniform(min_speed, max_speed)
        self.wave_manager = wave_manager

    def _create_enemy_image(self):
        """Cria sprite do inimigo.

        Returns:
            pygame.Surface: Superfície do inimigo.
        """
        surface = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)
        body_points = [
            (ENEMY_WIDTH // 2, 0), (ENEMY_WIDTH, ENEMY_HEIGHT // 2),
            (ENEMY_WIDTH // 2, ENEMY_HEIGHT), (0, ENEMY_HEIGHT // 2),
        ]
        pygame.draw.polygon(surface, self.color, body_points)
        inner_points = [
            (ENEMY_WIDTH // 2, 6), (ENEMY_WIDTH - 6, ENEMY_HEIGHT // 2),
            (ENEMY_WIDTH // 2, ENEMY_HEIGHT - 6), (6, ENEMY_HEIGHT // 2),
        ]
        pygame.draw.polygon(surface, DARK_GRAY, inner_points)
        pygame.draw.circle(surface, WHITE, (ENEMY_WIDTH // 2, ENEMY_HEIGHT // 2), 4)
        pygame.draw.circle(surface, RED, (ENEMY_WIDTH // 2, ENEMY_HEIGHT // 2), 2)
        return surface

    def update(self):
        """Move e remove se fora da tela."""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.wave_manager.enemy_escaped()
            self.kill()


class Boss(pygame.sprite.Sprite):
    """Chefe a cada 5 waves."""

    def __init__(self, level, boss_bullets, all_sprites_group):
        """Inicializa boss.

        Args:
            level: Nível.
            boss_bullets: Grupo de tiros.
            all_sprites_group: Grupo geral.
        """
        super().__init__()
        self.level = level
        self.max_hp = BOSS_BASE_HP + (level * BOSS_HP_PER_LEVEL)
        self.hp = self.max_hp
        self.speed = BOSS_SPEED + (level * 0.3)
        self.direction = 1
        self.last_shot = 0
        self.shoot_delay = max(400, BOSS_SHOOT_DELAY - (level * 50))
        self.boss_bullets = boss_bullets
        self.all_sprites_group = all_sprites_group
        self.entering = True
        self.image = self._create_boss_image()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = -10

    def _create_boss_image(self):
        """Cria sprite do boss.

        Returns:
            pygame.Surface: Superfície do boss.
        """
        surface = pygame.Surface((BOSS_WIDTH, BOSS_HEIGHT), pygame.SRCALPHA)
        body_points = [
            (BOSS_WIDTH // 2, 0), (BOSS_WIDTH - 5, 15),
            (BOSS_WIDTH, BOSS_HEIGHT // 2), (BOSS_WIDTH - 5, BOSS_HEIGHT - 10),
            (5, BOSS_HEIGHT - 10), (0, BOSS_HEIGHT // 2), (5, 15),
        ]
        pygame.draw.polygon(surface, PURPLE, body_points)
        inner_points = [
            (BOSS_WIDTH // 2, 8), (BOSS_WIDTH - 15, 18),
            (BOSS_WIDTH - 10, BOSS_HEIGHT // 2), (BOSS_WIDTH - 15, BOSS_HEIGHT - 15),
            (15, BOSS_HEIGHT - 15), (10, BOSS_HEIGHT // 2), (15, 18),
        ]
        pygame.draw.polygon(surface, DARK_GRAY, inner_points)
        eye_y = BOSS_HEIGHT // 2 - 3
        pygame.draw.circle(surface, RED, (BOSS_WIDTH // 2, eye_y), 8)
        pygame.draw.circle(surface, YELLOW, (BOSS_WIDTH // 2, eye_y), 4)
        pygame.draw.circle(surface, WHITE, (BOSS_WIDTH // 2, eye_y), 2)
        pygame.draw.rect(surface, DARK_RED, (5, BOSS_HEIGHT - 20, 8, 15))
        pygame.draw.rect(surface, DARK_RED, (BOSS_WIDTH - 13, BOSS_HEIGHT - 20, 8, 15))
        for i in range(min(self.level, 3)):
            pygame.draw.line(surface, MAGENTA, (15, 12 + i * 5), (BOSS_WIDTH - 15, 12 + i * 5), 1)
        return surface

    def update(self):
        """Atualiza posição e tiros."""
        if self.entering:
            self.rect.y += 1
            if self.rect.top >= 30:
                self.entering = False
            return
        self.rect.x += self.speed * self.direction
        if self.rect.right >= SCREEN_WIDTH - 10:
            self.direction = -1
        elif self.rect.left <= 10:
            self.direction = 1
        self.rect.y = 30 + int(10 * math.sin(pygame.time.get_ticks() / 800))
        self._shoot()

    def _shoot(self):
        """Dispara tiros."""
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            b1 = BossBullet(self.rect.centerx, self.rect.bottom, 0, BOSS_BULLET_SPEED)
            self.boss_bullets.add(b1)
            self.all_sprites_group.add(b1)
            if self.level >= 2:
                b2 = BossBullet(self.rect.left + 12, self.rect.bottom - 5, -1, BOSS_BULLET_SPEED)
                b3 = BossBullet(self.rect.right - 12, self.rect.bottom - 5, 1, BOSS_BULLET_SPEED)
                self.boss_bullets.add(b2, b3)
                self.all_sprites_group.add(b2, b3)
            if self.level >= 3:
                b4 = BossBullet(self.rect.left + 5, self.rect.bottom, -2, BOSS_BULLET_SPEED - 1)
                b5 = BossBullet(self.rect.right - 5, self.rect.bottom, 2, BOSS_BULLET_SPEED - 1)
                self.boss_bullets.add(b4, b5)
                self.all_sprites_group.add(b4, b5)

    def take_damage(self):
        """Reduz HP.

        Returns:
            bool: True se morreu.
        """
        self.hp -= 1
        if self.hp > 0:
            self.image = self._create_boss_image()
            flash = pygame.Surface((BOSS_WIDTH, BOSS_HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 0, 0, 80))
            self.image.blit(flash, (0, 0))
        return self.hp <= 0

    def draw_health_bar(self, screen):
        """Desenha barra de vida.

        Args:
            screen: Superfície.
        """
        if self.entering:
            return
        bar_width = 200
        bar_height = 12
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 15
        pygame.draw.rect(screen, DARK_GRAY, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        hp_ratio = self.hp / self.max_hp
        fill_width = int(bar_width * hp_ratio)
        bar_color = GREEN if hp_ratio > 0.5 else (YELLOW if hp_ratio > 0.25 else RED)
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_width, bar_height))
        boss_font = pygame.font.SysFont("arial", 14)
        boss_text = boss_font.render(f"BOSS Lv.{self.level}", True, WHITE)
        screen.blit(boss_text, (SCREEN_WIDTH // 2 - boss_text.get_width() // 2, bar_y - 15))


class BossBullet(pygame.sprite.Sprite):
    """Projétil do boss."""

    def __init__(self, x, y, speed_x, speed_y):
        """Inicializa tiro do boss."""
        super().__init__()
        self.image = pygame.Surface((6, 10), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, 6, 10))
        pygame.draw.rect(self.image, ORANGE, (1, 1, 4, 8))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        """Move e remove."""
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > SCREEN_HEIGHT or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    """Power-up."""

    TYPES = ["triple", "shield", "bomb"]

    def __init__(self, x, y):
        """Inicializa power-up."""
        super().__init__()
        self.kind = random.choice(self.TYPES)
        self.image = self._create_powerup_image()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = POWERUP_SPEED

    def _create_powerup_image(self):
        """Cria sprite do power-up.

        Returns:
            pygame.Surface: Superfície.
        """
        surface = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE), pygame.SRCALPHA)
        if self.kind == "triple":
            pygame.draw.polygon(surface, YELLOW, [
                (POWERUP_SIZE // 2, 2), (2, POWERUP_SIZE - 2), (POWERUP_SIZE - 2, POWERUP_SIZE - 2),
            ])
            pygame.draw.polygon(surface, ORANGE, [
                (POWERUP_SIZE // 2, 6), (6, POWERUP_SIZE - 4), (POWERUP_SIZE - 6, POWERUP_SIZE - 4),
            ])
        elif self.kind == "shield":
            pygame.draw.circle(surface, LIGHT_BLUE, (POWERUP_SIZE // 2, POWERUP_SIZE // 2), POWERUP_SIZE // 2 - 1)
            pygame.draw.circle(surface, BLUE, (POWERUP_SIZE // 2, POWERUP_SIZE // 2), POWERUP_SIZE // 2 - 4)
            pygame.draw.circle(surface, LIGHT_BLUE, (POWERUP_SIZE // 2, POWERUP_SIZE // 2), 4)
        elif self.kind == "bomb":
            pygame.draw.rect(surface, RED, (2, 2, POWERUP_SIZE - 4, POWERUP_SIZE - 4))
            pygame.draw.rect(surface, ORANGE, (6, 6, POWERUP_SIZE - 12, POWERUP_SIZE - 12))
            pygame.draw.rect(surface, YELLOW, (9, 9, POWERUP_SIZE - 18, POWERUP_SIZE - 18))
        return surface

    def update(self):
        """Move e remove."""
        self.rect.y += self.speed
        self.rect.x += int(math.sin(pygame.time.get_ticks() / 200) * 0.8)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Particle(pygame.sprite.Sprite):
    """Partícula de explosão."""

    def __init__(self, x, y, color):
        """Inicializa partícula."""
        super().__init__()
        self.pos_x = float(x)
        self.pos_y = float(y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(PARTICLE_MIN_SPEED, PARTICLE_MAX_SPEED)
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        self.color = color
        self.initial_radius = random.randint(2, 5)
        self.radius = self.initial_radius
        self.spawn_time = pygame.time.get_ticks()
        self._update_image()

    def _update_image(self):
        """Redesenha partícula."""
        size = max(self.radius * 2, 1)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        if self.radius >= 1:
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(int(self.pos_x), int(self.pos_y)))

    def update(self):
        """Move, encolhe e remove."""
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed >= PARTICLE_LIFETIME:
            self.kill()
            return
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        self.vel_x *= 0.96
        self.vel_y *= 0.96
        life_ratio = 1 - (elapsed / PARTICLE_LIFETIME)
        self.radius = max(int(self.initial_radius * life_ratio), 1)
        self._update_image()


class Explosion:
    """Fábrica de explosões."""

    COLORS = [YELLOW, ORANGE, RED, WHITE]

    @staticmethod
    def create(x, y, all_sprites_group, big=False):
        """Cria explosão."""
        count = EXPLOSION_PARTICLES * 3 if big else EXPLOSION_PARTICLES
        for _ in range(count):
            color = random.choice(Explosion.COLORS)
            particle = Particle(x, y, color)
            if big:
                particle.vel_x *= 2
                particle.vel_y *= 2
                particle.initial_radius = random.randint(3, 7)
            all_sprites_group.add(particle)


# =============================================================================
# CLASSE PRINCIPAL DO JOGO
# =============================================================================

class Game:
    """Classe principal do jogo."""

    def __init__(self):
        """Inicializa o jogo."""
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_MENU
        self.font_small = pygame.font.SysFont("arial", 16)
        self.font = pygame.font.SysFont("arial", 18)
        self.font_medium = pygame.font.SysFont("arial", 28)
        self.font_big = pygame.font.SysFont("arial", 52)
        self.font_title = pygame.font.SysFont("arial", 60, bold=True)
        self.background = Background()
        self.sound_manager = SoundManager()
        self.leaderboard = Leaderboard()
        self.final_score = 0
        self.final_wave = 0
        self.menu_selection = 0
        self.player_name = ""

    def run(self):
        """Loop principal."""
        while self.running:
            self.clock.tick(FPS)
            if self.state == STATE_MENU:
                self._menu_events()
                self.background.update()
                self._draw_menu()
            elif self.state == STATE_INSTRUCTIONS:
                self._instructions_events()
                self.background.update()
                self._draw_instructions()
            elif self.state == STATE_PLAYING:
                self._game_events()
                self._game_update()
                self._game_draw()
            elif self.state == STATE_GAME_OVER:
                self._game_over_events()
                self.background.update()
                self._draw_game_over()
            elif self.state == STATE_INPUT_NAME:
                self._input_name_events()
                self.background.update()
                self._draw_input_name()
            elif self.state == STATE_LEADERBOARD:
                self._leaderboard_events()
                self.background.update()
                self._draw_leaderboard()
        pygame.quit()

    # =========================================================================
    # MENU
    # =========================================================================

    def _menu_events(self):
        """Eventos do menu."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu_selection = (self.menu_selection - 1) % 4
                    self.sound_manager.play("menu_select")
                elif event.key == pygame.K_DOWN:
                    self.menu_selection = (self.menu_selection + 1) % 4
                    self.sound_manager.play("menu_select")
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.sound_manager.play("menu_confirm")
                    if self.menu_selection == 0:
                        self._start_new_game()
                    elif self.menu_selection == 1:
                        self.state = STATE_INSTRUCTIONS
                    elif self.menu_selection == 2:
                        self.state = STATE_LEADERBOARD
                    elif self.menu_selection == 3:
                        self.running = False
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def _draw_menu(self):
        """Desenha menu."""
        self.screen.fill(BLACK)
        self.background.draw(self.screen)
        title_y = 150
        glow = int(30 * math.sin(pygame.time.get_ticks() / 500)) + 225
        title_color = (0, glow, glow)
        title_text = self.font_title.render("SPACE", True, title_color)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, title_y))
        title_text2 = self.font_title.render("SHOOTER", True, title_color)
        self.screen.blit(title_text2, (SCREEN_WIDTH // 2 - title_text2.get_width() // 2, title_y + 65))
        nave_y = title_y + 155
        nave_points = [
            (SCREEN_WIDTH // 2, nave_y),
            (SCREEN_WIDTH // 2 - 20, nave_y + 35),
            (SCREEN_WIDTH // 2 + 20, nave_y + 35),
        ]
        pygame.draw.polygon(self.screen, CYAN, nave_points)
        pygame.draw.circle(self.screen, WHITE, (SCREEN_WIDTH // 2, nave_y + 14), 4)
        options = ["JOGAR", "INSTRUÇÕES", "RANKING", "SAIR"]
        menu_y = 410
        for i, option in enumerate(options):
            if i == self.menu_selection:
                color = CYAN
                prefix = "> "
                suffix = " <"
            else:
                color = GRAY
                prefix = "  "
                suffix = "  "
            text = self.font_medium.render(f"{prefix}{option}{suffix}", True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, menu_y + i * 45))
        hint = self.font_small.render("Use SETAS para navegar e ENTER para selecionar", True, GRAY)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))
        pygame.display.flip()

    # =========================================================================
    # INSTRUÇÕES
    # =========================================================================

    def _instructions_events(self):
        """Eventos das instruções."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    self.sound_manager.play("menu_confirm")
                    self.state = STATE_MENU

    def _draw_instructions(self):
        """Desenha instruções."""
        self.screen.fill(BLACK)
        self.background.draw(self.screen)
        title = self.font_big.render("INSTRUÇÕES", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
        y = 130
        sections = [
            ("CONTROLES", CYAN, [
                ("Setas / WASD", "Movimentar a nave"),
                ("Espaço", "Atirar"), ("ESC", "Voltar ao menu"),
            ]),
            ("POWER-UPS", YELLOW, [
                ("Triângulo Amarelo", "Tiro triplo (5s)"),
                ("Círculo Azul", "Escudo protetor (6s)"),
                ("Quadrado Vermelho", "Bomba (destrói todos)"),
            ]),
            ("BOSS", PURPLE, [
                ("", "A cada 5 waves aparece um BOSS!"),
                ("", "Ele atira de volta e fica mais"),
                ("", "forte a cada aparição."),
            ]),
            ("OBJETIVO", GREEN, [
                ("", "Destrua inimigos e sobreviva!"),
                ("", "+100 pontos por inimigo"),
                ("", "+500 pontos por boss derrotado"),
            ]),
        ]
        for section_title, section_color, items in sections:
            section_text = self.font_medium.render(section_title, True, section_color)
            self.screen.blit(section_text, (SCREEN_WIDTH // 2 - section_text.get_width() // 2, y))
            y += 35
            for key, description in items:
                if key:
                    key_text = self.font_small.render(f"{key}: ", True, WHITE)
                    desc_text = self.font_small.render(description, True, GRAY)
                    total_width = key_text.get_width() + desc_text.get_width()
                    start_x = SCREEN_WIDTH // 2 - total_width // 2
                    self.screen.blit(key_text, (start_x, y))
                    self.screen.blit(desc_text, (start_x + key_text.get_width(), y))
                else:
                    desc_text = self.font_small.render(description, True, GRAY)
                    self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, y))
                y += 22
            y += 10
        back_text = self.font.render("Pressione ENTER ou ESC para voltar", True, GRAY)
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 50))
        pygame.display.flip()

    # =========================================================================
    # GAMEPLAY
    # =========================================================================

    def _start_new_game(self):
        """Inicia nova partida."""
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()
        self.player = Player(self.bullets, self.all_sprites, self.sound_manager)
        self.all_sprites.add(self.player)
        self.wave_manager = WaveManager()
        self.wave_manager.start_next_wave()
        self.boss = None
        self.score = 0
        self.bomb_flash = 0
        self.state = STATE_PLAYING
        self.sound_manager.play_music()
        self.sound_manager.play("wave_start")

    def _game_events(self):
        """Eventos do jogo."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.sound_manager.stop_music()
                    self.state = STATE_MENU
                elif event.key == pygame.K_SPACE:
                    self.player.shoot()

    def _game_update(self):
        """Atualiza jogo."""
        self.all_sprites.update()
        self.background.update()
        if self.wave_manager.is_wave_complete():
            self.boss = None
            self.wave_manager.start_next_wave()
            self.sound_manager.play("wave_start")
        if not self.wave_manager.is_transitioning():
            if self.wave_manager.is_boss_wave:
                if self.wave_manager.should_spawn_boss():
                    self._spawn_boss()
            else:
                self._spawn_enemies()
        self._check_collisions()
        self._check_powerup_collisions()
        self._check_boss_collisions()

    def _spawn_enemies(self):
        """Spawna inimigos."""
        if self.wave_manager.should_spawn(len(self.enemies)):
            enemy = Enemy(
                self.wave_manager.enemy_min_speed,
                self.wave_manager.enemy_max_speed,
                self.wave_manager,
            )
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def _spawn_boss(self):
        """Spawna boss."""
        level = self.wave_manager.get_boss_level()
        self.boss = Boss(level, self.boss_bullets, self.all_sprites)
        self.all_sprites.add(self.boss)

    def _check_collisions(self):
        """Colisões: tiro x inimigo, inimigo x jogador."""
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
        for bullet, enemies_hit in hits.items():
            for enemy in enemies_hit:
                self.score += 100
                self.wave_manager.enemy_killed()
                self.sound_manager.play("explosion")
                Explosion.create(enemy.rect.centerx, enemy.rect.centery, self.all_sprites)
                if random.randint(1, 100) <= POWERUP_SPAWN_CHANCE:
                    powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery)
                    self.powerups.add(powerup)
                    self.all_sprites.add(powerup)
        if not self.player.invincible:
            enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
            if enemy_hits:
                for enemy in enemy_hits:
                    self.wave_manager.enemy_killed()
                    self.sound_manager.play("explosion")
                    Explosion.create(enemy.rect.centerx, enemy.rect.centery, self.all_sprites)
                alive = self.player.hit()
                if not alive:
                    Explosion.create(self.player.rect.centerx, self.player.rect.centery, self.all_sprites)
                    self.final_score = self.score
                    self.final_wave = self.wave_manager.wave_number
                    self.sound_manager.play("game_over")
                    self.sound_manager.stop_music()
                    self.state = STATE_GAME_OVER

    def _check_boss_collisions(self):
        """Colisões com boss."""
        if self.boss is None or not self.boss.alive():
            return
        boss_hits = pygame.sprite.spritecollide(self.boss, self.bullets, True)
        for bullet in boss_hits:
            self.sound_manager.play("boss_hit")
            dead = self.boss.take_damage()
            if dead:
                self.score += 500
                self.wave_manager.boss_defeated = True
                self.sound_manager.play("boss_death")
                Explosion.create(self.boss.rect.centerx, self.boss.rect.centery, self.all_sprites, big=True)
                Explosion.create(self.boss.rect.left + 10, self.boss.rect.top + 10, self.all_sprites, big=True)
                Explosion.create(self.boss.rect.right - 10, self.boss.rect.bottom - 10, self.all_sprites, big=True)
                powerup = PowerUp(self.boss.rect.centerx, self.boss.rect.centery)
                self.powerups.add(powerup)
                self.all_sprites.add(powerup)
                self.boss.kill()
                self.boss = None
                for b in self.boss_bullets:
                    b.kill()
                return
        if not self.player.invincible:
            boss_bullet_hits = pygame.sprite.spritecollide(self.player, self.boss_bullets, True)
            if boss_bullet_hits:
                alive = self.player.hit()
                if not alive:
                    Explosion.create(self.player.rect.centerx, self.player.rect.centery, self.all_sprites)
                    self.final_score = self.score
                    self.final_wave = self.wave_manager.wave_number
                    self.sound_manager.play("game_over")
                    self.sound_manager.stop_music()
                    self.state = STATE_GAME_OVER
        if not self.player.invincible and self.boss and pygame.sprite.collide_rect(self.player, self.boss):
            alive = self.player.hit()
            if not alive:
                Explosion.create(self.player.rect.centerx, self.player.rect.centery, self.all_sprites)
                self.final_score = self.score
                self.final_wave = self.wave_manager.wave_number
                self.sound_manager.play("game_over")
                self.sound_manager.stop_music()
                self.state = STATE_GAME_OVER

    def _check_powerup_collisions(self):
        """Coleta de power-ups."""
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            self.sound_manager.play("powerup")
            if powerup.kind == "triple":
                self.player.activate_triple_shot()
            elif powerup.kind == "shield":
                self.player.activate_shield()
            elif powerup.kind == "bomb":
                self._activate_bomb()

    def _activate_bomb(self):
        """Ativa bomba."""
        self.bomb_flash = pygame.time.get_ticks()
        self.sound_manager.play("bomb")
        for enemy in list(self.enemies):
            self.score += 100
            self.wave_manager.enemy_killed()
            Explosion.create(enemy.rect.centerx, enemy.rect.centery, self.all_sprites, big=True)
            enemy.kill()
        if self.boss and self.boss.alive():
            for _ in range(5):
                dead = self.boss.take_damage()
                if dead:
                    self.score += 500
                    self.wave_manager.boss_defeated = True
                    self.sound_manager.play("boss_death")
                    Explosion.create(self.boss.rect.centerx, self.boss.rect.centery, self.all_sprites, big=True)
                    self.boss.kill()
                    self.boss = None
                    for b in self.boss_bullets:
                        b.kill()
                    break

    def _game_draw(self):
        """Desenha o jogo."""
        self.screen.fill(BLACK)
        self.background.draw(self.screen)
        if pygame.time.get_ticks() - self.bomb_flash < BOMB_FLASH_DURATION:
            alpha = 255 * (1 - (pygame.time.get_ticks() - self.bomb_flash) / BOMB_FLASH_DURATION)
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.fill(WHITE)
            flash_surface.set_alpha(int(alpha))
            self.screen.blit(flash_surface, (0, 0))
        self.all_sprites.draw(self.screen)
        self.player.draw_shield(self.screen)
        if self.boss and self.boss.alive():
            self.boss.draw_health_bar(self.screen)
        self._draw_hud()
        if self.wave_manager.is_transitioning():
            self._draw_wave_transition()
        pygame.display.flip()

    def _draw_wave_transition(self):
        """Texto de transição."""
        elapsed = pygame.time.get_ticks() - self.wave_manager.transition_start
        if elapsed < 500:
            alpha = int(255 * (elapsed / 500))
        elif elapsed > WAVE_TRANSITION_DURATION - 500:
            alpha = int(255 * ((WAVE_TRANSITION_DURATION - elapsed) / 500))
        else:
            alpha = 255
        if self.wave_manager.is_boss_wave:
            wave_text = self.font_big.render(f"WAVE {self.wave_manager.wave_number}", True, RED)
            subtitle = self.font_medium.render("BOSS INCOMING!", True, YELLOW)
        else:
            wave_text = self.font_big.render(f"WAVE {self.wave_manager.wave_number}", True, CYAN)
            subtitle = self.font_medium.render("Prepare-se!", True, WHITE)
        wave_text.set_alpha(alpha)
        subtitle.set_alpha(alpha)
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 3 + 55))

    def _draw_hud(self):
        """Desenha HUD."""
        fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        self.screen.blit(fps_text, (5, 5))
        score_text = self.font.render(f"Pontuação: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 5))
        lives_text = self.font.render(f"Vidas: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 5))
        wave_text = self.font.render(f"Wave: {self.wave_manager.wave_number}", True, CYAN)
        self.screen.blit(wave_text, (SCREEN_WIDTH - wave_text.get_width() - 10, 28))
        y_indicator = 30
        if self.player.triple_shot:
            remaining = max(0, TRIPLE_SHOT_DURATION - (pygame.time.get_ticks() - self.player.triple_shot_timer))
            text = self.font.render(f"Tiro Triplo: {remaining // 1000 + 1}s", True, YELLOW)
            self.screen.blit(text, (5, y_indicator))
            y_indicator += 20
        if self.player.shield:
            remaining = max(0, SHIELD_DURATION - (pygame.time.get_ticks() - self.player.shield_timer))
            text = self.font.render(f"Escudo: {remaining // 1000 + 1}s", True, LIGHT_BLUE)
            self.screen.blit(text, (5, y_indicator))

    # =========================================================================
    # GAME OVER
    # =========================================================================

    def _game_over_events(self):
        """Eventos do game over."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.sound_manager.play("menu_confirm")
                    if self.leaderboard.is_high_score(self.final_score):
                        self.player_name = ""
                        self.state = STATE_INPUT_NAME
                    else:
                        self._start_new_game()
                elif event.key == pygame.K_ESCAPE:
                    if self.leaderboard.is_high_score(self.final_score):
                        self.player_name = ""
                        self.state = STATE_INPUT_NAME
                    else:
                        self.state = STATE_MENU

    def _draw_game_over(self):
        """Desenha game over."""
        self.screen.fill(BLACK)
        self.background.draw(self.screen)
        pulse = int(30 * math.sin(pygame.time.get_ticks() / 400)) + 225
        go_color = (pulse, 0, 0)
        go_text = self.font_title.render("GAME OVER", True, go_color)
        self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 150))
        stats_y = 300
        score_label = self.font.render("PONTUAÇÃO", True, GRAY)
        self.screen.blit(score_label, (SCREEN_WIDTH // 2 - score_label.get_width() // 2, stats_y))
        score_value = self.font_big.render(f"{self.final_score}", True, YELLOW)
        self.screen.blit(score_value, (SCREEN_WIDTH // 2 - score_value.get_width() // 2, stats_y + 25))
        wave_label = self.font.render("WAVE ALCANÇADA", True, GRAY)
        self.screen.blit(wave_label, (SCREEN_WIDTH // 2 - wave_label.get_width() // 2, stats_y + 100))
        wave_value = self.font_big.render(f"{self.final_wave}", True, CYAN)
        self.screen.blit(wave_value, (SCREEN_WIDTH // 2 - wave_value.get_width() // 2, stats_y + 125))

        # Indica se é high score
        if self.leaderboard.is_high_score(self.final_score):
            hs_text = self.font_medium.render("NOVO RECORDE!", True, YELLOW)
            self.screen.blit(hs_text, (SCREEN_WIDTH // 2 - hs_text.get_width() // 2, 250))

        options_y = 550
        play_text = self.font_medium.render("ENTER - Continuar", True, GREEN)
        self.screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, options_y))
        menu_text = self.font_medium.render("ESC - Menu principal", True, GRAY)
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, options_y + 40))
        pygame.display.flip()

    # =========================================================================
    # INPUT DE NOME
    # =========================================================================

    def _input_name_events(self):
        """Eventos da tela de input de nome."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(self.player_name) > 0:
                        self.sound_manager.play("menu_confirm")
                        self.leaderboard.add_entry(self.player_name, self.final_score, self.final_wave)
                        self.state = STATE_LEADERBOARD
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.leaderboard.add_entry("???", self.final_score, self.final_wave)
                    self.state = STATE_MENU
                else:
                    if len(self.player_name) < 10 and event.unicode.isprintable() and event.unicode != "":
                        self.player_name += event.unicode

    def _draw_input_name(self):
        """Desenha tela de input de nome."""
        self.screen.fill(BLACK)
        self.background.draw(self.screen)

        title = self.font_big.render("NOVO RECORDE!", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))

        score_text = self.font_medium.render(f"Pontuação: {self.final_score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 200))

        prompt = self.font_medium.render("Digite seu nome:", True, CYAN)
        self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 300))

        # Campo de texto com cursor piscante
        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        name_display = self.player_name + cursor
        name_text = self.font_big.render(name_display, True, WHITE)
        self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 360))

        # Caixa ao redor do nome
        box_width = 300
        box_height = 60
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = 355
        pygame.draw.rect(self.screen, CYAN, (box_x, box_y, box_width, box_height), 2)

        hint = self.font.render("ENTER para confirmar (máx. 10 caracteres)", True, GRAY)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 450))

        pygame.display.flip()

    # =========================================================================
    # LEADERBOARD
    # =========================================================================

    def _leaderboard_events(self):
        """Eventos da tela de leaderboard."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    self.sound_manager.play("menu_confirm")
                    self.state = STATE_MENU

    def _draw_leaderboard(self):
        """Desenha tela de leaderboard com o ranking."""
        self.screen.fill(BLACK)
        self.background.draw(self.screen)

        title = self.font_big.render("RANKING", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        entries = self.leaderboard.get_entries()

        if not entries:
            empty_text = self.font_medium.render("Nenhum recorde ainda!", True, GRAY)
            self.screen.blit(empty_text, (SCREEN_WIDTH // 2 - empty_text.get_width() // 2, 300))
        else:
            # Cabeçalho
            header_y = 110
            pos_header = self.font.render("#", True, CYAN)
            name_header = self.font.render("NOME", True, CYAN)
            score_header = self.font.render("PONTOS", True, CYAN)
            wave_header = self.font.render("WAVE", True, CYAN)
            self.screen.blit(pos_header, (40, header_y))
            self.screen.blit(name_header, (80, header_y))
            self.screen.blit(score_header, (280, header_y))
            self.screen.blit(wave_header, (400, header_y))

            # Linha separadora
            pygame.draw.line(self.screen, GRAY, (30, header_y + 25), (SCREEN_WIDTH - 30, header_y + 25), 1)

            # Entradas
            for i, entry in enumerate(entries):
                y = header_y + 35 + i * 40

                # Destaque para top 3
                if i == 0:
                    color = YELLOW
                elif i == 1:
                    color = LIGHT_BLUE
                elif i == 2:
                    color = ORANGE
                else:
                    color = WHITE

                pos_text = self.font.render(f"{i + 1}.", True, color)
                name_text = self.font.render(entry["name"][:10], True, color)
                score_text = self.font.render(f"{entry['score']}", True, color)
                wave_text = self.font.render(f"{entry['wave']}", True, color)

                self.screen.blit(pos_text, (40, y))
                self.screen.blit(name_text, (80, y))
                self.screen.blit(score_text, (280, y))
                self.screen.blit(wave_text, (410, y))

        back_text = self.font.render("Pressione ENTER ou ESC para voltar", True, GRAY)
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 50))
        pygame.display.flip()


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    game = Game()
    game.run()
