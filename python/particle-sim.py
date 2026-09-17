#!/usr/bin/env python3
"""
This is a particle simulation, exit by pressing ESC
Created 2026 by Daniel Goehring
Comes with a precoded policy, no learning algorithm implemented yet
Todo: Non-deterministic physics, e.g., gaussian, multi agents
"""
import math
import sys
import numpy as np
import pygame

# Configuration
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 1024
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
BG_COLOR = (30, 30, 30)# maximum width/height to scale the image to

MAX_STEPS_PER_EPISODE = 1000
MAX_FPS = True
RENDER = True
VERBOSE = True
NUM_PARTICLES = 50
STATE_DIM = 4

MIN_GRAVITATION_DISTANCE = 10
SPRING_CONSTANT = 0.00005
GRAVITATION_CONSTANT = 5


particle_table = np.zeros((NUM_PARTICLES, STATE_DIM))


def init():
    for i in range(NUM_PARTICLES):
        particle_table[i,0] = np.random.rand()*(WINDOW_SIZE[0]-1)
        particle_table[i,1] = np.random.rand()*(WINDOW_SIZE[1]-1)
        particle_table[i,2] = 0.0
        particle_table[i,3] = 0.0


def dist_angle(x1, y1, x2, y2):
    return math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1)), np.arctan2(y2 - y1, x2 - x1)

def gravitation_vector(d, a):
    min_d = max(MIN_GRAVITATION_DISTANCE, d)
    return GRAVITATION_CONSTANT * math.cos(a) / min_d / min_d, GRAVITATION_CONSTANT * math.sin(a) / min_d / min_d

def spring_force_vector(d, a):
    return SPRING_CONSTANT*d * math.cos(a), SPRING_CONSTANT*d * math.sin(a)


def update_state(steps):
    for i in range(NUM_PARTICLES):
        for j in range(NUM_PARTICLES):
            if i != j:
                d, a = dist_angle(particle_table[i, 0], particle_table[i, 1], particle_table[j, 0], particle_table[j, 1])

                force_x, force_y = gravitation_vector(d, a)
                #force_x, force_y = spring_force_vector(d, a)

                particle_table[i, 2] += force_x
                particle_table[i, 3] += force_y

    for i in range(NUM_PARTICLES):

        particle_table[i, 0] += particle_table[i, 2]
        particle_table[i, 1] += particle_table[i, 3]



def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Daniel's Particle Sim")
    clock = pygame.time.Clock()

    running = True

    episodes = 0
    steps = 0
    init()
    while running:

        update_state(steps)

        #SWITCH THIS ONE OFF FOR FAST SIMULATION or ON for real physics
        if not MAX_FPS:
            clock.tick(50)  # fps
        steps = steps + 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        #draw mountain and car
        if RENDER:
            screen.fill(BG_COLOR)
            for i in range(NUM_PARTICLES):
                pygame.draw.circle(screen, (240, 240, 240), (particle_table[i,0], particle_table[i,1]), 1)

            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()