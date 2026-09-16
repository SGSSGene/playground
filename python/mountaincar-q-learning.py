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
MAX_ABS_ACCELERATION = 0.7
MOUNTAIN_HEIGHT = 256
HORIZONTAL_SCALE_FACTOR = 2*math.pi/WINDOW_WIDTH
MAX_STEPS_PER_EPISODE = 1000
MAX_EPISODES = 500
MAX_FPS = True
RENDER = True
RENDER_EVERY_NTH_EPISODE = 10
VERBOSE = True
RANDOM_RESET = True

# Learning Configuration
MIN_POSITION = 0
MAX_POSITION = WINDOW_WIDTH
MIN_VELOCITY = -128
MAX_VELOCITY = 128
NUM_OF_POSITION_BUCKETS = 16
NUM_OF_VELOCITY_BUCKETS = 16

NUM_STATES = NUM_OF_POSITION_BUCKETS * NUM_OF_VELOCITY_BUCKETS
NUM_ACTIONS = 2  # 4 actions

# Learning parameters
ALPHA = 0.8  # Learning rate
GAMMA = 0.99  # Discount factor
EPSILON = 0.0  # Exploration rate
#EPSILON_DECAY = 0.99

q_table = np.zeros((NUM_STATES, NUM_ACTIONS))



def reset_state():
    if RANDOM_RESET:
        rand_p = np.random.rand()
        p = (.5*rand_p + .25) * (MAX_POSITION - MIN_POSITION) + MIN_POSITION
        rand_v = np.random.rand()
        v = (.5*rand_v + .25) * (MAX_VELOCITY - MIN_VELOCITY) + MIN_VELOCITY
    else:
        p = math.pi / HORIZONTAL_SCALE_FACTOR
        v = 0
    return p, v

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
    p = p + v/5 * abs(math.sin(math.atan(d)))

    if p > WINDOW_WIDTH:
        reward = 10000
        if VERBOSE:
            print("SUCCESS, required steps: ", steps, " resetting 01")

        p, v = reset_state()  #start at center
         #positive reward
        steps = 0
        trunc_or_term = 1


    elif p <= 0:
        reward = -10000
        if VERBOSE:
            print("CRASHED LEFT, required steps: ", steps, " resetting 02")

        p, v = reset_state()  # start at center
        # positive reward
        steps = 0
        trunc_or_term = 2

    else:
        reward = -1
        trunc_or_term = 0
        if steps > MAX_STEPS_PER_EPISODE:
            if VERBOSE:
                print("TOO MANY STEPS, ", steps, "  resetting 03")
            p, v = reset_state()
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
    return disc_p + disc_v * NUM_OF_POSITION_BUCKETS


def agent_request(p,v,steps):

    #...
 #   print("100: p ", p, " v ", v, " steps ", steps)

    disc_p, disc_v = discretize_pos_and_vel(p, v)
 #   print("105: disc_p ", disc_p, " disc_v ", disc_v, " steps ", steps)
    state = pos_and_vel_to_state(disc_p, disc_v)

 #   print("110 state ", state)



    if np.random.rand() < EPSILON:
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

#    q_table[0, 0] =       0
#    q_table[1, 0] =       0
#    q_table[2, 0] = -100000
#    q_table[3, 0] = -100000

#    q_table[0, 1] = -100000
#    q_table[1, 1] = -100000
#    q_table[2, 1] =       0
#    q_table[3, 1] =       0


        ##if reward >= 100:
    ##    print("REWARD 100 , state ", state , " action ", action , " pos ", p , " vel ", v , " disc p ", disc_p , " disc v ", disc_v, " state 0 ", q_table[state, 0], " state 1 ", q_table[state, 1])

    return new_p, new_v, steps, trunc_or_term

def main():

    pygame.init()
    if (RENDER):
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Daniel's Mountain Car(t)")

    clock = pygame.time.Clock()

    running = True

    #start position
    p, v = reset_state()

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



                    red_scale = (value_left - min(value_left, value_right)) / ((max(value_left, value_right) - min(value_left, value_right)) + 10000) * 255
                    green_scale = (value_right - min(value_left, value_right)) / ((max(value_left, value_right) - min(value_left, value_right)) + 10000) * 255

                    scale_factor = min(WINDOW_WIDTH, WINDOW_HEIGHT)/max(NUM_OF_POSITION_BUCKETS, NUM_OF_VELOCITY_BUCKETS)

                    pygame.draw.circle(screen, (red_scale, 0, 0 )  , ((x + 0.5) * scale_factor - scale_factor/8, WINDOW_HEIGHT - (y + 0.5) * scale_factor), scale_factor/8)
                    pygame.draw.circle(screen, (0, green_scale, 0 ), ((x + 0.5) * scale_factor + scale_factor/8, WINDOW_HEIGHT - (y + 0.5) * scale_factor), scale_factor/8)


            pygame.display.flip()

        steps = steps + 1
    print(f"Episode {episodes}: Q-Table\n{q_table}")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
