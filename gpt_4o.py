import pygame
import pymunk
import pymunk.pygame_util
import math

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Initialize Pymunk space
space = pymunk.Space()
space.gravity = (0, 980)  # Gravity in downward direction

# Create the hexagon
hexagon_radius = 200
hexagon_center = (WIDTH // 2, HEIGHT // 2)
rotation_speed = 0.05  # Radians per update

# Create hexagon walls
# Create hexagon walls
def create_hexagon():
    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    body.position = hexagon_center
    space.add(body)  # Add the body to the space first
    
    shape_list = []
    
    for i in range(6):
        angle1 = math.radians(60 * i)
        angle2 = math.radians(60 * (i + 1))
        p1 = (math.cos(angle1) * hexagon_radius, math.sin(angle1) * hexagon_radius)
        p2 = (math.cos(angle2) * hexagon_radius, math.sin(angle2) * hexagon_radius)
        shape = pymunk.Segment(body, p1, p2, 5)
        shape.elasticity = 0.9  # Bounciness
        shape.friction = 0.5
        space.add(shape)  # Now add the shape after the body is added
        shape_list.append(shape)
    
    return body, shape_list

hexagon_body, hexagon_shapes = create_hexagon()

# Create the ball
def create_ball():
    body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 20))
    body.position = (WIDTH // 2, HEIGHT // 4)
    shape = pymunk.Circle(body, 20)
    shape.elasticity = 0.8  # Bounciness
    shape.friction = 0.4
    space.add(body, shape)
    return body

ball_body = create_ball()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Rotate hexagon
    hexagon_body.angle += rotation_speed
    
    # Redraw
    screen.fill((0, 0, 0))
    space.debug_draw(draw_options)
    
    # Step physics
    space.step(1 / 60.0)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
