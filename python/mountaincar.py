#!/usr/bin/env python3
"""
This is a manual mountain car(t) with physics, exit by pressing ESC
Created 2026 by Daniel Goehring
Todo: Non-deterministic physics, e.g., gaussian, multi agents
"""
import math
import sys
import pygame

# Configuration
WINDOW_SIZE = (1024, 1024)
BG_COLOR = (30, 30, 30)
MAX_IMAGE_SIZE = 1024  # maximum width/height to scale the image to
MOUNTAIN_HEIGHT = 256
HORIZONTAL_SCALE_FACTOR = 0.007
MAX_STEPS_PER_EPISODE = 2000

def mountain_height_and_derivative(x):
    return MOUNTAIN_HEIGHT * math.cos(HORIZONTAL_SCALE_FACTOR*x), -MOUNTAIN_HEIGHT * math.sin(HORIZONTAL_SCALE_FACTOR*x)

def update_state(p, v, action, steps):
    #this calculates the height and ascent on the mountain
    trunc_or_term = 0
    y, d = mountain_height_and_derivative(p)

    # action leads to increased / decreased velocity
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
        print("SUCCESS, resetting 01")

        p = math.pi / HORIZONTAL_SCALE_FACTOR  #start at center
        v = 0 #positive reward
        steps = 0
        trunc_or_term = 1


    elif p <= 0:
        reward = -100
        print("FAIL TOO FAR LEFT, resetting 02")
        p = math.pi / HORIZONTAL_SCALE_FACTOR
        v = 0 #negative reward
        steps = 0
        trunc_or_term = 1

    else:
        if steps > MAX_STEPS_PER_EPISODE:
            print("TOO MANY STEPS, resetting 03")
            p = math.pi / HORIZONTAL_SCALE_FACTOR
            v = 0
            steps = 0
            trunc_or_term = 2
        reward = -1



    # needs to add value
    return p, v, steps, reward, trunc_or_term

def agent_request(p,v,steps):

    action = 0  #the agent does nothing yet, neither does it learn anything
    #-1 left
    # 1 right

    #here comes the state transition model, simple physics
    p, v, steps, reward, trunc_or_term = update_state(p, v, action,steps)

    return p, v, steps, trunc_or_term

def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Daniel's Mountain Car(t)")
    clock = pygame.time.Clock()

    running = True

    #start position
    p = 300

    #start velocity
    v = 0

    episodes = 0
    steps = 0
    while running:
        #SWITCH THIS ONE OFF FOR FAST SIMULATION or ON for real physics
        dt = clock.tick(100) / 1000.0  # seconds elapsed since last frame
        steps = steps + 1
        if steps % 100 == 0:
            print ("Episode: ", episodes, " Step: ", steps)

        #for manual intervention
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                v = v - 8
                print("Pressed Left")
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                v = v + 8
                print("Pressed Right")
        p, v, steps, trunc_or_term = agent_request(p, v, steps)

        if trunc_or_term !=0:
            episodes += 1

        #draw mountain and car
        screen.fill(BG_COLOR)
        #draw at first the mountain
        for x in range(1024):
            height, derivative = mountain_height_and_derivative(x)
            pygame.draw.circle(screen, (240, 240, 0), (x + 10, WINDOW_SIZE[1]/2 - height), 1)

        #now draw the car
        height, derivative = mountain_height_and_derivative(p)
        pygame.draw.circle(screen, (240, 240, 240), (p + 10, WINDOW_SIZE[1]/2 - height-12), 10)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
