#!/usr/bin/env python3
"""
This example can rotate an image from an image source OR a self created image, as the mandelbrot set.
You need to comment in the image you want yourself.
Requires: pygame (pip install pygame) and some more libraries
"""

import sys
import pygame
from PIL import Image
import numpy as np

# Configuration
WINDOW_SIZE = (1600, 1200)
BG_COLOR = (30, 30, 30)
ROTATION_SPEED = 90  # degrees per second
MAX_IMAGE_SIZE = 800  # maximum width/height to scale the image to


def load_image(path):
    try:
        img = pygame.image.load(path)
    except Exception as e:
        print("Failed to load image")
        raise SystemExit(1)
        # Use convert_alpha() to keep per-pixel alpha and faster blitting
    try:
        img = img.convert_alpha()
    except Exception:
        img = img.convert()
        # Optionally scale large images down to MAX_IMAGE_SIZE while preserving aspect
    w, h = img.get_size()
    max_side = max(w, h)
    if max_side > MAX_IMAGE_SIZE:
        scale = MAX_IMAGE_SIZE / max_side
        new_size = (int(w * scale), int(h * scale))
        # smoothscale looks nicer for photos
        img = pygame.transform.smoothscale(img, new_size)
    return img


def generate_mandelbrot_img():
    # print("Hallo")

    w, h = 1024, 1024  # determines the resolution of the output image

    maxiter = 100  # number of max iterations, higher values lead to more precise and detailed results
    threshold = 2  # to determine if the series does not converge, everything above to reaches infinity

    data = np.zeros((h, w, 3), dtype=np.uint8)
    ##data[0:256, 0:256] = [255, 0, 0]  # red patch in upper left

    for x in range(w):
        for y in range(h):
            c = complex(x/(h/4)-2, y/(h/4)-2)
            z = complex(0, 0)
            # print(c)
            for it in range(maxiter):
                z = z * z + c
                if z.__abs__() > threshold:
                    data[y, x] = [it * 255 / maxiter, 0, 0]
                    # the most iterations which only exceed the threshold in the end lead to the brightest colors, large numbers darker that don't converge, exceed the bound quicker and are painted darker.
                    # print(it)
                    break

    img = Image.fromarray(data, 'RGB')
    #    img.save('mandelbrot.png')
    return img

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


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Rotating Image")
    clock = pygame.time.Clock()

    image_path = sys.argv[1] if len(sys.argv) > 1 else "imgs/truck.png"

   #use an image from an image source or use a self-generated image.
    #image = load_image(image_path)
    image = pil_to_surface(generate_mandelbrot_img())

    angle = 0.0
    running = True
    direction = -1
    i = 0
    while running:
        dt = clock.tick(60) / 1000.0  # seconds elapsed since last frame
        i = i + 1
        if i % 100 == 0:
            print (i)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                direction = -1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                direction = 1


        angle = (angle + direction*ROTATION_SPEED * dt) % 360

        # rotozoom is often better quality than rotate; negative angle for clockwise
        rotated = pygame.transform.rotozoom(image, -angle, np.cos(angle*2*np.pi/360)*0.4+0.5)
        rotated_rect = rotated.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))

        screen.fill(BG_COLOR)
        screen.blit(rotated, rotated_rect.topleft)

        # optional center marker
        pygame.draw.circle(screen, (240, 240, 240), (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2), 3)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
