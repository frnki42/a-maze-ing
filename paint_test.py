from display import Kind, build_canvas, paint_cell, render
from mazegen import MazeGenerator

palette: dict[Kind, int] = {
    Kind.WALL: 250,
    Kind.FLOOR: 0,
    Kind.ENTRY: 201,
    Kind.EXIT: 196,
    Kind.PATTERN: 220,
}

gen = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
canvas = build_canvas(gen.generate())
paint_cell(canvas, (0, 0), Kind.ENTRY)
paint_cell(canvas, (19, 14), Kind.EXIT)
for cell in gen.pattern_cells:
    paint_cell(canvas, cell, Kind.PATTERN)
print(canvas[1][1], canvas[29][39])
print(render(canvas, palette), end="")
