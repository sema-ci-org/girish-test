import pygame
import random
import math
import time
from enum import Enum
from typing import List, Tuple, Dict, Optional

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 100) // GRID_SIZE  # Leave space for HUD
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
GREEN = (0, 255, 0)
GRAY = (40, 40, 40)

# Game states
class GameState(Enum):    
    MENU = 0
    PLAYING = 1
    LEVEL_COMPLETE = 2
    GAME_OVER = 3
    PAUSED = 4

# Direction enum
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)

# Ghost behavior states
class GhostState(Enum):
    CHASE = 0
    SCATTER = 1
    FRIGHTENED = 2
    EATEN = 3

class GameObject:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        
    def update_rect(self):
        self.rect.x = self.x * GRID_SIZE
        self.rect.y = self.y * GRID_SIZE + 50  # Offset for HUD
        
    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, self.rect)

class Wall(GameObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, BLUE)
        self.is_gate = False
        
    def draw(self, screen: pygame.Surface):
        if not self.is_gate:
            pygame.draw.rect(screen, self.color, self.rect, 1)
            inner_rect = self.rect.inflate(-6, -6)
            pygame.draw.rect(screen, self.color, inner_rect)

class Pellet(GameObject):
    def __init__(self, x: int, y: int, is_power_pellet: bool = False):
        super().__init__(x, y, WHITE)
        self.is_power_pellet = is_power_pellet
        self.radius = 4 if not is_power_pellet else 8
        self.eaten = False
        
    def draw(self, screen: pygame.Surface):
        if not self.eaten:
            center = (self.rect.centerx, self.rect.centery + 50)  # Offset for HUD
            pygame.draw.circle(screen, self.color, center, self.radius)

class Ghost(GameObject):
    def __init__(self, x: int, y: int, color: Tuple[int, int, int], name: str):
        super().__init__(x, y, color)
        self.name = name
        self.start_x = x
        self.start_y = y
        self.direction = Direction.LEFT
        self.next_direction = Direction.LEFT
        self.speed = 1.0
        self.state = GhostState.SCATTER
        self.frightened_timer = 0
        self.scatter_timer = 7 * FPS  # 7 seconds
        self.chase_timer = 20 * FPS   # 20 seconds
        self.target = (0, 0)
        self.in_house = True
        self.eye_direction = Direction.LEFT
        
    def update(self, level: 'Level', pacman: 'Pacman'):
        if self.state == GhostState.FRIGHTENED:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.state = GhostState.CHASE
                
        if self.state == GhostState.SCATTER:
            self.scatter_timer -= 1
            if self.scatter_timer <= 0:
                self.state = GhostState.CHASE
                self.chase_timer = 20 * FPS
        elif self.state == GhostState.CHASE:
            self.chase_timer -= 1
            if self.chase_timer <= 0:
                self.state = GhostState.SCATTER
                self.scatter_timer = 7 * FPS
                
        self.move(level, pacman)
        self.update_rect()
        
    def move(self, level: 'Level', pacman: 'Pacman'):
        # Simplified movement - in a real game, implement proper pathfinding
        possible_directions = self.get_possible_directions(level)
        
        if not possible_directions:
            return
            
        if len(possible_directions) > 1:
            self.direction = random.choice(possible_directions)
        else:
            self.direction = possible_directions[0]
            
        dx, dy = self.direction.value
        self.x += dx * self.speed * 0.1  # Slower movement
        self.y += dy * self.speed * 0.1
        
        # Wrap around
        if self.x < 0:
            self.x = GRID_WIDTH - 1
        elif self.x >= GRID_WIDTH:
            self.x = 0
            
    def get_possible_directions(self, level: 'Level') -> List[Direction]:
        directions = []
        for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            if direction != self.get_opposite_direction() and not self.would_collide(level, direction):
                directions.append(direction)
        return directions or [self.get_opposite_direction()]
    
    def get_opposite_direction(self) -> Direction:
        if self.direction == Direction.UP:
            return Direction.DOWN
        elif self.direction == Direction.DOWN:
            return Direction.UP
        elif self.direction == Direction.LEFT:
            return Direction.RIGHT
        else:
            return Direction.LEFT
            
    def would_collide(self, level: 'Level', direction: Direction) -> bool:
        dx, dy = direction.value
        new_x = int(self.x + dx)
        new_y = int(self.y + dy)
        
        # Check if out of bounds (wrapping is handled in move)
        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
            return False
            
        # Check for walls
        for wall in level.walls:
            if wall.x == new_x and wall.y == new_y and not wall.is_gate:
                return True
                
        return False
    
    def draw(self, screen: pygame.Surface):
        if self.state == GhostState.FRIGHTENED:
            color = (0, 0, 139)  # Dark blue when frightened
        elif self.state == GhostState.EATEN:
            color = (200, 200, 200)  # Faint gray when eaten
        else:
            color = self.color
            
        # Draw ghost body
        ghost_rect = self.rect.copy()
        ghost_rect.y += 50  # Offset for HUD
        pygame.draw.rect(screen, color, ghost_rect, 0, 10)
        
        # Draw eyes
        eye_radius = 3
        left_eye_pos = (ghost_rect.centerx - 4, ghost_rect.centery - 2)
        right_eye_pos = (ghost_rect.centerx + 4, ghost_rect.centery - 2)
        pygame.draw.circle(screen, WHITE, left_eye_pos, eye_radius + 2)
        pygame.draw.circle(screen, WHITE, right_eye_pos, eye_radius + 2)
        
        # Draw pupils
        pupil_offset = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0)
        }.get(self.eye_direction, (0, 0))
        
        pygame.draw.circle(screen, (0, 0, 0), 
                         (left_eye_pos[0] + pupil_offset[0] * 2, 
                          left_eye_pos[1] + pupil_offset[1] * 2), 
                         eye_radius - 1)
        pygame.draw.circle(screen, (0, 0, 0),
                         (right_eye_pos[0] + pupil_offset[0] * 2,
                          right_eye_pos[1] + pupil_offset[1] * 2),
                         eye_radius - 1)

class Pacman(GameObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, YELLOW)
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.speed = 2.0
        self.lives = 3
        self.score = 0
        self.power_pellet_active = False
        self.power_pellet_timer = 0
        self.mouth_angle = 45
        self.mouth_direction = -1  # -1 for closing, 1 for opening
        self.mouth_speed = 2
        
    def update(self, level: 'Level'):
        # Handle power pellet timer
        if self.power_pellet_active:
            self.power_pellet_timer -= 1
            if self.power_pellet_timer <= 0:
                self.power_pellet_active = False
                # Reset ghost states
                for ghost in level.ghosts:
                    if ghost.state != GhostState.EATEN:
                        ghost.state = GhostState.CHASE
        
        # Animate mouth
        self.mouth_angle += self.mouth_direction * self.mouth_speed
        if self.mouth_angle <= 0 or self.mouth_angle >= 45:
            self.mouth_direction *= -1
        
        # Try to change direction if needed
        if self.direction != self.next_direction:
            if not self.will_collide(level, self.next_direction):
                self.direction = self.next_direction
        
        # Move in current direction
        if not self.will_collide(level, self.direction):
            dx, dy = self.direction.value
            self.x += dx * self.speed * 0.1
            self.y += dy * self.speed * 0.1
            
            # Wrap around
            if self.x < 0:
                self.x = GRID_WIDTH - 1
            elif self.x >= GRID_WIDTH:
                self.x = 0
                
        # Check for pellet collisions
        self.check_pellet_collision(level)
        
        # Update rect for collision detection
        self.update_rect()
    
    def will_collide(self, level: 'Level', direction: Direction) -> bool:
        dx, dy = direction.value
        new_x = int(self.x + dx)
        new_y = int(self.y + dy)
        
        # Check if out of bounds (wrapping is handled in move)
        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
            return False
            
        # Check for walls
        for wall in level.walls:
            if wall.x == new_x and wall.y == new_y and not wall.is_gate:
                return True
                
        return False
    
    def check_pellet_collision(self, level: 'Level'):
        for pellet in level.pellets:
            if not pellet.eaten and math.dist((self.x, self.y), (pellet.x, pellet.y)) < 0.5:
                pellet.eaten = True
                if pellet.is_power_pellet:
                    self.score += 50
                    self.activate_power_pellet()
                else:
                    self.score += 10
                
                # Check if level is complete
                if all(p.eaten for p in level.pellets):
                    level.complete = True
    
    def activate_power_pellet(self):
        self.power_pellet_active = True
        self.power_pellet_timer = 10 * FPS  # 10 seconds
        # Set all ghosts to frightened state
        for ghost in level.ghosts:
            if ghost.state != GhostState.EATEN:
                ghost.state = GhostState.FRIGHTENED
                ghost.frightened_timer = 10 * FPS
    
    def draw(self, screen: pygame.Surface):
        # Draw Pac-Man as a circle with a mouth
        center_x = int(self.x * GRID_SIZE + GRID_SIZE // 2)
        center_y = int(self.y * GRID_SIZE + GRID_SIZE // 2 + 50)  # Offset for HUD
        radius = GRID_SIZE // 2 - 2
        
        # Calculate mouth angles based on direction and mouth_angle
        angle_offset = {
            Direction.RIGHT: 0,
            Direction.UP: 90,
            Direction.LEFT: 180,
            Direction.DOWN: 270
        }.get(self.direction, 0)
        
        start_angle = math.radians(angle_offset + self.mouth_angle)
        end_angle = math.radians(angle_offset + 360 - self.mouth_angle)
        
        # Draw Pac-Man
        pygame.draw.arc(screen, self.color, 
                       (center_x - radius, center_y - radius, 
                        radius * 2, radius * 2),
                       start_angle, end_angle, radius * 2)
        
        # Draw the mouth lines
        pygame.draw.line(screen, self.color, 
                        (center_x, center_y),
                        (center_x + math.cos(start_angle) * radius,
                         center_y + math.sin(start_angle) * radius), 2)
        pygame.draw.line(screen, self.color,
                        (center_x, center_y),
                        (center_x + math.cos(end_angle) * radius,
                         center_y + math.sin(end_angle) * radius), 2)
        
        # Draw a small eye
        eye_radius = 2
        eye_offset = radius // 2
        eye_x = center_x + math.cos(math.radians(angle_offset)) * eye_offset
        eye_y = center_y + math.sin(math.radians(angle_offset)) * eye_offset
        pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), eye_radius)

class Level:
    def __init__(self, level_num: int = 1):
        self.level_num = level_num
        self.walls: List[Wall] = []
        self.pellets: List[Pellet] = []
        self.ghosts: List[Ghost] = []
        self.pacman: Optional[Pacman] = None
        self.complete = False
        self.setup_level()
        
    def setup_level(self):
        # Create a simple maze
        # Outer walls
        for x in range(GRID_WIDTH):
            self.walls.append(Wall(x, 0))
            self.walls.append(Wall(x, GRID_HEIGHT - 1))
            
        for y in range(GRID_HEIGHT):
            self.walls.append(Wall(0, y))
            self.walls.append(Wall(GRID_WIDTH - 1, y))
        
        # Add some inner walls
        for x in range(5, GRID_WIDTH - 5):
            if x != GRID_WIDTH // 2:
                self.walls.append(Wall(x, 5))
                self.walls.append(Wall(x, GRID_HEIGHT - 6))
                
        # Add a gate for the ghost house
        gate = Wall(GRID_WIDTH // 2, 5)
        gate.is_gate = True
        self.walls.append(gate)
        
        # Add pellets
        for x in range(2, GRID_WIDTH - 2):
            for y in range(2, GRID_HEIGHT - 2):
                # Skip walls and ghost house area
                if not any(wall.x == x and wall.y == y for wall in self.walls) and \
                   not (x > GRID_WIDTH // 2 - 3 and x < GRID_WIDTH // 2 + 3 and y > 2 and y < 8):
                    is_power = (x == 2 and y == 2) or \
                              (x == GRID_WIDTH - 3 and y == 2) or \
                              (x == 2 and y == GRID_HEIGHT - 3) or \
                              (x == GRID_WIDTH - 3 and y == GRID_HEIGHT - 3)
                    self.pellets.append(Pellet(x, y, is_power))
        
        # Add Pac-Man
        self.pacman = Pacman(GRID_WIDTH // 2, GRID_HEIGHT - 3)
        
        # Add ghosts
        self.ghosts = [
            Ghost(GRID_WIDTH // 2 - 2, 7, RED, "Blinky"),
            Ghost(GRID_WIDTH // 2 + 2, 7, PINK, "Pinky"),
            Ghost(GRID_WIDTH // 2 - 2, 8, CYAN, "Inky"),
            Ghost(GRID_WIDTH // 2 + 2, 8, ORANGE, "Clyde")
        ]
    
    def update(self):
        self.pacman.update(self)
        
        # Update ghosts
        for ghost in self.ghosts:
            ghost.update(self, self.pacman)
            
            # Check ghost collisions with Pac-Man
            if (ghost.state != GhostState.EATEN and 
                math.dist((ghost.x, ghost.y), (self.pacman.x, self.pacman.y)) < 0.8):
                if ghost.state == GhostState.FRIGHTENED:
                    # Eat ghost
                    ghost.state = GhostState.EATEN
                    self.pacman.score += 200
                elif ghost.state != GhostState.EATEN:
                    # Lose a life
                    self.pacman.lives -= 1
                    if self.pacman.lives <= 0:
                        return "GAME_OVER"
                    else:
                        # Reset positions
                        self.pacman.x = GRID_WIDTH // 2
                        self.pacman.y = GRID_HEIGHT - 3
                        self.pacman.direction = Direction.RIGHT
                        self.pacman.next_direction = Direction.RIGHT
                        
                        for g in self.ghosts:
                            g.x = g.start_x
                            g.y = g.start_y
                            g.state = GhostState.SCATTER
                            g.in_house = True
        
        if self.complete:
            return "LEVEL_COMPLETE"
            
        return "PLAYING"
    
    def draw(self, screen: pygame.Surface):
        # Draw background
        screen.fill(BLACK)
        
        # Draw HUD
        self.draw_hud(screen)
        
        # Draw walls
        for wall in self.walls:
            wall.draw(screen)
            
        # Draw pellets
        for pellet in self.pellets:
            pellet.draw(screen)
            
        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw(screen)
            
        # Draw Pac-Man
        self.pacman.draw(screen)
    
    def draw_hud(self, screen: pygame.Surface):
        # Draw score and lives at the top
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.pacman.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.pacman.lives}", True, WHITE)
        level_text = font.render(f"Level: {self.level_num}", True, WHITE)
        
        screen.blit(score_text, (20, 10))
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 20, 10))
        
        # Draw power pellet timer if active
        if self.pacman.power_pellet_active:
            power_width = 200
            power_height = 10
            power_x = SCREEN_WIDTH // 2 - power_width // 2
            power_y = SCREEN_HEIGHT - 30
            
            # Background
            pygame.draw.rect(screen, GRAY, (power_x, power_y, power_width, power_height))
            
            # Timer bar
            timer_width = int(power_width * (self.pacman.power_pellet_timer / (10 * FPS)))
            pygame.draw.rect(screen, CYAN, (power_x, power_y, timer_width, power_height))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac Pro - Professional Pac-Man Management")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        self.current_level = 1
        self.level = None
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 36)
        self.setup_menu()
        
    def setup_menu(self):
        self.state = GameState.MENU
        self.menu_items = ["Start Game", "How to Play", "Quit"]
        self.selected_item = 0
        
    def setup_game(self):
        self.current_level = 1
        self.level = Level(self.current_level)
        self.state = GameState.PLAYING
        
    def next_level(self):
        self.current_level += 1
        self.level = Level(self.current_level)
        self.state = GameState.PLAYING
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    self.handle_menu_input(event)
                elif self.state == GameState.PLAYING:
                    self.handle_game_input(event)
                elif self.state == GameState.LEVEL_COMPLETE or self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        if self.state == GameState.LEVEL_COMPLETE:
                            self.next_level()
                        else:
                            self.setup_menu()
    
    def handle_menu_input(self, event):
        if event.key == pygame.K_UP:
            self.selected_item = (self.selected_item - 1) % len(self.menu_items)
        elif event.key == pygame.K_DOWN:
            self.selected_item = (self.selected_item + 1) % len(self.menu_items)
        elif event.key == pygame.K_RETURN:
            if self.selected_item == 0:  # Start Game
                self.setup_game()
            elif self.selected_item == 1:  # How to Play
                pass  # Could implement instructions screen
            elif self.selected_item == 2:  # Quit
                self.running = False
    
    def handle_game_input(self, event):
        if event.key == pygame.K_UP:
            self.level.pacman.next_direction = Direction.UP
        elif event.key == pygame.K_DOWN:
            self.level.pacman.next_direction = Direction.DOWN
        elif event.key == pygame.K_LEFT:
            self.level.pacman.next_direction = Direction.LEFT
        elif event.key == pygame.K_RIGHT:
            self.level.pacman.next_direction = Direction.RIGHT
        elif event.key == pygame.K_ESCAPE:
            self.state = GameState.PAUSED
    
    def update(self):
        if self.state == GameState.PLAYING and self.level:
            result = self.level.update()
            if result == "LEVEL_COMPLETE":
                self.state = GameState.LEVEL_COMPLETE
            elif result == "GAME_OVER":
                self.state = GameState.GAME_OVER
    
    def draw(self):
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING and self.level:
            self.level.draw(self.screen)
        elif self.state == GameState.LEVEL_COMPLETE:
            self.level.draw(self.screen)
            self.draw_message("Level Complete! Press ENTER to continue", GREEN)
        elif self.state == GameState.GAME_OVER:
            self.level.draw(self.screen)
            self.draw_message("Game Over! Press ENTER to continue", RED)
        elif self.state == GameState.PAUSED:
            self.level.draw(self.screen)
            self.draw_message("Paused - Press ESC to resume", WHITE)
            
        pygame.display.flip()
    
    def draw_menu(self):
        self.screen.fill(BLACK)
        title = self.font.render("PAC PRO", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        for i, item in enumerate(self.menu_items):
            color = YELLOW if i == self.selected_item else WHITE
            text = self.small_font.render(item, True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 50))
        
        # Draw instructions
        instructions = [
            "Use ARROW KEYS to navigate",
            "Press ENTER to select",
            "Eat all pellets to complete the level",
            "Avoid ghosts or eat them when powered up!"
        ]
        
        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 450 + i * 30))
    
    def draw_message(self, message, color):
        # Dark overlay
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(s, (0, 0))
        
        # Message
        text = self.font.render(message, True, color)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                               SCREEN_HEIGHT // 2 - text.get_height() // 2))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
