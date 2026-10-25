"""Writer for the maze output file (subject IV.5).

``write_maze()`` turns a ``Grid`` and its shortest path into the text
format described in its docstring, and raises ``OSError`` if the file
cannot be written. It lives here and not in the reusable ``mazegen``
package on purpose: the library hands out the maze structure and never
writes files, and subject VI allows that structure to differ from the
output format.
"""

from mazegen.grid import Direction, Grid


_LETTERS: dict[Direction, str] = {
    Direction.N: "N",
    Direction.E: "E",
    Direction.S: "S",
    Direction.W: "W",
}


def write_maze(
    grid: Grid,
    entry: tuple[int, int],
    goal: tuple[int, int],
    path: list[Direction],
    file_name: str,
) -> None:
    """Writes the maze and its shortest path to a file.

    The file has one row of hexadecimal digits per maze row (one digit per
    cell, a set bit is a closed wall: 1 = N, 2 = E, 4 = S, 8 = W), then an
    empty line, the entry as "x,y", the exit as "x,y" and the path as
    N/E/S/W letters. Every line ends with a newline (subject IV.5).

    Args:
        grid: The maze to write.
        entry: The entry cell as (x,y).
        goal: The exit cell as (x,y).
        path: The steps from entry to goal, one Direction per step.
        file_name: The path of the file to create or overwrite.

    Raises:
        OSError: If the file cannot be written.
    """
    grid_str_parts: list[str] = []

    for y in range(grid.height):
        digits: list[str] = []
        for x in range(grid.width):
            digits.append(format(grid.walls(x, y), "x"))
        grid_str_parts.append("".join(digits))
    grid_str_parts.append("")
    grid_str_parts.append(f"{entry[0]},{entry[1]}")
    grid_str_parts.append(f"{goal[0]},{goal[1]}")
    letters: list[str] = []
    for direction in path:
        letters.append(_LETTERS[direction])
    grid_str_parts.append("".join(letters))
    with open(file_name, "w") as fd:
        fd.write("\n".join(grid_str_parts) + "\n")
