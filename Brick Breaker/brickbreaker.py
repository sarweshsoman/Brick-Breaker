import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
BRICKS_IN_ROW = 12
BRICK_WIDTH, BRICK_HEIGHT = 60, 20
WIDTH, HEIGHT = BRICKS_IN_ROW * BRICK_WIDTH, 800
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 10  # Increased paddle width
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FONT_SIZE = 36

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")

# Clock to control the frame rate
clock = pygame.time.Clock()

def initialize_game():
    # Game variables
    ball_speed = 7.5  # Reduced by 25%
    ball_angle = random.uniform(math.pi / 4, 3 * math.pi / 4)
    ball_velocity = [ball_speed * math.cos(ball_angle), ball_speed * math.sin(ball_angle)]
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    paddle_speed = 1.5 * ball_speed  # Paddle speed is 1.5 times the ball speed
    paddle_pos = [WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 2 * PADDLE_HEIGHT]
    bricks = []

    # Create bricks to fill the entire width
    for row in range(10):  # Increased number of rows
        for col in range(BRICKS_IN_ROW):
            brick = pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT, BRICK_WIDTH, BRICK_HEIGHT)
            bricks.append(brick)

    # Starry background variables
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]
    star_timer = 0
    star_change_interval = 500  # Change the position of stars every 500 milliseconds

    return ball_velocity, ball_pos, paddle_speed, paddle_pos, bricks, stars, star_timer, star_change_interval

def collide_rect_circle(rect, circle):
    """
    Check for collision between a rectangle and a circle.
    """
    closest_x = max(rect.left, min(circle[0], rect.right))
    closest_y = max(rect.top, min(circle[1], rect.bottom))
    
    distance = math.sqrt((closest_x - circle[0])**2 + (closest_y - circle[1])**2)
    
    return distance < BALL_RADIUS

def reflect_vector(vector, normal):
    """
    Reflect a vector based on a normal vector.
    """
    dot = 2 * (vector[0] * normal[0] + vector[1] * normal[1])
    reflection = [vector[0] - dot * normal[0], vector[1] - dot * normal[1]]
    return reflection

def game_loop():
    # Initialize game variables
    ball_velocity, ball_pos, paddle_speed, paddle_pos, bricks, stars, star_timer, star_change_interval = initialize_game()

    # Game over variables
    game_over_font = pygame.font.Font(None, FONT_SIZE)
    game_over_text = game_over_font.render("Game Over", True, WHITE)
    blur_surface = pygame.Surface((WIDTH, HEIGHT))

    # Level complete variables
    level_complete_font = pygame.font.Font(None, FONT_SIZE)
    level_complete_text = level_complete_font.render("Level 0 Complete", True, WHITE)

    # Pause message variables
    pause_font = pygame.font.Font(None, FONT_SIZE)
    pause_text = pause_font.render("Paused", True, WHITE)

    # Pause flag
    paused = False

    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    # Pause the game
                    paused = not paused
                elif event.key == pygame.K_r and paused:
                    # Resume the game
                    paused = False
                elif event.key == pygame.K_n:
                    # Start a new game
                    return
                elif event.key == pygame.K_1:
                    # Break all red bricks
                    bricks = [brick for brick in bricks if brick.width != BRICK_WIDTH]

        if paused:
            # Display "Paused" message
            screen.blit(pause_text, (WIDTH // 2 - FONT_SIZE // 2, HEIGHT // 2 - FONT_SIZE // 2))
            pygame.display.flip()
            clock.tick(5)  # Reduce the frame rate when paused
            continue  # Skip the rest of the loop if the game is paused

        # Move the paddle with arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle_pos[0] > 0:
            paddle_pos[0] -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle_pos[0] < WIDTH - PADDLE_WIDTH:
            paddle_pos[0] += paddle_speed

        # Move the ball
        ball_pos[0] += ball_velocity[0]
        ball_pos[1] += ball_velocity[1]

        # Check for collisions with walls
        if ball_pos[0] - BALL_RADIUS <= 0 or ball_pos[0] + BALL_RADIUS >= WIDTH:
            ball_velocity[0] = -ball_velocity[0]
        if ball_pos[1] - BALL_RADIUS <= 0:
            ball_velocity[1] = -ball_velocity[1]

        # Check for collision with paddle
        if (
            paddle_pos[0] < ball_pos[0] < paddle_pos[0] + PADDLE_WIDTH
            and paddle_pos[1] < ball_pos[1] < paddle_pos[1] + PADDLE_HEIGHT
        ):
            # Reflect the ball's direction based on paddle collision
            normal = [0, -1]
            ball_velocity = reflect_vector(ball_velocity, normal)

        # Check for collisions with bricks
        for brick in bricks[:]:
            if collide_rect_circle(brick, ball_pos):
                # Reflect the ball's direction based on brick collision
                normal = [0, 0]
                if brick.left <= ball_pos[0] <= brick.right:
                    normal[1] = 1  # Hit from top or bottom
                else:
                    normal[0] = 1  # Hit from left or right

                ball_velocity = reflect_vector(ball_velocity, normal)
                bricks.remove(brick)

        # Update star positions periodically
        star_timer += clock.get_rawtime()
        if star_timer >= star_change_interval:
            # Multiply star movement by 3 to make them move three times faster
            stars = [(star[0] + 3 * random.randint(-3, 3), star[1] + 3 * random.randint(-3, 3)) for star in stars]
            star_timer = 0

        # Clear the screen
        screen.fill(BLACK)  # Set the background to black

        # Draw stars
        for star in stars:
            pygame.draw.circle(screen, WHITE, star, 1)

        # Draw the paddle with sky blue lines on both ends
        paddle_rect = pygame.Rect(paddle_pos[0], paddle_pos[1], PADDLE_WIDTH, PADDLE_HEIGHT)
        pygame.draw.rect(screen, WHITE, paddle_rect)

        # Draw dark sky blue lines on both ends of the paddle
        pygame.draw.line(screen, (0, 80, 200), (paddle_pos[0], paddle_pos[1]), (paddle_pos[0] + PADDLE_WIDTH, paddle_pos[1]), 3)
        pygame.draw.line(screen, (0, 80, 200), (paddle_pos[0], paddle_pos[1] + PADDLE_HEIGHT), (paddle_pos[0] + PADDLE_WIDTH, paddle_pos[1] + PADDLE_HEIGHT), 3)

        # Draw the ball in white
        pygame.draw.circle(screen, WHITE, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

        # Draw the bricks with shading
        for brick in bricks:
            pygame.draw.rect(screen, RED, brick)
            pygame.draw.line(screen, (200, 0, 0), (brick.left, brick.bottom), (brick.right, brick.bottom), 3)
            pygame.draw.line(screen, (255, 255, 255), (brick.left, brick.top), (brick.left, brick.bottom), 3)

        # Update the display
        pygame.display.flip()

        # Set the frame rate
        clock.tick(60)

        # Check for game over (ball falls below the paddle)
        if ball_pos[1] + BALL_RADIUS > HEIGHT:
            # Display Game Over screen with blurred effect
            for blur_alpha in range(0, 255, 10):
                blur_surface.set_alpha(blur_alpha)
                screen.blit(blur_surface, (0, 0))
                screen.blit(game_over_text, (WIDTH // 2 - FONT_SIZE * 2, HEIGHT // 2 - FONT_SIZE // 2))
                pygame.display.flip()
                pygame.time.delay(30)

            # Wait for a moment before restarting the game
            pygame.time.wait(2000)

            # Start a new game
            return

        # Check for level complete (no red bricks remaining)
        if not any(brick for brick in bricks if brick.width == BRICK_WIDTH):
            # Display Level 0 Complete screen with blurred effect
            for blur_alpha in range(0, 255, 10):
                blur_surface.set_alpha(blur_alpha)
                screen.blit(blur_surface, (0, 0))
                screen.blit(level_complete_text, (WIDTH // 2 - FONT_SIZE * 3, HEIGHT // 2 - FONT_SIZE // 2))
                pygame.display.flip()
                pygame.time.delay(30)

            # Wait for a moment before restarting the game
            pygame.time.wait(2000)

            # Start a new game
            return

game_running = True
while game_running:
    game_loop()
