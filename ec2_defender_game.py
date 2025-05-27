import pygame
import sys
import random
import os
import time

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EC2 Defender")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 128, 255)
PURPLE = (200, 0, 255)
ORANGE = (255, 165, 0)
DARK_GRAY = (50, 50, 50)

# Set up fonts
font = pygame.font.SysFont(None, 24)
score_font = pygame.font.SysFont(None, 36)
popup_font = pygame.font.SysFont(None, 32)
title_font = pygame.font.SysFont(None, 48)
subtitle_font = pygame.font.SysFont(None, 36)
instruction_font = pygame.font.SysFont(None, 28)
button_font = pygame.font.SysFont(None, 32)

# Load background
background_image = pygame.image.load(os.path.join('assets', 'background.png'))
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Load player image
player_image = pygame.image.load(os.path.join('assets', 'ec2.png'))
player_rect = player_image.get_rect()
player_rect.centerx = WIDTH // 2
player_rect.bottom = HEIGHT - 20
player_speed = 5

# Load enemy images
ddos_image = pygame.image.load(os.path.join('assets', 'ddos.png'))
malware_image = pygame.image.load(os.path.join('assets', 'malware.png'))

# Load powerup images
shield_image = pygame.image.load(os.path.join('assets', 'shield.png'))
waf_image = pygame.image.load(os.path.join('assets', 'waf.png'))

# Scale images
ddos_image = pygame.transform.scale(ddos_image, (50, 50))
malware_image = pygame.transform.scale(malware_image, (50, 50))
shield_image = pygame.transform.scale(shield_image, (40, 40))
waf_image = pygame.transform.scale(waf_image, (40, 40))

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.text_surf = button_font.render(text, True, WHITE)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        surface.blit(self.text_surf, self.text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

# Laser class
class Laser:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 4, 15)
        self.speed = 10
        self.color = GREEN
        
    def update(self):
        self.rect.y -= self.speed
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        
    def is_offscreen(self):
        return self.rect.bottom < 0

# Enemy class
class Enemy:
    def __init__(self, image, enemy_type):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.uniform(1.0, 3.0)
        self.type = enemy_type
        self.points = 20 if enemy_type == "DDoS" else 10
        
    def update(self, speed_multiplier):
        self.rect.y += self.speed * speed_multiplier
        
    def draw(self, surface):
        # Draw the enemy image
        surface.blit(self.image, self.rect)
        
        # Draw the label above the enemy
        label_color = RED if self.type == "DDoS" else YELLOW
        label_text = font.render(self.type, True, label_color)
        label_rect = label_text.get_rect(centerx=self.rect.centerx, bottom=self.rect.top - 5)
        surface.blit(label_text, label_rect)
        
    def is_offscreen(self):
        return self.rect.top > HEIGHT

# PowerUp class
class PowerUp:
    def __init__(self, image, powerup_type):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-150, -50)
        self.speed = 2.0
        self.type = powerup_type
        self.duration = 5.0  # seconds
        
    def update(self):
        self.rect.y += self.speed
        
    def draw(self, surface):
        # Draw the powerup image
        surface.blit(self.image, self.rect)
        
        # Draw the label above the powerup
        label_color = BLUE if self.type == "shield" else GREEN
        label_text = font.render("AWS Shield" if self.type == "shield" else "AWS WAF", True, label_color)
        label_rect = label_text.get_rect(centerx=self.rect.centerx, bottom=self.rect.top - 5)
        surface.blit(label_text, label_rect)
        
    def is_offscreen(self):
        return self.rect.top > HEIGHT

# Popup notification class
class Popup:
    def __init__(self, text, duration=2.0):
        self.text = text
        self.duration = duration
        self.start_time = time.time()
        self.text_surface = popup_font.render(text, True, WHITE)
        self.rect = self.text_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.background = pygame.Rect(0, 0, self.rect.width + 20, self.rect.height + 20)
        self.background.center = self.rect.center
        
    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.background, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.background, 2, border_radius=10)
        surface.blit(self.text_surface, self.rect)
        
    def is_expired(self):
        return time.time() - self.start_time > self.duration

# Function to display instruction screen
def show_instruction_screen():
    screen.blit(background_image, (0, 0))
    
    # Create a semi-transparent overlay for better text readability
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # Black with 150 alpha (semi-transparent)
    screen.blit(overlay, (0, 0))
    
    # Title
    title_text = title_font.render("EC2 Defender", True, CYAN)
    title_rect = title_text.get_rect(centerx=WIDTH//2, top=50)
    screen.blit(title_text, title_rect)
    
    # Create main content box
    content_box = pygame.Rect(WIDTH//8, 120, WIDTH*3//4, HEIGHT - 200)
    pygame.draw.rect(screen, (0, 0, 0, 200), content_box, border_radius=15)
    pygame.draw.rect(screen, BLUE, content_box, 2, border_radius=15)
    
    # Instructions header
    instructions_header = subtitle_font.render("How to Play:", True, ORANGE)
    instructions_header_rect = instructions_header.get_rect(centerx=WIDTH//2, top=content_box.top + 20)
    screen.blit(instructions_header, instructions_header_rect)
    
    # Controls section
    controls_y = instructions_header_rect.bottom + 20
    pygame.draw.line(screen, YELLOW, (content_box.left + 20, controls_y - 5), 
                    (content_box.right - 20, controls_y - 5), 1)
    
    controls_text = [
        "CONTROLS:",
        "• LEFT/RIGHT Arrow Keys: Move EC2 instance",
        "• SPACEBAR: Shoot lasers",
        "• ESC: Quit game"
    ]
    
    for i, text in enumerate(controls_text):
        color = YELLOW if i == 0 else WHITE
        line = instruction_font.render(text, True, color)
        screen.blit(line, (content_box.left + 30, controls_y + i*28))
    
    # Objective
    objective_y = controls_y + len(controls_text)*28 + 15
    pygame.draw.line(screen, YELLOW, (content_box.left + 20, objective_y - 5), 
                    (content_box.right - 20, objective_y - 5), 1)
    
    objective_text = [
        "OBJECTIVE:",
        "• Defend your EC2 instance from attacks",
        "• Destroy enemies to earn points",
        "• Game over when 5 enemies reach the bottom"
    ]
    
    for i, text in enumerate(objective_text):
        color = YELLOW if i == 0 else WHITE
        line = instruction_font.render(text, True, color)
        screen.blit(line, (content_box.left + 30, objective_y + i*28))
    
    # Power-ups
    powerup_y = objective_y + len(objective_text)*28 + 15
    pygame.draw.line(screen, YELLOW, (content_box.left + 20, powerup_y - 5), 
                    (content_box.right - 20, powerup_y - 5), 1)
    
    powerup_text = [
        "POWER-UPS:",
        "• AWS Shield: 5 seconds of invincibility",
        "• AWS WAF: 5 seconds of invincibility"
    ]
    
    for i, text in enumerate(powerup_text):
        color = YELLOW if i == 0 else WHITE
        line = instruction_font.render(text, True, color)
        screen.blit(line, (content_box.left + 30, powerup_y + i*28))
    
    # No power-up images on instruction screen
    
    # Start prompt with button-like appearance
    start_box = pygame.Rect(WIDTH//2 - 150, HEIGHT - 80, 300, 40)
    
    # Animated button effect
    if int(time.time() * 2) % 2 == 0:
        pygame.draw.rect(screen, GREEN, start_box, border_radius=10)
        pygame.draw.rect(screen, WHITE, start_box, 2, border_radius=10)
        start_text = instruction_font.render("Press any key to start", True, BLACK)
    else:
        pygame.draw.rect(screen, (0, 100, 0), start_box, border_radius=10)
        pygame.draw.rect(screen, WHITE, start_box, 2, border_radius=10)
        start_text = instruction_font.render("Press any key to start", True, WHITE)
    
    start_rect = start_text.get_rect(center=start_box.center)
    screen.blit(start_text, start_rect)
    
    # Add "developed using Amazon Q CLI" at the bottom with more space
    dev_text = font.render("Developed using Amazon Q CLI", True, (255, 165, 0))  # Orange color
    dev_rect = dev_text.get_rect(centerx=WIDTH//2, bottom=HEIGHT - 10)
    screen.blit(dev_text, dev_rect)
    
    pygame.display.flip()
    
    # Wait for key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
        
        # Update animated button
        if int(time.time() * 2) % 2 == 0:
            pygame.draw.rect(screen, GREEN, start_box, border_radius=10)
            pygame.draw.rect(screen, WHITE, start_box, 2, border_radius=10)
            start_text = instruction_font.render("Press any key to start", True, BLACK)
        else:
            pygame.draw.rect(screen, (0, 100, 0), start_box, border_radius=10)
            pygame.draw.rect(screen, WHITE, start_box, 2, border_radius=10)
            start_text = instruction_font.render("Press any key to start", True, WHITE)
        
        start_rect = start_text.get_rect(center=start_box.center)
        screen.blit(start_text, start_rect)
        
        pygame.display.update(start_box)
        pygame.time.delay(100)

# Function to display game over screen
def show_game_over_screen(final_score):
    # Create buttons
    button_width = 200
    button_height = 50
    button_y = HEIGHT - 200
    button_spacing = 70
    
    restart_button = Button(WIDTH//2 - button_width//2, button_y, 
                           button_width, button_height, "Restart", BLUE, CYAN)
    
    instructions_button = Button(WIDTH//2 - button_width//2, button_y + button_spacing, 
                               button_width, button_height, "Instructions", BLUE, CYAN)
    
    quit_button = Button(WIDTH//2 - button_width//2, button_y + button_spacing*2, 
                        button_width, button_height, "Quit", RED, ORANGE)
    
    buttons = [restart_button, instructions_button, quit_button]
    
    # Game over screen loop
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_clicked = True
        
        # Check button interactions
        for button in buttons:
            button.check_hover(mouse_pos)
            if mouse_clicked and button.is_clicked(mouse_pos, mouse_clicked):
                if button == restart_button:
                    return "restart"
                elif button == instructions_button:
                    return "instructions"
                elif button == quit_button:
                    pygame.quit()
                    sys.exit()
        
        # Draw game over screen
        screen.blit(background_image, (0, 0))
        
        # Game over title
        title_text = title_font.render("GAME OVER", True, RED)
        title_rect = title_text.get_rect(centerx=WIDTH//2, top=100)
        screen.blit(title_text, title_rect)
        
        # Final score
        score_text = score_font.render(f"Final Score: {final_score}", True, WHITE)
        score_rect = score_text.get_rect(centerx=WIDTH//2, top=title_rect.bottom + 50)
        screen.blit(score_text, score_rect)
        
        # Draw buttons
        for button in buttons:
            button.draw(screen)
        
        pygame.display.flip()
        pygame.time.delay(30)

# Main game function
def run_game():
    # Game variables
    enemies = []
    lasers = []
    powerups = []
    popups = []
    enemy_spawn_delay = 1.0  # seconds
    last_spawn_time = time.time()
    difficulty_multiplier = 1.0
    difficulty_increase_rate = 0.05
    difficulty_increase_interval = 5.0  # seconds
    last_difficulty_increase = time.time()
    laser_cooldown = 0.3  # seconds
    last_laser_time = 0
    powerup_spawn_chance = 0.003  # Reduced from 0.01 to 0.003 (0.3% chance per frame)
    score = 0
    missed_enemies = 0
    max_missed_enemies = 5
    
    # Reset player position
    player_rect.centerx = WIDTH // 2
    player_rect.bottom = HEIGHT - 20
    
    # Player state
    is_invincible = False
    invincibility_end_time = 0
    invincibility_flash = False
    invincibility_flash_interval = 0.1
    last_flash_time = 0
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    return "quit"
        
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
            player_rect.x += player_speed
        
        # Shooting lasers
        current_time = time.time()
        if keys[pygame.K_SPACE] and current_time - last_laser_time > laser_cooldown:
            lasers.append(Laser(player_rect.centerx - 2, player_rect.top))
            last_laser_time = current_time
        
        # Check invincibility status
        if is_invincible and current_time > invincibility_end_time:
            is_invincible = False
            popups.append(Popup("Protection Expired", 1.5))
        
        # Invincibility flashing effect
        if is_invincible and current_time - last_flash_time > invincibility_flash_interval:
            invincibility_flash = not invincibility_flash
            last_flash_time = current_time
        
        # Spawn enemies
        if current_time - last_spawn_time > enemy_spawn_delay:
            enemy_type = random.choice(["DDoS", "Malware"])
            if enemy_type == "DDoS":
                enemies.append(Enemy(ddos_image, enemy_type))
            else:
                enemies.append(Enemy(malware_image, enemy_type))
            last_spawn_time = current_time
            
        # Randomly spawn powerups (less frequently than enemies)
        if random.random() < powerup_spawn_chance:
            powerup_type = random.choice(["shield", "waf"])
            if powerup_type == "shield":
                powerups.append(PowerUp(shield_image, powerup_type))
            else:
                powerups.append(PowerUp(waf_image, powerup_type))
        
        # Increase difficulty over time
        if current_time - last_difficulty_increase > difficulty_increase_interval:
            difficulty_multiplier += difficulty_increase_rate
            enemy_spawn_delay = max(0.2, enemy_spawn_delay * 0.95)  # Decrease spawn delay, but not below 0.2
            last_difficulty_increase = current_time
        
        # Update lasers
        for laser in lasers[:]:
            laser.update()
            if laser.is_offscreen():
                lasers.remove(laser)
        
        # Update enemies
        for enemy in enemies[:]:
            enemy.update(difficulty_multiplier)
            if enemy.is_offscreen():
                enemies.remove(enemy)
                missed_enemies += 1
                popups.append(Popup(f"Enemy reached EC2 region! ({missed_enemies}/{max_missed_enemies})", 1.5))
                
                # Check for game over condition
                if missed_enemies >= max_missed_enemies:
                    return show_game_over_screen(score)
        
        # Update powerups
        for powerup in powerups[:]:
            powerup.update()
            if powerup.is_offscreen():
                powerups.remove(powerup)
        
        # Update popups
        for popup in popups[:]:
            if popup.is_expired():
                popups.remove(popup)
        
        # Check for collisions between lasers and enemies
        for laser in lasers[:]:
            for enemy in enemies[:]:
                if laser.rect.colliderect(enemy.rect):
                    score += enemy.points
                    enemies.remove(enemy)
                    if laser in lasers:  # Check if laser still exists
                        lasers.remove(laser)
                    break
        
        # Check for collisions between player and powerups
        for powerup in powerups[:]:
            if player_rect.colliderect(powerup.rect):
                is_invincible = True
                invincibility_end_time = current_time + powerup.duration
                
                if powerup.type == "shield":
                    popups.append(Popup(f"AWS Shield Activated for {int(powerup.duration)}s", 2.0))
                else:  # waf
                    popups.append(Popup(f"AWS WAF Activated for {int(powerup.duration)}s", 2.0))
                    
                powerups.remove(powerup)
        
        # Check for collisions between player and enemies (if not invincible)
        if not is_invincible:
            for enemy in enemies[:]:
                if player_rect.colliderect(enemy.rect):
                    # In a full game, this would handle player damage or game over
                    # For now, just remove the enemy
                    enemies.remove(enemy)
                    popups.append(Popup("EC2 instance hit!", 1.5))
                    break
        
        # Draw background
        screen.blit(background_image, (0, 0))
        
        # Draw lasers
        for laser in lasers:
            laser.draw(screen)
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw powerups
        for powerup in powerups:
            powerup.draw(screen)
        
        # Draw player (with flashing effect if invincible)
        if not is_invincible or invincibility_flash:
            screen.blit(player_image, player_rect)
        
        # Draw EC2 instance label below player
        ec2_label = font.render("EC2 instance", True, CYAN)
        ec2_label_rect = ec2_label.get_rect(centerx=player_rect.centerx, top=player_rect.bottom + 5)
        screen.blit(ec2_label, ec2_label_rect)
        
        # Draw shield indicator when active
        if is_invincible:
            shield_time_left = int(invincibility_end_time - current_time)
            shield_text = font.render(f"Protected: {shield_time_left}s", True, GREEN)
            screen.blit(shield_text, (10, 40))
            
            # Draw shield effect around player
            pygame.draw.circle(screen, BLUE if invincibility_flash else PURPLE, 
                              player_rect.center, player_rect.width, 2)
        
        # Draw popups
        for popup in popups:
            popup.draw(screen)
        
        # Display difficulty level
        difficulty_text = font.render(f"Difficulty: {difficulty_multiplier:.1f}x", True, RED)
        screen.blit(difficulty_text, (10, 10))
        
        # Display score
        score_text = score_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
        
        # Display missed enemies counter
        missed_text = font.render(f"Enemies Missed: {missed_enemies}/{max_missed_enemies}", True, ORANGE)
        screen.blit(missed_text, (10, 70))
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    return "quit"

# Main game loop
def main():
    action = "instructions"
    
    while action != "quit":
        if action == "instructions":
            show_instruction_screen()
            action = run_game()
        elif action == "restart":
            action = run_game()

# Start the game
if __name__ == "__main__":
    main()
