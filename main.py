import time
import asyncio
import curses
from random import randint, choice


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, choice([curses.A_BOLD, curses.A_DIM, curses.A_NORMAL]))
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, choice([curses.A_BOLD, curses.A_DIM, curses.A_NORMAL]))
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, choice([curses.A_BOLD, curses.A_DIM, curses.A_NORMAL]))
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    max_window_y, max_window_x = curses.window.getmaxyx(canvas)
    coroutines = [blink(canvas=canvas, row=randint(0, max_window_y-1), column=randint(0, max_window_x-1), symbol=choice('+*.:'))
                  for _ in range(150)]
    coroutines_copy = coroutines.copy()
    while True:
        try:
            [coroutine.send(None) for coroutine in coroutines_copy]
            canvas.refresh()
            time.sleep(0.5)
        except StopIteration:
            coroutines_copy = coroutines.copy()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)

