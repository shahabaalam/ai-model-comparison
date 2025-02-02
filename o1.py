import pygame
import math
import sys

# Window size
WIDTH, HEIGHT = 800, 600

# Simulation parameters
FPS = 60
GRAVITY = 0.2         # Gravity pulling ball downward each frame
AIR_FRICTION = 0.999  # Friction factor applied every frame (1.0 = no friction)
BOUNCE_FRICTION = 0.8 # Coefficient of restitution upon collision with a wall
ROTATION_SPEED = 1.0  # Degrees per frame the hexagon rotates
HEX_RADIUS = 200      # "Radius" of the hexagon (center to vertex)
BALL_RADIUS = 15
INITIAL_BALL_POS = (WIDTH//2, HEIGHT//2 - 100)
INITIAL_BALL_VEL = (2.0, 0.0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Define a function to get hexagon vertices in local (unrotated) coordinates
def get_hexagon_vertices(radius):
    # A regular hexagon has 6 vertices, each 60 degrees apart
    vertices = []
    for i in range(6):
        angle_deg = 60 * i - 30  # shift by -30 deg so a vertex is at the top
        angle_rad = math.radians(angle_deg)
        x = radius * math.cos(angle_rad)
        y = radius * math.sin(angle_rad)
        vertices.append((x, y))
    return vertices

# Rotate a point (x, y) around (cx, cy) by angle degrees
def rotate_point(x, y, cx, cy, angle_degs):
    # Convert angle to radians
    theta = math.radians(angle_degs)
    # Translate point to origin
    dx = x - cx
    dy = y - cy
    # Perform rotation
    rx = dx * math.cos(theta) - dy * math.sin(theta)
    ry = dx * math.sin(theta) + dy * math.cos(theta)
    # Translate back
    return (rx + cx, ry + cy)

# Check collision between ball center and a line segment (p1->p2). 
# If collision, reflect velocity and push ball outward.
def collide_and_reflect(ball_pos, ball_vel, p1, p2):
    # p1, p2: endpoints of the wall segment
    # ball_pos: (x, y), ball_vel: (vx, vy)
    # Return (new_pos, new_vel, collided_boolean)
    x, y = ball_pos
    vx, vy = ball_vel

    # Line segment vector
    line_dx = p2[0] - p1[0]
    line_dy = p2[1] - p1[1]

    # Wall normal (we can pick left normal)
    # For a line dx, dy, a normal can be (dy, -dx) or (-dy, dx)
    # We'll pick one, but it’s consistent for the inside of the shape
    wall_normal = (line_dy, -line_dx)

    # Vector from p1 to ball center
    p1_to_ball = (x - p1[0], y - p1[1])

    # Project p1_to_ball onto the wall_normal to get distance from line
    # Dist = (p1_to_ball . wall_normal) / |wall_normal|
    normal_length = math.hypot(*wall_normal)
    if normal_length == 0:
        return (ball_pos, ball_vel, False)  # Degenerate line

    dot = p1_to_ball[0]*wall_normal[0] + p1_to_ball[1]*wall_normal[1]
    dist = dot / normal_length

    # We consider collision if dist < ball radius and the projection of the
    # ball center along the line's direction is within the segment
    # But since it's inside shape, we specifically want negative side or so
    # We'll check the "inside" direction of the normal by a consistent
    # orientation, but let's keep it simple:

    # Check if the ball center is "close enough" to the line, 
    # and the intersection is within the segment bounds
    # To find the param of the projection on the line direction:
    line_len = math.hypot(line_dx, line_dy)
    if line_len == 0:
        return (ball_pos, ball_vel, False)

    # Dot of p1_to_ball with line direction:
    line_dot = p1_to_ball[0]*line_dx + p1_to_ball[1]*line_dy
    t = line_dot / (line_len**2)
    # Intersection point on the infinite line
    # p_int = p1 + t*(line_dx, line_dy)

    # Check 0 <= t <= 1 => intersection is within segment
    if 0 <= t <= 1:
        # If |dist| < BALL_RADIUS => collision or penetration
        # We'll look at sign of dist. We assume "inside" the hex is
        # in the direction of negative or positive normal. 
        # For a consistent normal for a convex shape like hex, 
        # we can check if dist < 0 is inside or outside. 
        # We want the ball to be on the inside side of each wall.
        # Let's assume the normal is outward if dist>0 => outside. 
        # We'll just check absolute value:
        if abs(dist) < BALL_RADIUS:
            # There's a collision
            overlap = BALL_RADIUS - abs(dist)

            # Normal unit vector
            nx = wall_normal[0]/normal_length
            ny = wall_normal[1]/normal_length

            # The ball center is "over" the line if dot>0 => sign matches dist
            # If dist > 0 => we push it negative, etc. 
            # We'll push the ball along the direction of the normal 
            # so that it no longer overlaps
            if dist > 0:
                # Ball center is outside, push inward
                x_new = x - nx * overlap
                y_new = y - ny * overlap
            else:
                # Ball center is inside, no collision from that side
                # In a typical convex shape, the normal points outward
                # so dist < 0 means it's inside - no reflection needed
                return (ball_pos, ball_vel, False)

            # Reflect velocity around normal
            # v_new = v - 2*(v.n)*n
            # n is the normal unit vector
            v_dot_n = vx*nx + vy*ny
            vx_new = vx - 2 * v_dot_n * nx
            vy_new = vy - 2 * v_dot_n * ny

            # Apply bounce friction (coefficient of restitution)
            vx_new *= BOUNCE_FRICTION
            vy_new *= BOUNCE_FRICTION

            return ((x_new, y_new), (vx_new, vy_new), True)

    return (ball_pos, ball_vel, False)

def main():
    # Hexagon center
    hex_center = (WIDTH//2, HEIGHT//2)

    # Precompute local (unrotated) hex vertices
    hex_local_vertices = get_hexagon_vertices(HEX_RADIUS)

    # Ball state
    ball_x, ball_y = INITIAL_BALL_POS
    ball_vx, ball_vy = INITIAL_BALL_VEL

    rotation_angle = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # delta time in seconds, if desired

        # ========== Event handling ==========
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ========== Update Physics ==========

        # 1) Apply gravity
        ball_vy += GRAVITY

        # 2) Apply air friction
        ball_vx *= AIR_FRICTION
        ball_vy *= AIR_FRICTION

        # 3) Update ball position
        ball_x += ball_vx
        ball_y += ball_vy

        # 4) Rotate hexagon
        rotation_angle += ROTATION_SPEED
        if rotation_angle >= 360:
            rotation_angle -= 360

        # 5) Construct rotated hexagon vertices
        rotated_vertices = []
        for vx, vy in hex_local_vertices:
            rx, ry = rotate_point(vx + hex_center[0],
                                  vy + hex_center[1],
                                  hex_center[0],
                                  hex_center[1],
                                  rotation_angle)
            rotated_vertices.append((rx, ry))

        # 6) Check collision with each hexagon edge
        #    The hex has 6 sides, connect consecutive vertices
        for i in range(len(rotated_vertices)):
            p1 = rotated_vertices[i]
            p2 = rotated_vertices[(i+1) % len(rotated_vertices)]

            (new_pos, new_vel, collided) = collide_and_reflect(
                (ball_x, ball_y), (ball_vx, ball_vy), p1, p2
            )
            ball_x, ball_y = new_pos
            ball_vx, ball_vy = new_vel

            if collided:
                # If you want to apply additional friction on bounce, do so here
                # e.g. ball_vx *= 0.95; ball_vy *= 0.95
                pass

        # ========== Draw ==========
        screen.fill((30, 30, 30))

        # Draw hexagon edges
        COLOR_HEX = (0, 200, 255)
        for i in range(len(rotated_vertices)):
            p1 = rotated_vertices[i]
            p2 = rotated_vertices[(i+1) % len(rotated_vertices)]
            pygame.draw.line(screen, COLOR_HEX, p1, p2, 2)

        # Draw ball
        COLOR_BALL = (255, 50, 50)
        pygame.draw.circle(screen, COLOR_BALL, (int(ball_x), int(ball_y)), BALL_RADIUS)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
