import pygame
import sys
import numpy as np
import pyaudio

# Initialize Pygame
pygame.init()

# Constants for game
WIDTH, HEIGHT = 600, 400
PADDLE_WIDTH, PADDLE_HEIGHT = 80, 10
BALL_RADIUS = 7
BRICK_WIDTH, BRICK_HEIGHT = 50, 20
PADDLE_SPEED = 5
BALL_SPEED_X, BALL_SPEED_Y = 3, -3
NUM_BRICKS_PER_ROW = WIDTH // BRICK_WIDTH
NUM_ROWS = 5

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Initialize PyAudio for sound
p = pyaudio.PyAudio()
SAMPLE_RATE = 44100
VOLUME = 0.5

def generate_square_wave(frequency, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    square_wave = np.sign(np.sin(2 * np.pi * frequency * t)) * VOLUME
    return square_wave.astype(np.float32)

def play_tone(frequency, duration):
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE, output=True)
    samples = generate_square_wave(frequency, duration)
    stream.write(samples.tobytes())
    stream.stop_stream()
    stream.close()

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout Game")

# Paddle
paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)

# Initial ball
ball = pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_speed = [BALL_SPEED_X, BALL_SPEED_Y]

# Bricks
bricks = []
for row in range(NUM_ROWS):
    for col in range(NUM_BRICKS_PER_ROW):
        brick = pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT + 50, BRICK_WIDTH, BRICK_HEIGHT)
        bricks.append(brick)

# Score
score = 0
font = pygame.font.Font(None, 36)

# Game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            p.terminate()
            pygame.quit()
            sys.exit()

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.x -= PADDLE_SPEED
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.x += PADDLE_SPEED

    # Ball movement
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # Ball collision with walls
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_speed[0] = -ball_speed[0]
    if ball.top <= 0:
        ball_speed[1] = -ball_speed[1]
    if ball.bottom >= HEIGHT:
        # Reset ball and play sound
        play_tone(220, 0.1)
        ball.x = WIDTH // 2 - BALL_RADIUS
        ball.y = HEIGHT // 2 - BALL_RADIUS
        ball_speed = [BALL_SPEED_X, BALL_SPEED_Y]
        score = 0  # Reset score

    # Ball collision with paddle
    if ball.colliderect(paddle):
        ball_speed[1] = -ball_speed[1]
        play_tone(440, 0.1)  # Play sound

    # Ball collision with bricks
    for brick in bricks[:]:
        if ball.colliderect(brick):
            bricks.remove(brick)
            ball_speed[1] = -ball_speed[1]
            score += 10  # Increase score
            play_tone(880, 0.1)  # Play sound
            break

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, paddle)
    pygame.draw.ellipse(screen, RED, ball)
    for brick in bricks:
        pygame.draw.rect(screen, GREEN, brick)

    # Display score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    pygame.time.Clock().tick(60)
 
