from enum import Enum, IntEnum

from mazegen import MazeGenerator
from mazegen.grid import Direction, Grid


RESET = "\033[0m"
CLEAR = "\033[H\033[2J"
PROMPT = "Choice? (1-4): "
MENU = (
    "=== A-Maze-ing ===\n"
    "1. Re-generate a new maze\n"
    "2. Show / Hide the shortest path\n"
    "3. Rotate the wall colours\n"
    "4. Quit\n"
)


class Choice(Enum):
    REGENERATE = "1"
    TOGGLE_PATH = "2"
    ROTATE_COLORS = "3"
    QUIT = "4"


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
        Kind.PATH: 142,
    },
]


def _to_canvas(x: int, y: int) -> tuple[int, int]:
    return x * 2 + 1, y * 2 + 1


def _read_choice() -> Choice | None:
    try:
        choice = input(PROMPT)
    except (EOFError, KeyboardInterrupt):
        print()
        return Choice.QUIT
    try:
        return Choice(choice.strip())
    except ValueError:
        return None


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


def _compose(
    grid: Grid,
    entry: tuple[int, int],
    exit_cell: tuple[int, int],
    pattern: set[tuple[int, int]],
    path: list[Direction],
    show_path: bool,
) -> list[list[Kind]]:
    canvas = build_canvas(grid)
    if show_path:
        paint_path(canvas, entry, path)
    paint_cell(canvas, entry, Kind.ENTRY)
    paint_cell(canvas, exit_cell, Kind.EXIT)
    for cell in pattern:
        paint_cell(canvas, cell, Kind.PATTERN)
    return canvas


def render(canvas: list[list[Kind]], palette: dict[Kind, int]) -> str:
    parts: list[str] = []
    for row in canvas:
        for kind in row:
            color = palette[kind]
            parts.append(f"\033[48;5;{color}m  ")
        parts.append(RESET + "\n")
    return "".join(parts)


def draw(canvas: list[list[Kind]], palette: dict[Kind, int]) -> None:
    print(CLEAR + render(canvas, palette), end="")
    print(MENU, end="")


def run(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_cell: tuple[int, int],
    perfect: bool,
    seed: int | None = None,
) -> None:
    gen = MazeGenerator(width, height, entry, exit_cell, perfect, seed)
    grid = gen.generate()
    path: list[Direction] = []
    show_path = False
    palette_idx = 0
    while True:
        canvas = _compose(
            grid, entry, exit_cell, gen.pattern_cells, path, show_path,
        )
        draw(canvas, PALETTES[palette_idx])
        choice = _read_choice()
        if choice is Choice.QUIT:
            break
        elif choice is Choice.REGENERATE:
            gen = MazeGenerator(width, height, entry, exit_cell, perfect)
            grid = gen.generate()
        elif choice is Choice.TOGGLE_PATH:
            show_path = not show_path
        elif choice is Choice.ROTATE_COLORS:
            palette_idx = (palette_idx + 1) % len(PALETTES)
