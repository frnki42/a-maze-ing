"""Interactive terminal display of a maze using ANSI background colours.

The maze is first drawn onto a canvas: a grid of ``Kind`` values of size
``(2 * width + 1) x (2 * height + 1)``. Each maze cell sits at an odd
canvas position, and the positions between cells are the walls. Colours
are only chosen when the canvas is rendered, from a palette that maps each
``Kind`` to a 256-colour ANSI code, so switching palettes never needs a
rebuild of the canvas.

``run()`` is the entry point: it builds every maze from the config with
``_make_maze()`` (generate, solve, write the output file) and redraws the
screen after each menu choice.
"""

from enum import Enum, IntEnum

from config import Config
from mazegen import MazeGenerator
from mazegen.grid import Direction, Grid
from mazegen.pathfinding import find_shortest_path
from output import write_maze


RESET = "\033[0m"
CLEAR = "\033[H\033[2J"
NO_PATTERN = 'Error: the maze is too small for the "42" pattern (min 9x7).'
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


def draw(
    canvas: list[list[Kind]],
    palette: dict[Kind, int],
    status: str,
) -> None:
    """Clear the terminal and print the maze, a status text and the menu.

    Args:
        canvas: The canvas to show.
        palette: The colour code to use for each kind.
        status: Text printed between the maze and the menu.
    """
    print(CLEAR + render(canvas, palette), end="")
    print(status)
    print(MENU, end="")


def _make_maze(
    config: Config,
    seed: int | None,
) -> tuple[MazeGenerator, list[Direction]]:
    """Generate a maze, find its shortest path and write the output file.

    Args:
        config: The parsed configuration file.
        seed: Seed for the maze; None picks a random one.

    Returns:
        The generator, after ``generate()``, and the shortest path from
        the entry to the exit, one ``Direction`` per step.

    Raises:
        ValueError: If ``MazeGenerator`` rejects the configuration.
        OSError: If the output file cannot be written.
    """
    gen = MazeGenerator(
        config.width,
        config.height,
        config.entry,
        config.goal,
        config.perfect,
        seed,
    )
    grid = gen.generate()
    path = find_shortest_path(grid, config.entry, config.goal)
    write_maze(grid, config.entry, config.goal, path, config.output_file)
    return gen, path


def run(config: Config) -> None:
    """Show mazes made from config until the user quits.

    Each loop draws the maze and the menu, reads one choice and applies
    it. Invalid input simply redraws the screen. The first maze uses
    ``config.seed``; "Re-generate" makes a new one with a random seed.
    Every new maze is also written to ``config.output_file``.

    Args:
        config: The parsed configuration file.

    Raises:
        ValueError: If ``MazeGenerator`` rejects the configuration.
        OSError: If the output file cannot be written.
    """
    gen, path = _make_maze(config, config.seed)
    show_path = False
    palette_idx = 0
    while True:
        canvas = _compose(
            gen.grid,
            config.entry,
            config.goal,
            gen.pattern_cells,
            path,
            show_path,
        )
        status = f"Seed: {gen.seed}"
        if not gen.pattern_cells:
            status += "\n" + NO_PATTERN
        draw(canvas, PALETTES[palette_idx], status)
        choice = _read_choice()
        if choice is Choice.QUIT:
            break
        elif choice is Choice.REGENERATE:
            gen, path = _make_maze(config, None)
        elif choice is Choice.TOGGLE_PATH:
            show_path = not show_path
        elif choice is Choice.ROTATE_COLORS:
            palette_idx = (palette_idx + 1) % len(PALETTES)
