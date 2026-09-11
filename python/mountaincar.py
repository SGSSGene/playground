#!/usr/bin/env python3
"""
This is a manual mountain car(t) with physics, exit by pressing ESC
Created 2026 by Daniel Goehring
Comes with a precoded policy, no learning algorithm implemented yet
Todo: Non-deterministic physics, e.g., gaussian, multi agents
"""
import math
import sys
import pygame

# Configuration
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 1024
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
BG_COLOR = (30, 30, 30)# maximum width/height to scale the image to
MAX_ABS_ACCELERATION = 0.6
MOUNTAIN_HEIGHT = 256
HORIZONTAL_SCALE_FACTOR = 2*math.pi/WINDOW_WIDTH
MAX_STEPS_PER_EPISODE = 1000
MAX_EPISODES = 1000
INSANE_SPEED = True
RENDER = False
VERBOSE = False

def mountain_height_and_derivative(x):
    return MOUNTAIN_HEIGHT * math.cos(HORIZONTAL_SCALE_FACTOR*x), -MOUNTAIN_HEIGHT * math.sin(HORIZONTAL_SCALE_FACTOR*x)

def update_state(p, v, action, steps):
    #this calculates the height and ascent on the mountain
    trunc_or_term = 0
    y, d = mountain_height_and_derivative(p)

    # action leads to increased / decreased velocity
    if action == 1:
        v = v + MAX_ABS_ACCELERATION
    if action == -1:
        v = v - MAX_ABS_ACCELERATION

    #velocity update by gravitational force
    v = v - math.sin(math.atan(d))

    #velocity update with viscous friction force
    v = v*0.995

    #position update
    p = p + v/10

    if p > WINDOW_WIDTH:
        reward = 100
        print("SUCCESS, required steps: ", steps, " resetting 01")

        p = math.pi / HORIZONTAL_SCALE_FACTOR  #start at center
        v = 0 #positive reward
        steps = 0
        trunc_or_term = 1


    elif p <= 0:
        reward = -1 #-100
        #print("FELL OF LEFT CLIFF, required steps: ", steps, " resetting 02")
        p = 0#math.pi / HORIZONTAL_SCALE_FACTOR
        v = 0 #negative reward
        #steps = 0
        trunc_or_term = 0#1

    else:
        if steps > MAX_STEPS_PER_EPISODE:
            print("TOO MANY STEPS, ", steps, "  resetting 03")
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
    ##possible policy:
    h, d = mountain_height_and_derivative(p)
    if d > 0:
        if v >= -1:
            action = 1
        else:
            action = -1
    else:
        if v >= -1:
            action = 1
        else:
            action = -1

    ##
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
    p = math.pi / HORIZONTAL_SCALE_FACTOR #start at the valley

    #start velocity
    v = 0

    episodes = 0
    steps = 0
    while running:
        #SWITCH THIS ONE OFF FOR FAST SIMULATION or ON for real physics
        if not INSANE_SPEED:
            clock.tick(100)  # fps
        steps = steps + 1

        if VERBOSE:
            if steps % 100 == 0:
                print ("Episode: ", episodes, " Step: ", steps)

        #for manual intervention
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                v = v - MAX_ABS_ACCELERATION * 10
                print("Pressed Left")
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                v = v + MAX_ABS_ACCELERATION * 10
                print("Pressed Right")
        p, v, steps, trunc_or_term = agent_request(p, v, steps)

        if trunc_or_term !=0:
            episodes += 1
            print("Episode: ", episodes, " FINISHED ")

        if episodes >= MAX_EPISODES:
            running = False

        #draw mountain and car
        if RENDER:
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
