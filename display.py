"""Interactive terminal display of a maze using ANSI background colours.

The maze is first drawn onto a canvas: a grid of ``Kind`` values of size
``(2 * width + 1) x (2 * height + 1)``. Each maze cell sits at an odd
canvas position, and the positions between cells are the walls. Colours
are only chosen when the canvas is rendered, from a palette that maps each
``Kind`` to a 256-colour ANSI code, so switching palettes never needs a
rebuild of the canvas.
"""

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
    """A menu action, identified by the text the user types.

    Attributes:
        REGENERATE: Generate a new maze with a new seed.
        TOGGLE_PATH: Show or hide the shortest path.
        ROTATE_COLORS: Switch to the next palette in ``PALETTES``.
        QUIT: Leave the display loop.
    """

    REGENERATE = "1"
    TOGGLE_PATH = "2"
    ROTATE_COLORS = "3"
    QUIT = "4"


class Kind(IntEnum):
    """What a canvas position shows; a palette maps each kind to a colour.

    Attributes:
        WALL: A closed wall, or a corner between cells.
        FLOOR: An open cell or an open passage between two cells.
        ENTRY: The entry cell.
        EXIT: The exit cell.
        PATTERN: A fully closed cell of the "42" pattern.
        PATH: A cell or passage on the shortest path.
    """

    WALL = 0
    FLOOR = 1
    ENTRY = 2
    EXIT = 3
    PATTERN = 4
    PATH = 5


PALETTES: list[dict[Kind, int]] = [
    {  # Nord
        Kind.WALL: 253,
        Kind.FLOOR: 237,
        Kind.ENTRY: 108,
        Kind.EXIT: 131,
        Kind.PATTERN: 67,
        Kind.PATH: 110,
    },
    {  # Gruvbox Dark
        Kind.WALL: 223,
        Kind.FLOOR: 235,
        Kind.ENTRY: 142,
        Kind.EXIT: 167,
        Kind.PATTERN: 214,
        Kind.PATH: 109,
    },
    {  # Dracula
        Kind.WALL: 141,
        Kind.FLOOR: 236,
        Kind.ENTRY: 84,
        Kind.EXIT: 203,
        Kind.PATTERN: 212,
        Kind.PATH: 117,
    },
    {  # Solarized Dark
        Kind.WALL: 245,
        Kind.FLOOR: 234,
        Kind.ENTRY: 64,
        Kind.EXIT: 160,
        Kind.PATTERN: 136,
        Kind.PATH: 33,
    },
    {  # Catppuccin Mocha
        Kind.WALL: 111,
        Kind.FLOOR: 235,
        Kind.ENTRY: 151,
        Kind.EXIT: 211,
        Kind.PATTERN: 216,
        Kind.PATH: 229,
    },
    {  # Graphite: grey shades with green and white highlights
        Kind.WALL: 240,
        Kind.FLOOR: 233,
        Kind.ENTRY: 255,
        Kind.EXIT: 46,
        Kind.PATTERN: 250,
        Kind.PATH: 35,
    },
]


def _to_canvas(x: int, y: int) -> tuple[int, int]:
    """Convert maze cell coordinates to canvas coordinates.

    Args:
        x: Column of the cell in the maze.
        y: Row of the cell in the maze.

    Returns:
        The ``(x, y)`` position of the cell on the canvas.
    """
    return x * 2 + 1, y * 2 + 1


def _read_choice() -> Choice | None:
    """Ask the user for a menu choice.

    Returns:
        The chosen action, ``Choice.QUIT`` on end of input (Ctrl+D) or
        Ctrl+C, or None if the input is not a valid choice.
    """
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
    """Draw the walls and open passages of a maze onto a new canvas.

    Every position starts as a wall; each cell, and each open wall to its
    east or south neighbour, is then set to floor.

    Args:
        grid: The maze to draw.

    Returns:
        The canvas, a list of rows of size
        ``(2 * grid.width + 1) x (2 * grid.height + 1)``.
    """
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
    """Paint one maze cell on the canvas.

    Args:
        canvas: The canvas to modify in place.
        cell: The maze cell as ``(x, y)``.
        kind: What the cell should show.
    """
    cx, cy = _to_canvas(*cell)
    canvas[cy][cx] = kind


def paint_path(
    canvas: list[list[Kind]],
    entry: tuple[int, int],
    path: list[Direction],
) -> None:
    """Paint a path on the canvas, starting at the entry.

    Each step paints the passage it crosses and the cell it reaches.

    Args:
        canvas: The canvas to modify in place.
        entry: The start cell as ``(x, y)``.
        path: The steps from the entry, one direction per cell.
    """
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
    """Build the complete canvas for one frame.

    The layers are painted in order, so later ones win where they overlap:
    maze, path (if shown), entry, exit, then the "42" pattern.

    Args:
        grid: The maze to draw.
        entry: The entry cell as ``(x, y)``.
        exit_cell: The exit cell as ``(x, y)``.
        pattern: The cells of the "42" pattern.
        path: The shortest path from the entry, one direction per step.
        show_path: Whether to paint the path.

    Returns:
        The finished canvas.
    """
    canvas = build_canvas(grid)
    if show_path:
        paint_path(canvas, entry, path)
    paint_cell(canvas, entry, Kind.ENTRY)
    paint_cell(canvas, exit_cell, Kind.EXIT)
    for cell in pattern:
        paint_cell(canvas, cell, Kind.PATTERN)
    return canvas


def render(canvas: list[list[Kind]], palette: dict[Kind, int]) -> str:
    """Turn a canvas into a coloured string for the terminal.

    Each canvas position becomes two spaces with an ANSI 256-colour
    background, so cells look square in most terminal fonts.

    Args:
        canvas: The canvas to render.
        palette: The colour code to use for each kind.

    Returns:
        The rendered maze, one line per canvas row, each ending with a
        colour reset and a newline.
    """
    parts: list[str] = []
    for row in canvas:
        for kind in row:
            color = palette[kind]
            parts.append(f"\033[48;5;{color}m  ")
        parts.append(RESET + "\n")
    return "".join(parts)


def draw(canvas: list[list[Kind]], palette: dict[Kind, int]) -> None:
    """Clear the terminal and print the maze followed by the menu.

    Args:
        canvas: The canvas to show.
        palette: The colour code to use for each kind.
    """
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
    """Generate a maze and show it until the user quits.

    Each loop draws the maze and the menu, reads one choice and applies
    it. Invalid input simply redraws the screen.

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell as ``(x, y)``.
        exit_cell: Exit cell as ``(x, y)``.
        perfect: Whether to generate a perfect maze.
        seed: Seed for the first maze; None picks a random one. Mazes made
            with "Re-generate" always get a new random seed.

    Raises:
        ValueError: If ``MazeGenerator`` rejects the parameters.
    """
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
