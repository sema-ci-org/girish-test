import pygame
import random
import time
import os

# Initialize pygame
pygame.init()

# Game window dimensions
WIDTH = 400
HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)

# Game settings
FPS = 60
PLAYER_SPEED = 5
ENEMY_SPEED = 5
SCORE = 0
HIGH_SCORE = 0

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Race Game")
clock = pygame.time.Clock()

# Load images
car_img = pygame.Surface((50, 80))
car_img.fill(GREEN)

enemy_img = pygame.Surface((50, 80))
enemy_img.fill(RED)

# Road
road = pygame.Surface((WIDTH - 100, HEIGHT))
road.fill(GRAY)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = car_img
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 100)
    
    def update(self):
        # Move the player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 50:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH - 50:
            self.rect.x += 5
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= 5
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += 5

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, WIDTH - 100)
        self.rect.y = -100
        self.speed = random.randint(3, 7)
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(50, WIDTH - 100)
            self.rect.y = -100
            self.speed = random.randint(3, 7)
            return True
        return False

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# Create enemies
for i in range(5):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

def draw_text(surface, text, size, x, y):
    font = pygame.font.SysFont('Arial', size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def show_game_over_screen():
    screen.fill(BLACK)
    draw_text(screen, "CAR RACE GAME", 64, WIDTH // 2, HEIGHT // 4)
    draw_text(screen, f"Score: {SCORE}", 36, WIDTH // 2, HEIGHT // 2)
    draw_text(screen, "Press any key to play again", 22, WIDTH // 2, HEIGHT * 3/4)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYUP:
                waiting = False
    return True

# Game loop
running = True
game_over = False

while running:
    # Keep loop running at the right speed
    clock.tick(FPS)
    
    # Process input (events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    if game_over:
        if show_game_over_screen():
            # Reset game
            SCORE = 0
            game_over = False
            all_sprites = pygame.sprite.Group()
            enemies = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)
            for i in range(5):
                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)
        else:
            break
    
    # Update
    all_sprites.update()
    
    # Check if enemy is off screen
    for enemy in enemies:
        if enemy.update():  # If enemy went off screen
            SCORE += 1
    
    # Check for collisions
    if pygame.sprite.spritecollide(player, enemies, False):
        game_over = True
    
    # Draw / render
    screen.fill(BLACK)
    # Draw road
    screen.blit(road, (50, 0))
    # Draw road markings
    for i in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 5, i, 10, 20))
    
    all_sprites.draw(screen)
    
    # Draw score
    draw_text(screen, f"Score: {SCORE}", 18, WIDTH // 2, 10)
    
    # Flip the display
    pygame.display.flip()

pygame.quit()
