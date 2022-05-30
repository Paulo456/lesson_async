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


def get_start_rocket_coordinates(window_max_yx, rocket_size_yx):
    window_max_y, window_max_x = window_max_yx
    rocket_size_y, rocket_size_x = rocket_size_yx
    return [window_max_y - rocket_size_y, window_max_x // 2 - rocket_size_x // 2]


def draw_negative_rocket(canvas, rocket_coordinates):
    [draw_frame(canvas, *rocket_coordinates, rocket_image, negative=True)
     for rocket_image in rocket_images]


def calculate_shift_coordinate(rocket_coordinate, shift, window_max_coordinate, rocket_size_coordinate):
    rocket_coordinate += shift
    rocket_coordinate = median([0, rocket_coordinate, window_max_coordinate - rocket_size_coordinate])
    return rocket_coordinate


def calculate_rocket_position(rocket_coordinates, rocket_size, window_max_yx, rocket_shifting):
    shift_on_y, shift_on_x = rocket_shifting
    rocket_size_y, rocket_size_x = rocket_size
    window_max_y, window_max_x = window_max_yx
    rocket_coordinate_y, rocket_coordinate_x = rocket_coordinates
    rocket_coordinate_y = calculate_shift_coordinate(rocket_coordinate_y, shift_on_y, window_max_y, rocket_size_y)
    rocket_coordinate_x = calculate_shift_coordinate(rocket_coordinate_x, shift_on_x, window_max_x, rocket_size_x)
    return [rocket_coordinate_y, rocket_coordinate_x]


async def draw_rocket_flying(canvas, rocket_coordinates, rocket_size, window_max_yx, rocket_shifting=(0, 0)):
    draw_negative_rocket(canvas, rocket_coordinates)
    rocket_coordinates[:] = calculate_rocket_position(rocket_coordinates, rocket_size, window_max_yx, rocket_shifting)
    images = cycle(rocket_images)

    while True:
        draw_negative_rocket(canvas, rocket_coordinates)
        draw_frame(canvas, *rocket_coordinates, next(images))
        await asyncio.sleep(0)
        # skip one beat
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    # The getmaxy function actually returns the width and height. The coordinates are one value less.
    # The coordinates are stored in the following order: rows - 0, columns - 1
    window_max_yx = [screen_size - 1 for screen_size in canvas.getmaxyx()]
    rocket_size_yx = get_frame_size(rocket_images[0])
    rocket_coordinates = get_start_rocket_coordinates(window_max_yx, rocket_size_yx)

    rocket = draw_rocket_flying(canvas, rocket_coordinates, rocket_size_yx, window_max_yx)
    window_max_y, window_max_x = window_max_yx
    coroutine_fire = fire(canvas, window_max_y, window_max_x / 2)
    coroutines = [blink(canvas, randint(0, window_max_y), randint(0, window_max_x), choice('+*.:'))
                  for _ in range(150)]

    coroutines.append(coroutine_fire)
    coroutines.append(rocket)
    while True:
        pressed_key_code = read_controls(canvas)
        if pressed_key_code != (0, 0, False):
            shift_on_y, shift_on_x, space_pressed = pressed_key_code
            rocket_shifting = shift_on_y, shift_on_x
            coroutines.pop()
            rocket = draw_rocket_flying(canvas, rocket_coordinates, rocket_size_yx, window_max_yx, rocket_shifting)
            coroutines.append(rocket)

        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if not coroutines:
            break
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    rocket_images = get_rocket_images()
    curses.update_lines_cols()
    curses.wrapper(draw)
