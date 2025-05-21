import pygame
import random
import sys
import math


pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coin Collector")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

#Sound Settings
sound_enabled = True
sound_volume = 1.0

#Load Sounds
coin_sound = pygame.mixer.Sound("coin.mp3")
hit_sound = pygame.mixer.Sound("hit.mp3")
shoot_sound = pygame.mixer.Sound("shoot.mp3")
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)
coin_sound.set_volume(sound_volume)
hit_sound.set_volume(sound_volume)
shoot_sound.set_volume(sound_volume)
pygame.mixer.music.set_volume(sound_volume)

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

#Constants
PLAYER_SPEED = 5
ENEMY_SPEED = 2
NUM_COINS = 10
TIME_LIMIT = 30  # s
INVULNERABILITY_DURATION = 2000  # ms
BULLET_SPEED = 7

#Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.lives = 3
        self.speed = PLAYER_SPEED
        self.invulnerable = False
        self.invulnerable_start = 0
        self.direction = (0, -1)
        self.spread_level = 0

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.direction = (-1, 0)
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.direction = (1, 0)
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
            self.direction = (0, -1)
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            self.direction = (0, 1)
        self.rect.clamp_ip(screen.get_rect())

    def set_invulnerable(self):
        self.invulnerable = True
        self.invulnerable_start = pygame.time.get_ticks()

    def check_invulnerability(self):
        if self.invulnerable and pygame.time.get_ticks() - self.invulnerable_start > INVULNERABILITY_DURATION:
            self.invulnerable = False

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    def update(self):
        self.rect.x += self.direction[0] * ENEMY_SPEED
        self.rect.y += self.direction[1] * ENEMY_SPEED
        if not screen.get_rect().contains(self.rect):
            self.direction = (-self.direction[0], -self.direction[1])
            self.rect.clamp_ip(screen.get_rect())

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, color=BLUE, enemy_bullet=False):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.enemy_bullet = enemy_bullet

    def update(self):
        self.rect.x += self.dx * BULLET_SPEED
        self.rect.y += self.dy * BULLET_SPEED
        if (self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

class ShooterEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.image.fill((255, 100, 100))
        self.last_shot_time = pygame.time.get_ticks()

    def update(self):
        super().update()
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > 2000:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
            dx /= dist
            dy /= dist
            bullet = Bullet(self.rect.centerx, self.rect.centery, dx, dy, color=WHITE, enemy_bullet=True)
            bullets.add(bullet)
            all_sprites.add(bullet)
            self.last_shot_time = now

#Functions
def draw_text(text, x, y, color=WHITE):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def reset_level():
    all_sprites.empty()
    all_sprites.add(player)
    player.rect.center = (WIDTH // 2, HEIGHT // 2)
    player.set_invulnerable()
    coins.empty()
    enemies.empty()
    bullets.empty()
    for _ in range(NUM_COINS):
        coin = Coin(random.randint(20, WIDTH-20), random.randint(20, HEIGHT-20))
        coins.add(coin)
    for i in range(current_level):
        if i % 3 == 2:
            e = ShooterEnemy()
        else:
            e = Enemy()
        enemies.add(e)
        all_sprites.add(e)
    return 0, pygame.time.get_ticks()

#Groups
player = Player()
coins = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
all_sprites = pygame.sprite.Group(player)

current_level = 1
level_score, start_time = 0, 0
total_score = 0
coins_collected = 0
upgrade_menu = False
upgrade_selected = False
show_menu = True
show_options = False

# --- UI Drawing Functions ---
def draw_main_menu():
    screen.fill(BLACK)
    draw_text("COIN COLLECTOR", WIDTH // 2 - 130, HEIGHT // 2 - 120)
    draw_text("1. Start Game", WIDTH // 2 - 100, HEIGHT // 2 - 60)
    draw_text("2. Options", WIDTH // 2 - 100, HEIGHT // 2 - 20)
    draw_text("3. Quit", WIDTH // 2 - 100, HEIGHT // 2 + 20)
    pygame.display.flip()

def draw_options_menu():
    screen.fill(BLACK)
    draw_text("OPTIONS", WIDTH // 2 - 60, HEIGHT // 2 - 100)
    draw_text(f"1. Toggle Sound (Currently: {'ON' if sound_enabled else 'OFF'})", WIDTH // 2 - 200, HEIGHT // 2 - 40)
    draw_text("2. Increase Volume", WIDTH // 2 - 200, HEIGHT // 2)
    draw_text("3. Decrease Volume", WIDTH // 2 - 200, HEIGHT // 2 + 40)
    draw_text("4. Back to Main Menu", WIDTH // 2 - 200, HEIGHT // 2 + 80)
    pygame.display.flip()

# --- Game Loop ---
running = True
game_over = False
win = False
while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if show_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    show_menu = False
                    level_score, start_time = reset_level()
                elif event.key == pygame.K_2:
                    show_menu = False
                    show_options = True
                elif event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()

        elif show_options:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    sound_enabled = not sound_enabled
                    for s in [coin_sound, hit_sound, shoot_sound, pygame.mixer.music]:
                        s.set_volume(sound_volume if sound_enabled else 0)
                elif event.key == pygame.K_2:
                    sound_volume = min(1.0, sound_volume + 0.1)
                    if sound_enabled:
                        for s in [coin_sound, hit_sound, shoot_sound, pygame.mixer.music]:
                            s.set_volume(sound_volume)
                elif event.key == pygame.K_3:
                    sound_volume = max(0.0, sound_volume - 0.1)
                    if sound_enabled:
                        for s in [coin_sound, hit_sound, shoot_sound, pygame.mixer.music]:
                            s.set_volume(sound_volume)
                elif event.key == pygame.K_4:
                    show_menu = True
                    show_options = False

        if event.type == pygame.KEYDOWN and not game_over and not upgrade_menu:
            if event.key == pygame.K_SPACE:
                directions = [player.direction]
                if player.spread_level > 0:
                    angle = 30
                    for i in range(1, player.spread_level + 1):
                        offset = math.radians(angle * i)
                        for sign in [-1, 1]:
                            cos_off = math.cos(sign * offset)
                            sin_off = math.sin(sign * offset)
                            dx = player.direction[0] * cos_off - player.direction[1] * sin_off
                            dy = player.direction[0] * sin_off + player.direction[1] * cos_off
                            directions.append((dx, dy))
                for dx, dy in directions:
                    b = Bullet(player.rect.centerx, player.rect.centery, dx, dy)
                    bullets.add(b)
                    all_sprites.add(b)
                if sound_enabled:
                    shoot_sound.play()

        if event.type == pygame.KEYDOWN and game_over:
            current_level = 1
            total_score = 0
            coins_collected = 0
            player.lives = 2
            player.speed = PLAYER_SPEED
            level_score, start_time = reset_level()
            game_over = False

        if event.type == pygame.KEYDOWN and upgrade_menu:
            if event.key == pygame.K_1 and coins_collected >= 10:
                player.lives += 1
                coins_collected -= 10
                upgrade_selected = True
            if event.key == pygame.K_2 and coins_collected >= 5:
                player.speed += 1
                coins_collected -= 5
                upgrade_selected = True
            if event.key == pygame.K_3 and coins_collected >= 10:
                TIME_LIMIT += 10
                coins_collected -= 10
                upgrade_selected = True
            if event.key == pygame.K_4 and coins_collected >= 50:
                player.spread_level += 1
                coins_collected -= 50
                upgrade_selected = True
            if event.key == pygame.K_RETURN or upgrade_selected:
                level_score, start_time = reset_level()
                upgrade_menu = False
                upgrade_selected = False

    if show_menu:
        draw_main_menu()
        continue

    if show_options:
        draw_options_menu()
        continue

    screen.fill(BLACK)

    if not game_over and not upgrade_menu:
        player.update(keys)
        player.check_invulnerability()
        enemies.update()
        bullets.update()

        for bullet in bullets:
            if bullet.enemy_bullet:
                if not player.invulnerable and bullet.rect.colliderect(player.rect):
                    player.lives -= 1
                    bullet.kill()
                    if sound_enabled:
                        hit_sound.play()
                    if player.lives <= 0:
                        game_over = True
                        win = False
                    else:
                        player.set_invulnerable()
            else:
                hit = pygame.sprite.spritecollideany(bullet, enemies)
                if hit:
                    hit.kill()
                    bullet.kill()

        collected = pygame.sprite.spritecollide(player, coins, dokill=True)
        if collected and sound_enabled:
            coin_sound.play()
        level_score += len(collected)
        coins_collected += len(collected)

        if not player.invulnerable and pygame.sprite.spritecollideany(player, enemies):
            player.lives -= 1
            if sound_enabled:
                hit_sound.play()
            if player.lives <= 0:
                game_over = True
                win = False
            else:
                player.set_invulnerable()

        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        if elapsed_time >= TIME_LIMIT:
            game_over = True
            win = False

        if level_score >= NUM_COINS:
            total_score += level_score
            current_level += 1
            upgrade_menu = True

        all_sprites.draw(screen)
        coins.draw(screen)
        enemies.draw(screen)
        bullets.draw(screen)

        draw_text(f"Level: {current_level}", 10, 10)
        draw_text(f"Total Score: {total_score + level_score}", 10, 40)
        draw_text(f"Lives: {player.lives}", 10, 70)
        draw_text(f"Time: {TIME_LIMIT - elapsed_time}", 10, 100)
        draw_text(f"Coins: {coins_collected}", 10, 130)

    elif upgrade_menu:
        draw_text("Coins"+ str(coins_collected), WIDTH // 2 - 100, HEIGHT // 2 - 150)
        draw_text("Upgrade Menu", WIDTH//2 - 100, HEIGHT//2 - 100)
        draw_text("1. +1 Life (10 coins)", WIDTH//2 - 100, HEIGHT//2 - 50)
        draw_text("2. +1 Speed (5 coins)", WIDTH//2 - 100, HEIGHT//2)
        draw_text("3. +10s Time Limit (10 coins)", WIDTH//2 - 100, HEIGHT//2 + 50)
        draw_text("4. Spread Shot Level +1 (50 coins)", WIDTH//2 - 100, HEIGHT//2 + 100)
        draw_text("Press 1–4 to buy, Enter to skip", WIDTH//2 - 150, HEIGHT//2 + 150)

    else:
        if win:
            draw_text("You Win! Press any key to restart", WIDTH//2 - 200, HEIGHT//2)
        else:
            draw_text("Game Over! Press any key to restart", WIDTH//2 - 220, HEIGHT//2)

    pygame.display.flip()

pygame.quit()
sys.exit()
