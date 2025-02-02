import pygame
import math
import sys

# Initialize Pygame
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncing Ball in Spinning Hexagon")
clock = pygame.time.Clock()

# Constants
center = (width//2, height//2)
hex_size = 200
ball_radius = 10
gravity = 0.8
friction = 0.98
restitution = 0.8
angular_speed = 0.5

# Colors
hex_color = (0, 255, 0)
ball_color = (255, 0, 0)
bg_color = (0, 0, 0)

# Initialize ball
ball = {
    'x': center[0],
    'y': center[1] - 150,
    'vx': 0,
    'vy': 0
}

# Original hexagon vertices
original_vertices = []
for i in range(6):
    angle = math.radians(60 * i)
    x = hex_size * math.cos(angle)
    y = hex_size * math.sin(angle)
    original_vertices.append((x, y))

def rotate_point(point, angle):
    theta = math.radians(angle)
    x, y = point
    x_rot = x * math.cos(theta) - y * math.sin(theta)
    y_rot = x * math.sin(theta) + y * math.cos(theta)
    return (x_rot, y_rot)

# Main loop
angle = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update hexagon rotation
    angle += angular_speed
    angle %= 360

    # Apply physics
    ball['vy'] += gravity
    ball['vx'] *= friction
    ball['vy'] *= friction
    ball['x'] += ball['vx']
    ball['y'] += ball['vy']

    # Generate rotated hexagon vertices
    current_vertices = [rotate_point(v, angle) for v in original_vertices]
    hex_points = [(center[0] + x, center[1] + y) for (x, y) in current_vertices]

    # Collision detection
    for i in range(6):
        a = hex_points[i]
        b = hex_points[(i+1)%6]
        
        ax, ay = a
        bx, by = b
        dx = bx - ax
        dy = by - ay
        
        if dx == 0 and dy == 0:
            continue
        
        # Ball position
        cx = ball['x']
        cy = ball['y']
        
        # Closest point on edge
        apx = cx - ax
        apy = cy - ay
        dot = apx * dx + apy * dy
        len_sq = dx*dx + dy*dy
        
        closest_x = ax
        closest_y = ay
        if dot > 0:
            t = min(dot / len_sq, 1)
            closest_x = ax + dx * t
            closest_y = ay + dy * t
        
        dist_x = cx - closest_x
        dist_y = cy - closest_y
        distance = math.hypot(dist_x, dist_y)
        
        if distance < ball_radius:
            # Collision response
            normal_x = -dy / math.sqrt(len_sq)
            normal_y = dx / math.sqrt(len_sq)
            
            # Reflect velocity with energy loss
            dot_product = ball['vx'] * normal_x + ball['vy'] * normal_y
            ball['vx'] -= 2 * dot_product * normal_x * restitution
            ball['vy'] -= 2 * dot_product * normal_y * restitution
            
            # Resolve collision penetration
            penetration = ball_radius - distance
            ball['x'] += normal_x * penetration
            ball['y'] += normal_y * penetration

    # Draw everything
    screen.fill(bg_color)
    pygame.draw.polygon(screen, hex_color, hex_points, 2)
    pygame.draw.circle(screen, ball_color, (int(ball['x']), int(ball['y'])), ball_radius)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()