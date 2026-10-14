from display import CLEAR, PALETTES, Kind, build_canvas, draw, paint_cell
from display import paint_path
from mazegen.grid import Direction, Grid

grid = Grid(3, 2)
grid.carve_wall(0, 0, Direction.E)
grid.carve_wall(1, 0, Direction.E)
grid.carve_wall(2, 0, Direction.S)
grid.carve_wall(2, 1, Direction.W)
grid.carve_wall(1, 1, Direction.W)
canvas = build_canvas(grid)
paint_path(canvas, (0, 0), [Direction.E, Direction.E, Direction.S,
                            Direction.W, Direction.W])
paint_cell(canvas, (0, 0), Kind.ENTRY)
paint_cell(canvas, (0, 1), Kind.EXIT)

print("this line should disappear")
draw(canvas, PALETTES[0])
print(repr(CLEAR))
