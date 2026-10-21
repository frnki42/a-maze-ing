from mazegen.grid import Direction, Grid


def write_maze(
    grid: Grid,
    entry: tuple[int, int],
    goal: tuple[int, int],
    path: list[Direction],
    file_name: str,
) -> None:
    """Writes the maze configuration and solution path to a file.

    This function serializes the maze grid's wall structure into hexadecimal
    characters, appends the entry and goal coordinates, and adds the string
    representation of the solution path. The resulting string is then saved
    to the specified text file.

    Args:
        grid (Grid): The grid object representing the maze layout and walls.
        entry (tuple[int, int]): The (x, y) coordinates for the starting point of the maze.
        goal (tuple[int, int]): The (x, y) coordinates for the end/target point of the maze.
        path (list[Direction]): A sequence of Direction enums representing the solved path
            from the entry to the goal.
        file_name (str): The name or path of the file where the maze data will be saved.
    """
    grid_str_parts: list[str] = []

    for y in range(grid.height):
        row = "".join(
            str(hex(grid.walls(x, y)))[-1] for x in range(grid.width)
        )
        grid_str_parts.append(row)
    grid_str_parts.append("")
    grid_str_parts.append(str(entry))
    grid_str_parts.append(str(goal))
    grid_str_parts.append("".join(direction.name for direction in path))
    with open(file_name, "w") as fd:
        fd.write("\n".join(grid_str_parts))
