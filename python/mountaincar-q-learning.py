#!/usr/bin/env python3
"""
This is a manual mountain car(t) with physics, exit by pressing ESC
Created 2026 by Daniel Goehring
Comes with a precoded policy, no learning algorithm implemented yet
Todo: Non-deterministic physics, e.g., gaussian, multi agents
"""
import math
import sys
from math import floor

import numpy as np
import pygame

# Configuration
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 1024
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
BG_COLOR = (30, 30, 30)# maximum width/height to scale the image to
MAX_ABS_ACCELERATION = 0.75
MOUNTAIN_HEIGHT = 256
HORIZONTAL_SCALE_FACTOR = 2*math.pi/WINDOW_WIDTH
MAX_STEPS_PER_EPISODE = 1000
MAX_EPISODES = 100
MAX_FPS = True
RENDER = True
RENDER_EVERY_NTH_EPISODE = 10
VERBOSE = True

# Learning Configuration
MIN_POSITION = 0
MAX_POSITION = WINDOW_WIDTH
MIN_VELOCITY = -128
MAX_VELOCITY = 128
NUM_OF_POSITION_BUCKETS = 8
NUM_OF_VELOCITY_BUCKETS = 8

NUM_STATES = NUM_OF_POSITION_BUCKETS * NUM_OF_VELOCITY_BUCKETS  # 36 states for a 6x6 map
NUM_ACTIONS = 2  # 4 actions
q_table = np.zeros((NUM_STATES, NUM_ACTIONS))

# Learning parameters
ALPHA = 0.8  # Learning rate
GAMMA = 0.99  # Discount factor
EPSILON = 0.0  # Exploration rate
#EPSILON_DECAY = 0.99



def mountain_height_and_derivative(x):
    return MOUNTAIN_HEIGHT * math.cos(HORIZONTAL_SCALE_FACTOR*x), -MOUNTAIN_HEIGHT * math.sin(HORIZONTAL_SCALE_FACTOR*x)

def update_state(p, v, action, steps):
    #this calculates the height and ascent on the mountain
    y, d = mountain_height_and_derivative(p)

    # action leads to increased / decreased velocity
    v = v + action * MAX_ABS_ACCELERATION

    #velocity update by gravitational force
    v = v - math.sin(math.atan(d))

    #velocity update with viscous friction force
    v = v*0.995

    #position update
    p = p + v/5

    if p > WINDOW_WIDTH:
        reward = 10000
        if VERBOSE:
            print("SUCCESS, required steps: ", steps, " resetting 01")

        p = math.pi / HORIZONTAL_SCALE_FACTOR  #start at center
        v = 0 #positive reward
        steps = 0
        trunc_or_term = 1


    elif p <= 0:
        reward = -1*steps  #*math.log10(steps+2)
        p = 0
        v = 0
        trunc_or_term = 0

    else:
        reward = -1*steps
        trunc_or_term = 0
        if steps > MAX_STEPS_PER_EPISODE:
            if VERBOSE:
                print("TOO MANY STEPS, ", steps, "  resetting 03")
            p = math.pi / HORIZONTAL_SCALE_FACTOR
            v = 0
            steps = 0
            trunc_or_term = 2

    # needs to add value
    return p, v, steps, reward, trunc_or_term

def discretize_pos_and_vel(p,v):
    #clip to boundaries
    if p < MIN_POSITION:
        p = MIN_POSITION
    if p >= MAX_POSITION-1:
        p = MAX_POSITION-1
    if v < MIN_VELOCITY:
        v = MIN_VELOCITY
    if v >= MAX_VELOCITY-1:
        v = MAX_VELOCITY-1

    disc_p = floor((p-MIN_POSITION) / ((MAX_POSITION - MIN_POSITION) / NUM_OF_POSITION_BUCKETS))
    disc_v = floor((v-MIN_VELOCITY) / ((MAX_VELOCITY - MIN_VELOCITY) / NUM_OF_VELOCITY_BUCKETS))

    return disc_p, disc_v

def pos_and_vel_to_state(disc_p, disc_v):
    return disc_p*NUM_OF_POSITION_BUCKETS+disc_v


def agent_request(p,v,steps):

    #...
    #print("100: p ", p, " v ", v, " steps ", steps)

    disc_p, disc_v = discretize_pos_and_vel(p, v)
    state = pos_and_vel_to_state(disc_p, disc_v)

   # print("Step ", steps, " disc_p ", disc_p, " disc_v ", disc_v, " state ", state, " leftVal ", q_table[state, 0], " rightVal ", q_table[state, 1])

    if np.random.rand() < EPSILON:
    # Explore: random action
      #  print("Should not be here")
        if np.random.rand() < 0.5:
            action = -1
        else:
            action = 1
    else:
        #Finishing the best action (only two actions possible)
        if  q_table[state, 0] > q_table[state, 1]:
            #print("Went left")
            action = -1
        elif q_table[state, 0] < q_table[state, 1]:
            #print("Went right")
            action = 1
        #Both actions have similar value
        else:
            if np.random.rand() < 0.5:
             #   print("Random left")
                action = -1
            else:
              #  print("Random right")
                action = 1
    #Now execute action
    new_p, new_v, steps, reward, trunc_or_term = update_state(p, v, action,steps)
    new_disc_p, new_disc_v = discretize_pos_and_vel(new_p, new_v)

    new_state = pos_and_vel_to_state(new_disc_p, new_disc_v)

    if q_table[new_state, 0] > q_table[new_state, 1]:
        best_future_q = q_table[new_state, 0]
    else:
        best_future_q = q_table[new_state, 1]

    if action == -1:
        q_table[state, 0] += ALPHA * (reward + GAMMA * best_future_q - q_table[state, 0])

    if action == 1:
        q_table[state, 1] += ALPHA * (reward + GAMMA * best_future_q - q_table[state, 1])

    ##if reward >= 100:
    ##    print("REWARD 100 , state ", state , " action ", action , " pos ", p , " vel ", v , " disc p ", disc_p , " disc v ", disc_v, " state 0 ", q_table[state, 0], " state 1 ", q_table[state, 1])

    return new_p, new_v, steps, trunc_or_term

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
        if not MAX_FPS:
            clock.tick(50)  # fps

        #if VERBOSE:
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
            if VERBOSE:
                if episodes % 10 == 0:
                     print(f"Episode {episodes}")

            #print(f"Episode {episodes}: Q-Table\n{q_table}")


        if episodes >= MAX_EPISODES:
            running = False

        #draw mountain and car
        if RENDER and (episodes % RENDER_EVERY_NTH_EPISODE == 0):
            screen.fill(BG_COLOR)
            #draw at first the mountain
            for x in range(1024):
                height, derivative = mountain_height_and_derivative(x)
                pygame.draw.circle(screen, (240, 240, 0), (x + 10, WINDOW_HEIGHT/2 - height), 1)

            #now draw the car
            height, derivative = mountain_height_and_derivative(p)
            pygame.draw.circle(screen, (240, 240, 240), (p + 10, WINDOW_HEIGHT/2 - height-12), 10)

            #draw the q-values
            for x in range(NUM_OF_POSITION_BUCKETS):
                for y in range (NUM_OF_VELOCITY_BUCKETS):
                    value_left = q_table[(pos_and_vel_to_state(x, y)),0]
                    value_right = q_table[(pos_and_vel_to_state(x, y)),1]

                    color_scale = 0.01

                    col_left = 128 + value_left*color_scale
                    col_right = 128 + value_right*color_scale

                    if col_left < 0:
                        col_left = 0
                    if col_right < 0:
                        col_right = 0

                    if col_left > 255:
                        col_left = 255
                    if col_right > 255:
                        col_right = 255

                    pygame.draw.circle(screen, (col_left, col_left, 255-col_left ), ((x + 0.5) * WINDOW_WIDTH / NUM_OF_POSITION_BUCKETS - WINDOW_WIDTH/NUM_OF_POSITION_BUCKETS/16, WINDOW_HEIGHT - (y + 0.5) * WINDOW_HEIGHT / NUM_OF_VELOCITY_BUCKETS), WINDOW_WIDTH/NUM_OF_POSITION_BUCKETS/8)
                    pygame.draw.circle(screen, (col_right, col_right, 255-col_right), ((x + 0.5) * WINDOW_WIDTH / NUM_OF_POSITION_BUCKETS + WINDOW_WIDTH/NUM_OF_POSITION_BUCKETS/16, WINDOW_HEIGHT - (y + 0.5) * WINDOW_HEIGHT / NUM_OF_VELOCITY_BUCKETS), WINDOW_WIDTH/NUM_OF_POSITION_BUCKETS/8)


            pygame.display.flip()

        steps = steps + 1

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
