import pygame
import math
import pyaudio
import struct
import numpy as np

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

def generate_beep(frequency=440, duration=0.1):
    """Generate a sine wave beep using numpy"""
    samples = (np.sin(2 * np.pi * np.arange(RATE * duration) * frequency / RATE)).astype(np.float32)
    return (samples * 32767).astype(np.int16).tobytes()

class AudioPlayer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True)
    
    def play(self, data):
        self.stream.write(data)
    
    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Vibe Mode Breakout")

# Game Colors
BG_COLOR = (0, 0, 0)
PADDLE_COLOR = (0, 255, 0)
BALL_COLOR = (255, 0, 0)
BRICK_COLORS = [(255, 255, 0), (0, 255, 255), (255, 0, 255)]

# Game Variables
paddle_width = 100
paddle_height = 20
paddle_x = (800 - paddle_width) // 2
paddle_y = 550
paddle_speed = 0

ball_x = 400
ball_y = 300
ball_radius = 10
ball_dx = 5
ball_dy = -5

bricks = []
brick_width = 75
brick_height = 20
score = 0
lives = 3

# Initialize Audio
audio = AudioPlayer()

# Generate Bricks
for i in range(4):
    for j in range(10):
        bricks.append(pygame.Rect(
            j * (brick_width + 5) + 15,
            i * (brick_height + 5) + 50,
            brick_width,
            brick_height
        ))

def draw_text(text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Game Loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BG_COLOR)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                paddle_speed = -8
            if event.key == pygame.K_RIGHT:
                paddle_speed = 8
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                paddle_speed = 0
    
    # Update paddle position
    paddle_x += paddle_speed
    paddle_x = max(0, min(800 - paddle_width, paddle_x))
    
    # Update ball position
    ball_x += ball_dx
    ball_y += ball_dy
    
    # Ball-wall collisions
    if ball_x - ball_radius < 0 or ball_x + ball_radius > 800:
        ball_dx *= -1
        audio.play(generate_beep(660, 0.05))
    if ball_y - ball_radius < 0:
        ball_dy *= -1
        audio.play(generate_beep(880, 0.05))
    
    # Ball-paddle collision
    paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
    if paddle_rect.colliderect(pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, 
                                        2*ball_radius, 2*ball_radius)):
        ball_dy = -abs(ball_dy)
        offset = (ball_x - paddle_x - paddle_width/2) / (paddle_width/2)
        ball_dx = offset * 8
        audio.play(generate_beep(440, 0.1))
    
    # Ball-brick collisions
    for brick in bricks[:]:
        if brick.colliderect(pygame.Rect(ball_x - ball_radius, ball_y - ball_radius,
                                      2*ball_radius, 2*ball_radius)):
            bricks.remove(brick)
            ball_dy *= -1
            score += 10
            audio.play(generate_beep(1200, 0.05))
    
    # Lose life
    if ball_y + ball_radius > 600:
        lives -= 1
        ball_x = 400
        ball_y = 300
        ball_dx = 5
        ball_dy = -5
        audio.play(generate_beep(220, 0.3))
        if lives <= 0:
            running = False
    
    # Draw elements
    pygame.draw.rect(screen, PADDLE_COLOR, (paddle_x, paddle_y, paddle_width, paddle_height))
    pygame.draw.circle(screen, BALL_COLOR, (int(ball_x), int(ball_y)), ball_radius)
    
    for i, brick in enumerate(bricks):
        color = BRICK_COLORS[(i//10) % len(BRICK_COLORS)]
        pygame.draw.rect(screen, color, brick)
    
    draw_text(f"Score: {score}", 36, 100, 20)
    draw_text(f"Lives: {lives}", 36, 700, 20)
    
    pygame.display.flip()
    clock.tick(60)

# Game Over
screen.fill(BG_COLOR)
draw_text("GAME OVER", 72, 400, 300)
draw_text(f"Final Score: {score}", 48, 400, 400)
pygame.display.flip()
pygame.time.wait(3000)

audio.close()
pygame.quit()
