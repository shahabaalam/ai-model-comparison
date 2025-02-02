import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CENTER = (WIDTH // 2, HEIGHT // 2)
HEX_RADIUS = 200
BALL_RADIUS = 10
GRAVITY = 600  # pixels per second squared
AIR_FRICTION = 0.02  # per second
RESTITUTION = 0.8
FRICTION = 0.3
ANGULAR_VELOCITY = math.radians(180)  # 180 degrees per second in radians

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in Spinning Hexagon")
clock = pygame.time.Clock()

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 0.0
        self.vy = 0.0

class Hexagon:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        self.rotation_angle = 0.0  # radians

    def get_vertices(self):
        vertices = []
        cx, cy = self.center
        for i in range(6):
            theta = self.rotation_angle + math.radians(60 * i)
            x = cx + self.radius * math.cos(theta)
            y = cy + self.radius * math.sin(theta)
            vertices.append((x, y))
        return vertices

def closest_point_on_segment(A, B, C):
    Ax, Ay = A
    Bx, By = B
    Cx, Cy = C

    ABx = Bx - Ax
    ABy = By - Ay
    ACx = Cx - Ax
    ACy = Cy - Ay

    t = (ACx * ABx + ACy * ABy) / (ABx**2 + ABy**2 + 1e-8)
    t = max(0.0, min(1.0, t))

    Px = Ax + t * ABx
    Py = Ay + t * ABy

    return (Px, Py)

# Initialize ball and hexagon
ball = Ball(CENTER[0], CENTER[1], BALL_RADIUS)
ball.vx = 100.0  # initial velocity
hexagon = Hexagon(CENTER, HEX_RADIUS)

running = True
while running:
    dt = clock.tick(60) / 1000.0  # dt in seconds

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update hexagon rotation
    hexagon.rotation_angle += ANGULAR_VELOCITY * dt

    # Update ball physics (gravity and air friction)
    ball.vy += GRAVITY * dt
    ball.vx *= (1 - AIR_FRICTION * dt)
    ball.vy *= (1 - AIR_FRICTION * dt)

    # Update ball position
    ball.x += ball.vx * dt
    ball.y += ball.vy * dt

    # Check collisions with hexagon walls
    vertices = hexagon.get_vertices()
    for i in range(6):
        A = vertices[i]
        B = vertices[(i + 1) % 6]
        C = (ball.x, ball.y)

        # Find closest point on the segment AB
        P = closest_point_on_segment(A, B, C)
        distance = math.hypot(C[0] - P[0], C[1] - P[1])

        if distance < ball.radius:
            # Compute midpoint of AB
            mid_x = (A[0] + B[0]) / 2
            mid_y = (A[1] + B[1]) / 2
            # Compute normal vector (from center to midpoint)
            normal_x = mid_x - hexagon.center[0]
            normal_y = mid_y - hexagon.center[1]
            # Normalize the normal vector
            norm = math.hypot(normal_x, normal_y)
            if norm == 0:
                continue  # avoid division by zero
            normal_x /= norm
            normal_y /= norm

            # Compute velocity of point P due to rotation
            # P's position relative to center
            rel_px = P[0] - hexagon.center[0]
            rel_py = P[1] - hexagon.center[1]
            # Velocity of P: v = (-omega * rel_py, omega * rel_px)
            omega = ANGULAR_VELOCITY
            v_wall_x = -omega * rel_py
            v_wall_y = omega * rel_px

            # Relative velocity
            rel_vx = ball.vx - v_wall_x
            rel_vy = ball.vy - v_wall_y

            # Dot product of relative velocity and normal
            dot_product = rel_vx * normal_x + rel_vy * normal_y

            if dot_product < 0:  # Moving towards the wall
                # Compute penetration vector
                penetration = ball.radius - distance
                ball.x += normal_x * penetration
                ball.y += normal_y * penetration

                # Compute new relative velocity after collision
                # Restitution affects the normal component
                new_normal_v = -RESTITUTION * dot_product
                # Tangential component is scaled by (1 - FRICTION)
                tangent_vx = rel_vx - dot_product * normal_x
                tangent_vy = rel_vy - dot_product * normal_y
                tangent_vx *= (1 - FRICTION)
                tangent_vy *= (1 - FRICTION)

                # New relative velocity
                new_rel_vx = new_normal_v * normal_x + tangent_vx
                new_rel_vy = new_normal_v * normal_y + tangent_vy

                # New ball velocity
                ball.vx = v_wall_x + new_rel_vx
                ball.vy = v_wall_y + new_rel_vy

    # Draw everything
    screen.fill(BLACK)

    # Draw hexagon
    vertices = hexagon.get_vertices()
    pygame.draw.polygon(screen, WHITE, vertices, 2)

    # Draw ball
    pygame.draw.circle(screen, RED, (int(ball.x), int(ball.y)), ball.radius)

    pygame.display.flip()

pygame.quit()