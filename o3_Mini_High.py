import math
import sys
import pygame
from pygame.math import Vector2

# -------------------- Configuration --------------------

# Window dimensions and frame rate
WIDTH, HEIGHT = 800, 600
FPS = 60

# Ball properties
BALL_RADIUS = 12
BALL_COLOR = (220, 50, 50)  # red
# Initial position and velocity of the ball
ball_pos = Vector2(WIDTH / 2, HEIGHT / 2)
ball_vel = Vector2(4, -7)

# Gravity (pixels per frame^2)
GRAVITY = Vector2(0, 0.5)
# Air friction (damping) applied each frame (optional)
AIR_FRICTION = 0.999

# Collision parameters (when the ball hits a wall)
RESTITUTION = 0.9       # bounciness (1.0 is perfectly elastic)
FRICTION_COEFF = 0.1    # friction at the wall contact (0 = no friction, 1 = complete stop tangentially)

# Hexagon properties
HEX_CENTER = Vector2(WIDTH / 2, HEIGHT / 2)
HEX_RADIUS = 250        # distance from center to vertex
hex_rotation = 0.0      # initial rotation angle (in radians)
# Angular velocity in radians per frame (a positive value here gives a counterclockwise spin)
HEX_ANG_VEL = 0.02

# Maximum iterations to “unstick” the ball if it’s interpenetrating a wall
COLLISION_ITERATIONS = 5

# -------------------- Helper Functions --------------------

def get_hexagon_vertices(center, radius, rotation):
    """
    Returns a list of six Vector2 points that are the vertices of a regular hexagon,
    rotated by the given angle.
    """
    vertices = []
    for i in range(6):
        angle = rotation + i * (2 * math.pi / 6)
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        vertices.append(Vector2(x, y))
    return vertices

def check_collision(ball_pos, ball_vel, ball_radius, A, B, hex_center, hex_ang_vel):
    """
    Checks and (if needed) resolves the collision of a circle (the ball) with a line segment
    defined by endpoints A and B. (hex_center is used to help determine the inward normal
    for the hexagon; hex_ang_vel is used to compute the wall’s linear velocity.)
    
    Returns a tuple: (collision_occurred, new_ball_pos, new_ball_vel)
    """
    # Compute the projection of the ball center onto the edge AB.
    AB = B - A
    # Compute the projection parameter t (before clamping)
    t = (ball_pos - A).dot(AB) / AB.dot(AB)
    # Clamp t to the [0,1] segment
    t_clamped = max(0, min(1, t))
    closest_point = A + AB * t_clamped
    displacement = ball_pos - closest_point
    dist = displacement.length()

    if dist < ball_radius:
        # Amount by which the ball is penetrating the wall:
        penetration = ball_radius - dist

        # --- Determine a good collision normal ---
        # If the contact point lies well within the segment (not near a vertex),
        # we use the wall’s inward normal (pointing from the edge toward the center of the hexagon).
        if 0.01 < t_clamped < 0.99:
            # Midpoint of the edge:
            midpoint = (A + B) / 2
            # Inward normal: from the edge’s midpoint toward the hexagon center.
            wall_normal = (hex_center - midpoint).normalize()
        else:
            # If the contact is near a vertex, use the vector from that vertex to the ball.
            # Choose the closer endpoint.
            if (ball_pos - A).length() < (ball_pos - B).length():
                wall_normal = (ball_pos - A).normalize() if (ball_pos - A).length() > 0 else Vector2(1, 0)
            else:
                wall_normal = (ball_pos - B).normalize() if (ball_pos - B).length() > 0 else Vector2(1, 0)

        # (Optional safeguard: if the displacement vector is almost zero, default to the computed wall normal.)
        if displacement.length() < 1e-6:
            displacement = wall_normal

        # Move the ball out of penetration
        new_ball_pos = ball_pos + wall_normal * penetration

        # --- Compute the collision response ---
        # The wall (edge) is moving because the hexagon is rotating.
        # The linear velocity of any point on the hexagon is given by: v = ω × r,
        # where r is the vector from the center to that point.
        r = closest_point - hex_center
        # In 2D, the “cross product” with a scalar ω gives a perpendicular vector:
        wall_vel = hex_ang_vel * Vector2(-r.y, r.x)

        # Compute the relative velocity between the ball and the moving wall.
        rel_vel = ball_vel - wall_vel

        # Decompose rel_vel into a component normal to the wall and a tangential component.
        rel_vel_normal = rel_vel.dot(wall_normal) * wall_normal
        rel_vel_tangent = rel_vel - rel_vel_normal

        # Reflect the normal component (with a coefficient of restitution) and apply friction
        new_rel_normal = -RESTITUTION * rel_vel_normal
        new_rel_tangent = (1 - FRICTION_COEFF) * rel_vel_tangent
        new_rel_vel = new_rel_normal + new_rel_tangent

        # The new ball velocity is the sum of the wall’s velocity and the corrected relative velocity.
        new_ball_vel = wall_vel + new_rel_vel

        return True, new_ball_pos, new_ball_vel
    else:
        # No collision detected with this edge.
        return False, ball_pos, ball_vel

# -------------------- Main Loop --------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Ball in a Spinning Hexagon")
    clock = pygame.time.Clock()

    global ball_pos, ball_vel, hex_rotation

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Update the Simulation ---

        # Update the hexagon’s rotation.
        hex_rotation += HEX_ANG_VEL
        vertices = get_hexagon_vertices(HEX_CENTER, HEX_RADIUS, hex_rotation)

        # Update the ball’s velocity and position.
        ball_vel += GRAVITY
        ball_vel *= AIR_FRICTION
        ball_pos += ball_vel

        # --- Collision Detection & Response ---
        # Check for penetration against each hexagon edge.
        # We use several iterations to “unstick” the ball if it overlaps more than one wall.
        for _ in range(COLLISION_ITERATIONS):
            collision_happened = False
            for i in range(len(vertices)):
                A = vertices[i]
                B = vertices[(i + 1) % len(vertices)]
                collided, new_pos, new_vel = check_collision(ball_pos, ball_vel, BALL_RADIUS,
                                                               A, B, HEX_CENTER, HEX_ANG_VEL)
                if collided:
                    ball_pos = new_pos
                    ball_vel = new_vel
                    collision_happened = True
                    # Break out of this inner loop so that we re‐check all walls after resolution.
                    break
            if not collision_happened:
                break

        # --- Drawing ---
        screen.fill((30, 30, 30))  # dark gray background

        # Draw the rotating hexagon.
        # Convert the list of Vector2 vertices to a list of (x,y) tuples.
        hex_points = [(int(v.x), int(v.y)) for v in vertices]
        pygame.draw.polygon(screen, (50, 200, 50), hex_points, 4)  # green outline, 4 pixels thick

        # Draw the ball.
        pygame.draw.circle(screen, BALL_COLOR, (int(ball_pos.x), int(ball_pos.y)), BALL_RADIUS)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
