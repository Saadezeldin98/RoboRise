import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 0, 255)
ORANGE = (255, 165, 0)

# Screen size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RoboRise")

# Object size
robot_width = 50
robot_height = 50
laser_width = 4
laser_height = 20
laser_speed = 6
enemy_health = 3

# Images
robot_image = pygame.image.load("images/Robot.png")
robot_image = pygame.transform.scale(robot_image, (robot_width, robot_height))
enemy_image = pygame.image.load("images/enemy.png")
enemy_image = pygame.transform.scale(enemy_image, (50, 50))
background_img = pygame.image.load("images/Space.png")
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
boss_image = pygame.image.load("images/boss_blob.png")
boss_image = pygame.transform.scale(boss_image, (100, 100))

# Powerup images and types
powerup_images = [
    pygame.image.load("images/gift.png"),  # Standard gift
]
powerup_images_scaled = [pygame.transform.scale(img, (50, 50)) for img in powerup_images]
POWERUP_TYPES = ["Extra Life", "Double Laser", "Triple Laser", "Score Boost"]  # Add more types if you like

# Sounds
pygame.mixer.music.load("sounds/bg_music.wav")
pygame.mixer.music.play(-1, 0.0)
laser_sound = pygame.mixer.Sound("sounds/hit.wav")
enemy_death_sound = pygame.mixer.Sound("sounds/monster-death.wav")

# Fonts
font = pygame.font.SysFont("Arial", 24)
large_font = pygame.font.SysFont("Arial", 48)

def show_message(message):
    screen.fill(BLACK)
    text = large_font.render(message, True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.update()
    pygame.time.delay(3000)

def show_options():
    while True:
        screen.fill(BLACK)
        title = large_font.render("Options", True, GREEN)
        back_text = font.render("Press [B] to go back", True, GREEN)
        explanation = font.render("RoboRise is a space shooter game.", True, GREEN)
        control_lines = ["Controls:", "[A] - Left", "[D] - Right", "[W] - Up", "[S] - Down", "[K] - Shoot"]

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(explanation, (SCREEN_WIDTH // 2 - explanation.get_width() // 2, 180))
        for i, line in enumerate(control_lines):
            text = font.render(line, True, GREEN)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 220 + i * 30))
        screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 420))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                return

def start_menu():
    while True:
        screen.fill(BLACK)
        title = large_font.render("RoboRise", True, GREEN)
        start = font.render("Press [S] to start the game", True, GREEN)
        options = font.render("Press [O] for options", True, GREEN)
        quit_text = font.render("Press [Q] to quit the game", True, GREEN)

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
        screen.blit(start, (SCREEN_WIDTH // 2 - start.get_width() // 2, 300))
        screen.blit(options, (SCREEN_WIDTH // 2 - options.get_width() // 2, 350))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 400))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    return
                elif event.key == pygame.K_o:
                    show_options()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def create_boss(level):
    return {
        "rect": pygame.Rect(SCREEN_WIDTH // 2 - 50, 50, 100, 100),
        "health": 15 + level * 5,
        "dx": 4 + level,
    }

def game_loop():
    level = 1
    boss = create_boss(level)

    background_y = 0
    robot_x = SCREEN_WIDTH // 2 - robot_width // 2
    robot_y = SCREEN_HEIGHT - robot_height - 10
    laser_list = []
    boss_lasers = []
    enemies = []
    powerups = []
    score = 0
    robot_lives = 5
    double_laser_active = False
    triple_laser_active = False

    powerup_speed = 1
    enemy_speed = 2
    max_enemies = 3
    boss_laser_speed = 4
    boss_laser_delay = 2000
    last_boss_shot_time = pygame.time.get_ticks()
    powerup_spawn_rate = 600

    clock = pygame.time.Clock()
    running = True
    last_shot_time = 0
    shot_delay = 400

    while running:
        screen.blit(background_img, (0, background_y))
        screen.blit(background_img, (0, background_y - SCREEN_HEIGHT))
        background_y = (background_y + 1) % SCREEN_HEIGHT

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and robot_x > 0:
            robot_x -= 3
        if keys[pygame.K_d] and robot_x < SCREEN_WIDTH - robot_width:
            robot_x += 3
        if keys[pygame.K_w] and robot_y > 0:
            robot_y -= 3
        if keys[pygame.K_s] and robot_y < SCREEN_HEIGHT - robot_height:
            robot_y += 3
        if keys[pygame.K_k]:
            now = pygame.time.get_ticks()
            if now - last_shot_time > shot_delay:
                laser = pygame.Rect(robot_x + robot_width // 2 - laser_width // 2, robot_y, laser_width, laser_height)
                laser_list.append(laser)
                laser_sound.play()
                last_shot_time = now
                if double_laser_active:
                    laser2 = pygame.Rect(robot_x + robot_width // 2 + 10, robot_y, laser_width, laser_height)
                    laser_list.append(laser2)
                if triple_laser_active:
                        laser3 = pygame.Rect(robot_x + robot_width // 3 + 10, robot_y, laser_width, laser_height)
                        laser_list.append(laser3)

        boss["rect"].x += boss["dx"]
        if boss["rect"].left <= 0 or boss["rect"].right >= SCREEN_WIDTH:
            boss["dx"] *= -1

        current_time = pygame.time.get_ticks()
        if current_time - last_boss_shot_time > boss_laser_delay:
            bl = pygame.Rect(boss["rect"].centerx - 3, boss["rect"].bottom, 6, 20)
            boss_lasers.append(bl)
            last_boss_shot_time = current_time

        for laser in laser_list[:]:
            laser.y -= laser_speed
            if laser.y < 0:
                laser_list.remove(laser)
            elif boss["rect"].colliderect(laser):
                boss["health"] -= 1
                laser_list.remove(laser)

        for bl in boss_lasers[:]:
            bl.y += boss_laser_speed
            if bl.y > SCREEN_HEIGHT:
                boss_lasers.remove(bl)
            elif pygame.Rect(robot_x, robot_y, robot_width, robot_height).colliderect(bl):
                boss_lasers.remove(bl)
                robot_lives -= 1
                if robot_lives <= 0:
                    show_message("GAME OVER")
                    return

        while len(enemies) < max_enemies:
            x = random.randint(0, SCREEN_WIDTH - 50)
            enemies.append({"rect": pygame.Rect(x, 0, 50, 50), "health": enemy_health})

        for enemy in enemies[:]:
            enemy["rect"].y += enemy_speed
            if enemy["rect"].y > SCREEN_HEIGHT:
                enemies.remove(enemy)
            if enemy["rect"].colliderect(pygame.Rect(robot_x, robot_y, robot_width, robot_height)):
                robot_lives -= 1
                if enemy in enemies:
                    enemies.remove(enemy)
                if robot_lives <= 0:
                    show_message("GAME OVER")
                    return
            for laser in laser_list[:]:
                if laser.colliderect(enemy["rect"]):
                    enemy["health"] -= 1
                    laser_list.remove(laser)
                    if enemy["health"] <= 0:
                        enemy_death_sound.play()
                        score += 10
                        if enemy in enemies:
                            enemies.remove(enemy)

        if random.randint(1, powerup_spawn_rate) == 1:
            px = random.randint(0, SCREEN_WIDTH - 40)
            powerup_type = random.choice(POWERUP_TYPES)
            powerup_index = POWERUP_TYPES.index(powerup_type) % len(powerup_images_scaled)
            powerups.append({"rect": pygame.Rect(px, 0, 40, 40), "type": powerup_type, "image_index": powerup_index})

        for pu in powerups[:]:
            pu["rect"].y += powerup_speed
            if pu["rect"].y > SCREEN_HEIGHT:
                powerups.remove(pu)
            elif pygame.Rect(robot_x, robot_y, robot_width, robot_height).colliderect(pu["rect"]):
                if pu["type"] == "Extra Life":
                    robot_lives += 1
                elif pu["type"] == "Double Laser":
                    double_laser_active = True
                elif pu["type"] == "Triple Laser":
                    triple_laser_active = True
                elif pu["type"] == "Score Boost":
                    score += 100
                powerups.remove(pu)
            else:
                screen.blit(powerup_images_scaled[pu["image_index"]], pu["rect"])
                # --- This part adds text above the powerup ---
                text = font.render(pu["type"], True, WHITE)
                text_x = pu["rect"].centerx - text.get_width() // 2
                text_y = pu["rect"].top - 20
                screen.blit(text, (text_x, text_y))

        screen.blit(robot_image, (robot_x, robot_y))
        for laser in laser_list:
            pygame.draw.rect(screen, RED, laser)
        for bl in boss_lasers:
            pygame.draw.rect(screen, YELLOW, bl)
        for e in enemies:
            screen.blit(enemy_image, e["rect"])
            pygame.draw.rect(screen, BLACK, (e["rect"].x, e["rect"].top - 10, 50, 5))
            pygame.draw.rect(screen, GREEN, (e["rect"].x, e["rect"].top - 10, 50 * e["health"] / enemy_health, 5))

        screen.blit(boss_image, boss["rect"])
        pygame.draw.rect(screen, BLACK, (boss["rect"].x, boss["rect"].top - 15, 100, 10))
        pygame.draw.rect(screen, RED, (boss["rect"].x, boss["rect"].top - 15, 100 * boss["health"] / 15, 10))

        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 10, 10))

        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {robot_lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))

        if boss["health"] == 0:
            show_message(f"Level {level} complete.")
            level += 1
            boss = create_boss(level)

        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    start_menu()
    game_loop()
    pygame.quit()
    sys.exit()
