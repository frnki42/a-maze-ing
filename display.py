from enum import IntEnum

from mazegen.grid import Direction, Grid


RESET = "\033[0m"


class Kind(IntEnum):
    WALL = 0
    FLOOR = 1
    ENTRY = 2
    EXIT = 3
    PATTERN = 4
    PATH = 5


PALETTES: list[dict[Kind, int]] = [
    {
        Kind.WALL: 252,
        Kind.FLOOR: 234,
        Kind.ENTRY: 201,
        Kind.EXIT: 196,
        Kind.PATTERN: 220,
        Kind.PATH: 45,
    },
    {
        Kind.WALL: 172,
        Kind.FLOOR: 233,
        Kind.ENTRY: 201,
        Kind.EXIT: 196,
        Kind.PATTERN: 223,
        Kind.PATH: 228,
    },
    {
        Kind.WALL: 42,
        Kind.FLOOR: 24,
        Kind.ENTRY: 204,
        Kind.EXIT: 224,
        Kind.PATTERN: 242,
        Kind.PATH: 244,
    },
]


def _to_canvas(x: int, y: int) -> tuple[int, int]:
    return x * 2 + 1, y * 2 + 1


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


def paint_path(
    canvas: list[list[Kind]],
    entry: tuple[int, int],
    path: list[Direction],
) -> None:
    cx, cy = _to_canvas(*entry)
    canvas[cy][cx] = Kind.PATH
    for direction in path:
        dx, dy = direction.delta
        canvas[cy + dy][cx + dx] = Kind.PATH
        cx += 2 * dx
        cy += 2 * dy
        canvas[cy][cx] = Kind.PATH


def render(canvas: list[list[Kind]], palette: dict[Kind, int]) -> str:
    parts: list[str] = []
    for row in canvas:
        for kind in row:
            color = palette[kind]
            parts.append(f"\033[48;5;{color}m  ")
        parts.append(RESET + "\n")
    return "".join(parts)
