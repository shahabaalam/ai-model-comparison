import math
import sys
import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in a Spinning Hexagon")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BALL_COLOR = (200, 50, 50)
HEX_COLOR = (50, 150, 200)

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# ---------------------------
# Simulation parameters
# ---------------------------
dt = 1 / 60  # seconds per frame
gravity = pygame.Vector2(0, 500)  # pixels per second^2 (downwards)
air_friction = 0.999  # slight damping on the ball's velocity each frame

# Collision parameters
restitution = 0.9      # bounciness (1.0 is perfectly elastic)
wall_friction = 0.98   # friction on the tangential velocity component on collision

# ---------------------------
# Ball parameters
# ---------------------------
ball_radius = 15
ball_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2 - 100)
ball_vel = pygame.Vector2(150, -50)  # initial velocity

# ---------------------------
# Hexagon parameters
# ---------------------------
hex_center = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
hex_radius = 250   # distance from center to a vertex
num_sides = 6

# Precompute the hexagon’s vertices in “local” coordinates (centered at (0,0))
local_hex_vertices = []
for i in range(num_sides):
    angle = 2 * math.pi * i / num_sides
    x = hex_radius * math.cos(angle)
    y = hex_radius * math.sin(angle)
    local_hex_vertices.append(pygame.Vector2(x, y))

# Rotation parameters for the hexagon
hex_angle = 0.0               # current rotation angle (in radians)
hex_angular_velocity = 0.5    # radians per second

def rotate_point(point, angle):
    """Rotate a point (pygame.Vector2) by a given angle (in radians)."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return pygame.Vector2(point.x * cos_a - point.y * sin_a,
                          point.x * sin_a + point.y * cos_a)

def get_rotated_hex_vertices(center, angle):
    """Return the world coordinates of the hexagon vertices rotated by angle."""
    return [center + rotate_point(v, angle) for v in local_hex_vertices]

def closest_point_on_segment(p, a, b):
    """Return the closest point on line segment ab to point p."""
    ab = b - a
    ab_len2 = ab.length_squared()
    if ab_len2 == 0:
        return a
    t = max(0, min(1, (p - a).dot(ab) / ab_len2))
    return a + t * ab

def process_collisions(ball_pos, ball_vel, hex_vertices):
    """
    Check for collisions between the ball and each edge of the hexagon.
    Adjust ball position and velocity if a collision is detected.
    """
    global hex_center, hex_angular_velocity

    for i in range(len(hex_vertices)):
        # Get the endpoints of the current edge.
        p1 = hex_vertices[i]
        p2 = hex_vertices[(i + 1) % len(hex_vertices)]
        
        # Find the closest point on the edge to the ball.
        closest = closest_point_on_segment(ball_pos, p1, p2)
        diff = ball_pos - closest
        dist = diff.length()
        
        # Check for collision (penetration)
        if dist < ball_radius:
            # Compute penetration depth and collision normal.
            # If the ball is exactly at the line, choose a default normal.
            if dist != 0:
                normal = diff.normalize()
            else:
                # Fallback normal (pointing from edge midpoint to ball)
                normal = (ball_pos - (p1 + p2) * 0.5).normalize()
            penetration = ball_radius - dist

            # Compute the wall's velocity at the collision point.
            # For a rotating body, the velocity at a point is given by:
            # v = omega x r, where r = (collision_point - center)
            r = closest - hex_center
            # In 2D, the cross product with angular speed (a scalar) gives:
            wall_velocity = hex_angular_velocity * pygame.Vector2(-r.y, r.x)
            
            # Compute the ball's velocity relative to the moving wall.
            rel_vel = ball_vel - wall_velocity

            # Only reflect if the ball is moving into the wall.
            if rel_vel.dot(normal) < 0:
                # Separate normal and tangential components.
                vn = normal * rel_vel.dot(normal)
                vt = rel_vel - vn

                # Reflect the normal component with restitution.
                vn = -restitution * vn
                # Apply friction to the tangential component.
                vt *= wall_friction

                # The new relative velocity is:
                rel_vel_new = vn + vt
                # Convert back to the absolute frame.
                ball_vel = rel_vel_new + wall_velocity

                # Correct the ball's position so it is not inside the wall.
                ball_pos += normal * penetration
    return ball_pos, ball_vel

# ---------------------------
# Main loop
# ---------------------------
running = True
while running:
    # Handle events.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update hexagon rotation.
    hex_angle += hex_angular_velocity * dt

    # Update ball physics.
    # Apply gravity.
    ball_vel += gravity * dt
    # Apply a little air friction.
    ball_vel *= air_friction
    # Update ball position.
    ball_pos += ball_vel * dt

    # Get the current hexagon vertices (rotated).
    hex_vertices = get_rotated_hex_vertices(hex_center, hex_angle)

    # Process collisions with the hexagon walls.
    ball_pos, ball_vel = process_collisions(ball_pos, ball_vel, hex_vertices)

    # Draw everything.
    screen.fill(BLACK)

    # Draw the hexagon.
    pygame.draw.polygon(screen, HEX_COLOR, [(v.x, v.y) for v in hex_vertices], 4)

    # Draw the ball.
    pygame.draw.circle(screen, BALL_COLOR, (int(ball_pos.x), int(ball_pos.y)), ball_radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
