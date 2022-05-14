import time
import asyncio
import curses
from itertools import cycle
from random import randint, choice
from curses_tools import draw_frame, read_controls, get_frame_size, fire, blink
from statistics import median


def get_rocket_images():
    with open('rocket_frame_1.txt') as f:
        image1 = f.read()

    with open('rocket_frame_2.txt') as f:
        image2 = f.read()

    return image1, image2


async def draw_rocket_flying(canvas, rocket_coordinates, rocket_size, max_window, move_to=(0, 0)):
    draw_frame(canvas, rocket_coordinates[0], rocket_coordinates[1], rocket_image1, negative=True)
    draw_frame(canvas, rocket_coordinates[0], rocket_coordinates[1], rocket_image2, negative=True)
    for i in (0, 1):
        rocket_coordinates[i] += move_to[i]
        rocket_coordinates[i] = median([0, rocket_coordinates[i], max_window[i] - rocket_size[i]])
    images = cycle((rocket_image1, rocket_image2))
    while True:
        draw_frame(canvas, rocket_coordinates[0], rocket_coordinates[1], next(images), negative=True)
        draw_frame(canvas, rocket_coordinates[0], rocket_coordinates[1], next(images))
        next(images)
        await asyncio.sleep(0)
        # skip one beat
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    # The getmaxy function actually returns the width and height. The coordinates are one value less.
    # The coordinates are stored in the following order: rows - 0, columns - 1
    max_window = [i - 1 for i in canvas.getmaxyx()]
    rocket_size = get_frame_size(rocket_image1)
    rocket_coordinates = [max_window[0] - rocket_size[0], max_window[1] // 2 - rocket_size[1] // 2]

    rocket = draw_rocket_flying(canvas, rocket_coordinates, rocket_size, max_window)
    coroutine_fire = fire(canvas, max_window[0], max_window[1] / 2)
    coroutines = [blink(canvas, randint(0, max_window[0]), randint(0, max_window[1]), choice('+*.:'))
                  for _ in range(150)]

    coroutines.append(coroutine_fire)
    coroutines.append(rocket)
    while True:
        pressed_key_code = read_controls(canvas)
        if pressed_key_code != (0, 0, False):
            row, column, space_pressed = pressed_key_code
            move_to = row, column
            coroutines.pop()
            rocket = draw_rocket_flying(canvas, rocket_coordinates, rocket_size, max_window, move_to)
            coroutines.append(rocket)

        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    rocket_image1, rocket_image2 = get_rocket_images()
    curses.update_lines_cols()
    curses.wrapper(draw)
