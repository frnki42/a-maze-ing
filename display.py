from enum import IntEnum

from mazegen.grid import Direction, Grid


RESET = "\033[0m"


class Kind(IntEnum):
    WALL = 0
    FLOOR = 1
    ENTRY = 2
    EXIT = 3
    PATTERN = 4


def _to_canvas(x: int, y: int) -> tuple[int, int]:
    return x * 2 + 1, y * 2 + 1


def build_canvas(grid: Grid) -> list[list[Kind]]:
    canvas_width, canvas_height = _to_canvas(grid.width, grid.height)
    canvas: list[list[Kind]] = []
    for _ in range(canvas_height):
        row: list[Kind] = []
        for _ in range(canvas_width):
            row.append(Kind.WALL)
        canvas.append(row)
    for y in range(grid.height):
        for x in range(grid.width):
            cx, cy = _to_canvas(x, y)
            canvas[cy][cx] = Kind.FLOOR
            open_dirs = grid.open_directions(x, y)
            if Direction.E in open_dirs:
                canvas[cy][cx + 1] = Kind.FLOOR
            if Direction.S in open_dirs:
                canvas[cy + 1][cx] = Kind.FLOOR
    return canvas


def paint_cell(
    canvas: list[list[Kind]],
    cell: tuple[int, int],
    kind: Kind,
) -> None:
    cx, cy = _to_canvas(*cell)
    canvas[cy][cx] = kind


def render(canvas: list[list[Kind]], palette: dict[Kind, int]) -> str:
    parts: list[str] = []
    for row in canvas:
        for kind in row:
            color = palette[kind]
            parts.append(f"\033[48;5;{color}m  ")
        parts.append(RESET + "\n")
    return "".join(parts)
