import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncing Ball in Rotating Hexagon")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

# Hexagon parameters
hexagon_center = (width // 2, height // 2)
hexagon_radius = 150
num_sides = 6

# Ball parameters
ball_radius = 10
ball_x = width // 2
ball_y = height // 4  # Start a bit above center
ball_vx = 5  # Initial x velocity
ball_vy = 0  # Initial y velocity
gravity = 0.5
friction = 0.98  # Air resistance/friction

# Rotation parameters
rotation_angle = 0
rotation_speed = 0.02  # Radians per frame

# Clock for controlling frame rate
clock = pygame.time.Clock()
fps = 60

def draw_hexagon(center, radius, angle):
    points = []
    for i in range(num_sides):
        angle_rad = math.radians(angle + i * (360 / num_sides))
        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)
        points.append((x, y))
    pygame.draw.polygon(screen, white, points, 2)


def ball_collision(ball_x, ball_y, ball_vx, ball_vy, center, radius, angle):
    for i in range(num_sides):
        angle_rad1 = math.radians(angle + i * (360 / num_sides))
        angle_rad2 = math.radians(angle + (i + 1) * (360 / num_sides))

        x1 = center[0] + radius * math.cos(angle_rad1)
        y1 = center[1] + radius * math.sin(angle_rad1)
        x2 = center[0] + radius * math.cos(angle_rad2)
        y2 = center[1] + radius * math.sin(angle_rad2)
        
        #Simplified collision detection (distance to line segment)
        dx = x2 - x1
        dy = y2 - y1
        t = ((ball_x - x1) * dx + (ball_y - y1) * dy) / (dx*dx + dy*dy)

        if 0 <= t <= 1: #Check if the closest point on the line segment is within the segment
            closest_x = x1 + t * dx
            closest_y = y1 + t * dy
            distance = math.sqrt((ball_x - closest_x)**2 + (ball_y - closest_y)**2)

            if distance <= ball_radius: #Collision!
                # Calculate normal vector
                nx = -(y2 - y1)
                ny = x2 - x1
                norm_length = math.sqrt(nx*nx + ny*ny)
                nx /= norm_length
                ny /= norm_length

                # Calculate dot product (for reflection)
                dot_product = ball_vx * nx + ball_vy * ny

                # Reflect the velocity
                ball_vx -= 2 * dot_product * nx
                ball_vy -= 2 * dot_product * ny

                #Small adjustment to prevent sticking
                ball_x += nx * (ball_radius - distance + 1) #+1 to be sure it's out
                ball_y += ny * (ball_radius - distance + 1)

                # Apply some energy loss (friction)
                ball_vx *= friction
                ball_vy *= friction
                break #Exit the loop after one collision

    return ball_x, ball_y, ball_vx, ball_vy

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update ball position
    ball_x += ball_vx
    ball_y += ball_vy

    # Apply gravity
    ball_vy += gravity

    # Collision detection with hexagon
    ball_x, ball_y, ball_vx, ball_vy = ball_collision(ball_x, ball_y, ball_vx, ball_vy, hexagon_center, hexagon_radius, rotation_angle)

    # Keep ball within screen bounds (optional - for debugging)
    if ball_x + ball_radius > width:
      ball_x = width - ball_radius
      ball_vx *= -friction
    if ball_x - ball_radius < 0:
      ball_x = ball_radius
      ball_vx *= -friction
    if ball_y + ball_radius > height:
      ball_y = height - ball_radius
      ball_vy *= -friction
    if ball_y - ball_radius < 0:
      ball_y = ball_radius
      ball_vy *= -friction


    # Rotate the hexagon
    rotation_angle += rotation_speed

    # Draw everything
    screen.fill(black)
    draw_hexagon(hexagon_center, hexagon_radius, rotation_angle)
    pygame.draw.circle(screen, red, (int(ball_x), int(ball_y)), ball_radius)

    # Update the display
    pygame.display.flip()

    # Control frame rate
    clock.tick(fps)

pygame.quit()