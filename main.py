import time
import asyncio
import curses
from random import randint, choice
from curses_tools import draw_frame, read_controls, get_frame_size, fire, blink
from statistics import median


def get_rocket_images():
    with open('rocket_frame_1.txt') as f:
        image1 = f.read()

    with open('rocket_frame_2.txt') as f:
        image2 = f.read()

    return image1, image2


async def draw_rocket_flying(canvas, row, column):
    while True:
        draw_frame(canvas, row, column, rocket_image2, negative=True)
        draw_frame(canvas, row, column, rocket_image1)
        await asyncio.sleep(0)

        draw_frame(canvas, row, column, rocket_image1, negative=True)
        draw_frame(canvas, row, column, rocket_image2)
        await asyncio.sleep(0)


async def clear_rocket_from_frame(canvas, row, column):
    while True:
        draw_frame(canvas, row, column, rocket_image1, negative=True)
        draw_frame(canvas, row, column, rocket_image2, negative=True)
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    max_window_y, max_window_x = canvas.getmaxyx()
    rocket_size_y, rocket_size_x = get_frame_size(rocket_image1)
    rocket_x = max_window_x // 2 - rocket_size_x // 2
    rocket_y = max_window_y - rocket_size_y
    rocket = draw_rocket_flying(canvas, rocket_y, rocket_x)
    coroutines = [blink(canvas, randint(0, max_window_y - 1), randint(0, max_window_x - 1), choice('+*.:'))
                  for _ in range(150)]
    coroutine_fire = fire(canvas, max_window_y - 1, max_window_x / 2)
    do_fire = True
    while True:
        [coroutine.send(None) for coroutine in coroutines]
        pressed_key_code = read_controls(canvas)
        if do_fire:
            try:
                coroutine_fire.send(None)
            except StopIteration:
                do_fire = False
        if pressed_key_code != (0, 0, False):
            rows_direction, columns_direction, space_pressed = pressed_key_code
            rocket_wipe = clear_rocket_from_frame(canvas, rocket_y, rocket_x)
            rocket_wipe.send(None)
            rocket_x += columns_direction
            rocket_x = median([0, rocket_x, max_window_x - rocket_size_x])
            rocket_y += rows_direction
            rocket_y = median([0, rocket_y, max_window_y - rocket_size_y])

            rocket = draw_rocket_flying(canvas, rocket_y, rocket_x)
        rocket.send(None)
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    rocket_image1, rocket_image2 = get_rocket_images()
    curses.update_lines_cols()
    curses.wrapper(draw)
