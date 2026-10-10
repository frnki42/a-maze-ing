from enum import IntEnum

from mazegen.grid import Direction, Grid


class Kind(IntEnum):
    WALL = 0
    FLOOR = 1


def build_canvas(grid: Grid) -> list[list[Kind]]:
    canvas_width = grid.width * 2 + 1
    canvas_height = grid.height * 2 + 1
    canvas: list[list[Kind]] = []
    for _ in range(canvas_height):
        row: list[Kind] = []
        for _ in range(canvas_width):
            row.append(Kind.WALL)
        canvas.append(row)
    for y in range(grid.height):
        for x in range(grid.width):
            cx = x * 2 + 1
            cy = y * 2 + 1
            canvas[cy][cx] = Kind.FLOOR
            open_dirs = grid.open_directions(x, y)
            if Direction.E in open_dirs:
                canvas[cy][cx + 1] = Kind.FLOOR
            if Direction.S in open_dirs:
                canvas[cy + 1][cx] = Kind.FLOOR
    return canvas


RESET = "\033[0m"


def render(canvas: list[list[Kind]], palette: dict[Kind, int]) -> str:
    parts: list[str] = []
    for row in canvas:
        for kind in row:
            color = palette[kind]
            parts.append(f"\033[48;5;{color}m  ")
        parts.append(RESET + "\n")
    return "".join(parts)
