#!/usr/bin/env python3
"""
This is a manual mountain car(t)
"""
import math
import sys
import pygame

# Configuration
WINDOW_SIZE = (1024, 1024)
BG_COLOR = (30, 30, 30)
ROTATION_SPEED = 90  # degrees per second
MAX_IMAGE_SIZE = 1024  # maximum width/height to scale the image to
HORIZONTAL_SCALE_FACTOR = 0.007


def mountain_height_and_derivative(x):


    return 256 * math.cos(HORIZONTAL_SCALE_FACTOR*x) + 256, -256 * math.sin(HORIZONTAL_SCALE_FACTOR*x)

def pil_to_surface(pil_image):
    # Ensure mode is RGB or RGBA
    if pil_image.mode not in ("RGB", "RGBA"):
        pil_image = pil_image.convert("RGBA")

    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()  # raw bytes

    # Use fromstring and then convert to display format
    if mode == "RGBA":
        surf = pygame.image.fromstring(data, size, "RGBA")
        return surf.convert_alpha()
    else:  # mode == "RGB"
        surf = pygame.image.fromstring(data, size, "RGB")
        return surf.convert()

def update_state(p, v, action, steps):
    #print("before", p, v)
    y, d = mountain_height_and_derivative(p)

    # action
    if action == 1:
        v = v + 8
    if action == -1:
        v = v - 8

    #velocity update by gravitational force
    v = v - math.sin(math.atan(d))

    #velocity update with viscous friction force
    v = v*0.995

    #position update
    p = p + v/10

    if p > MAX_IMAGE_SIZE:
        reward = 100
        print("initialize new episode 001")

        p = math.pi / HORIZONTAL_SCALE_FACTOR  #start at center
        v = 0 #positive reward
        steps = 0


    elif p <= 0:
        reward = -100
        print("initialize new episode 002")
        p = math.pi / HORIZONTAL_SCALE_FACTOR
        v = 0 #negative reward
        steps = 0

    else:
        reward = -1
    
    # needs to add value
    return p, v, steps, reward

def agent_request(p,v,steps):

    action = 0
    #-1 left
    # 1 right
    p, v, steps, reward = update_state(p, v, action,steps)

    return p, v, steps

def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Mountain Cart")
    clock = pygame.time.Clock()


    running = True

    #start position
    p = 300

    #start velocity
    v = 0

    i = 0
    while running:
        #this is to slow the simulation down
        dt = clock.tick(100) / 1000.0  # seconds elapsed since last frame
        i = i + 1
        if i % 100 == 0:
            print (i)



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                v = v - 8
                print(v)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                v = v + 8

        p, v, i = agent_request(p, v, i)


        screen.fill(BG_COLOR)
#draw mountain and car
        for x in range(1024):
            height, derivative = mountain_height_and_derivative(x)
            pygame.draw.circle(screen, (240, 240, 0), (x + 10, WINDOW_SIZE[1] - height-128), 1)

        height, derivative = mountain_height_and_derivative(p)
        pygame.draw.circle(screen, (240, 240, 240), (p + 10, WINDOW_SIZE[1] - height-140), 10)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()