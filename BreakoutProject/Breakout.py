import pygame
import random
import time
import os

# Initialize
pygame.init()
pygame.mixer.init()

# Screen
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout Deluxe")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0),
          (0, 255, 0), (0, 128, 255), (75, 0, 130)]

# Sounds
hit_sound = pygame.mixer.Sound("sounds/hit.wav")
gameover_sound = pygame.mixer.Sound("sounds/gameover.wav")
pygame.mixer.music.load("sounds/bg_music.wav")
pygame.mixer.music.set_volume(0.3)
hit_sound.set_volume(1.0)
pygame.mixer.music.play(-1)

# Font
font = pygame.font.SysFont("arial", 24)
effect_font = pygame.font.SysFont("arial", 28, bold=True)

# Paddle
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle_speed = 7

# Ball
BALL_SPEED = 4
ball_list = [pygame.Rect(WIDTH // 2, HEIGHT // 2, 15, 15)]
ball_speed_list = [[BALL_SPEED, -BALL_SPEED]]
invisible_timer = 0

# Bricks
BRICK_ROWS, BRICK_COLS = 6, 10
BRICK_WIDTH = WIDTH // BRICK_COLS
BRICK_HEIGHT = 30

def create_bricks(rows, cols):
    bricks = []
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT, BRICK_WIDTH - 2, BRICK_HEIGHT - 2)
            bricks.append((rect, COLORS[row % len(COLORS)]))
    return bricks

bricks = create_bricks(BRICK_ROWS, BRICK_COLS)

# Power-up
gift_img = pygame.image.load("images/gift.png")
gift_rect = None
gift_speed = 4
gift_active = False
gift_type = ""
gift_effect_text = ""
gift_effect_time = 0

# Score & Level
score = 0
high_score = 0
next_gift_score = 30
level = 1

# Load previous high score
if os.path.exists("high_score.txt"):
    with open("high_score.txt", "r") as f:
        high_score = int(f.read())

def update_high_score():
    global high_score
    if score > high_score:
        high_score = score
    with open("high_score.txt", "w") as f:
        f.write(str(high_score))

# Background
background_img = pygame.image.load("images/background.png")
background_y = 0
background_speed = 1

def move_background():
    global background_y
    background_y += background_speed
    if background_y >= HEIGHT:
        background_y = 0

# Next Level
def next_level():
    global level, bricks, ball_list, ball_speed_list, paddle, gift_active, gift_rect, gift_type, next_gift_score, paddle_speed

    level += 1
    ball_list.clear()
    ball_speed_list.clear()
    ball_list.append(pygame.Rect(WIDTH // 2, HEIGHT // 2, 15, 15))
    speed_boost = BALL_SPEED + level
    ball_speed_list.append([speed_boost, -speed_boost])

    paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_speed = abs(paddle_speed)

    brick_rows = BRICK_ROWS + (level - 1)
    bricks = create_bricks(brick_rows, BRICK_COLS)

    gift_active = False
    gift_rect = None
    gift_type = ""
    next_gift_score += 30

# Game Loop
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60)
    WIN.fill(BLACK)
    move_background()
    WIN.blit(background_img, (0, background_y))
    WIN.blit(background_img, (0, background_y - HEIGHT))

    # Input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.x += paddle_speed

    # Ball Movement
    for i in range(len(ball_list) - 1, -1, -1):
        ball = ball_list[i]
        speed = ball_speed_list[i]
        ball.x += speed[0]
        ball.y += speed[1]

        if ball.left <= 0 or ball.right >= WIDTH:
            speed[0] *= -1
        if ball.top <= 0:
            speed[1] *= -1
        if ball.bottom >= HEIGHT:
            ball_list.pop(i)
            ball_speed_list.pop(i)

    if not ball_list:
        gameover_sound.play()
        update_high_score()
        print(f"Game Over! High Score: {high_score}")
        pygame.time.delay(1500)
        running = False

    # Paddle collision
    for i in range(len(ball_list)):
        ball = ball_list[i]
        if ball.colliderect(paddle):
            hit_sound.play()
            ball_speed_list[i][1] *= -1
            offset = (ball.centerx - paddle.centerx) / (paddle.width / 2)
            ball_speed_list[i][0] = (BALL_SPEED + level) * offset

    # Brick collision
    for ball in ball_list:
        for brick, color in bricks[:]:
            if ball.colliderect(brick):
                hit_sound.play()
                ball_speed_list[ball_list.index(ball)][1] *= -1
                bricks.remove((brick, color))
                score += 10

                if not gift_active and score >= next_gift_score:
                    gift_rect = gift_img.get_rect(midtop=brick.center)
                    gift_active = True
                    gift_type = random.choice(["multi_ball", "fast_ball", "big_paddle", "bonus_points", "invisible_ball", "reverse_controls", "shrink_paddle"])
                    next_gift_score += 30
                break

    # Power-up logic
    if gift_active:
        gift_rect.y += gift_speed
        WIN.blit(gift_img, gift_rect)
        label = font.render(gift_type.replace("_", " ").title(), True, WHITE)
        WIN.blit(label, (gift_rect.centerx - label.get_width() // 2, gift_rect.y - 20))
        if gift_rect.colliderect(paddle):
            gift_active = False
            gift_effect_time = pygame.time.get_ticks()
            gift_effect_text = ""

            if gift_type == "multi_ball":
                new_ball = ball_list[0].copy()
                new_speed = [-ball_speed_list[0][0], -ball_speed_list[0][1]]
                ball_list.append(new_ball)
                ball_speed_list.append(new_speed)
                gift_effect_text = "Extra ball!"
            elif gift_type == "fast_ball":
                for s in ball_speed_list:
                    s[0] *= 1.5
                    s[1] *= 1.5
                gift_effect_text = "Faster ball!"
            elif gift_type == "big_paddle":
                paddle.width = min(WIDTH, paddle.width + 40)
                gift_effect_text = "Bigger paddle!"
            elif gift_type == "bonus_points":
                score += 50
                gift_effect_text = "+50 points!"
            elif gift_type == "invisible_ball":
                invisible_timer = pygame.time.get_ticks()
                gift_effect_text = "Invisible ball!"
            elif gift_type == "reverse_controls":
                gift_effect_text = "Reverse controls!"
                paddle_speed *= -1
            elif gift_type == "shrink_paddle":
                paddle.width = max(60, paddle.width - 40)
                gift_effect_text = "Shrunk paddle!"
        elif gift_rect.top > HEIGHT:
            gift_active = False

    # Draw Elements
    pygame.draw.rect(WIN, WHITE, paddle)
    for ball in ball_list:
        if gift_type == "invisible_ball" and pygame.time.get_ticks() - invisible_timer < 5000:
            continue
        pygame.draw.ellipse(WIN, WHITE, ball)
    for brick, color in bricks:
        pygame.draw.rect(WIN, color, brick)

    WIN.blit(font.render(f"Score: {score}", True, WHITE), (WIDTH - 150, 10))
    WIN.blit(font.render(f"High Score: {high_score}", True, WHITE), (WIDTH - 150, 40))
    WIN.blit(font.render(f"Level: {level}", True, WHITE), (10, 10))

    if gift_effect_text and pygame.time.get_ticks() - gift_effect_time < 2000:
        effect = effect_font.render(gift_effect_text, True, WHITE)
        WIN.blit(effect, (WIDTH // 2 - effect.get_width() // 2, HEIGHT // 2 - 30))

    pygame.display.update()

    # Next level check
    if not bricks:
        pygame.time.delay(1000)
        next_level()

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
