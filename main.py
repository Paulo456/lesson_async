import time
import asyncio
import curses
from random import randint, choice
from curses_tools import draw_frame

with open('rocket_frame_1.txt') as f:
    rocket_image1 = f.read()

with open('rocket_frame_2.txt') as f:
    rocket_image2 = f.read()


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, choice([curses.A_BOLD, curses.A_DIM, curses.A_NORMAL]))
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, choice([curses.A_BOLD, curses.A_DIM, curses.A_NORMAL]))
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, choice([curses.A_BOLD, curses.A_DIM, curses.A_NORMAL]))
        await asyncio.sleep(0)


async def rocket_fly(canvas, row, column):
    while True:
        draw_frame(canvas, row, column, rocket_image2, negative=True)
        draw_frame(canvas, row, column, rocket_image1)
        await asyncio.sleep(0)

        draw_frame(canvas, row, column, rocket_image1, negative=True)
        draw_frame(canvas, row, column, rocket_image2)
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    max_window_y, max_window_x = canvas.getmaxyx()
    rocket = rocket_fly(canvas, max_window_y - 9, max_window_x/2-2)
    coroutines = [blink(canvas, randint(0, max_window_y - 1), randint(0, max_window_x - 1), choice('+*.:'))
                  for _ in range(150)]
    coroutine_fire = fire(canvas, max_window_y - 1, max_window_x/2)
    do_fire = True
    while True:
        [coroutine.send(None) for coroutine in coroutines]
        rocket.send(None)
        if do_fire:
            try:
                coroutine_fire.send(None)
            except StopIteration:
                do_fire = False

        canvas.refresh()
        time.sleep(0.2)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
