"""Canvas drawing helpers for the Food Chain Simulator."""

from typing import Dict, List, Tuple

from model import LEVELS, LEVEL_COLORS

BOX_WIDTH = 320
BOX_HEIGHT = 85
LEFT_MARGIN = 30
RIGHT_MARGIN = 300
TOP_MARGIN = 24
VERTICAL_SPACING = 34


def clear_canvas(canvas) -> None:
    """Remove all canvas items."""
    canvas.delete("all")


def draw_chain(canvas, names: Dict[str, str], populations: Dict[str, int]) -> None:
    """Draw the chain boxes, arrows, and population visuals on the canvas."""
    clear_canvas(canvas)

    canvas_width = max(canvas.winfo_width(), 900)
    x1 = LEFT_MARGIN
    x2 = min(x1 + BOX_WIDTH, canvas_width - RIGHT_MARGIN)

    level_order_for_rows = list(reversed(LEVELS))
    positions_by_level: Dict[str, Tuple[int, int, int, int]] = {}

    for index, level in enumerate(level_order_for_rows):
        y1 = TOP_MARGIN + index * (BOX_HEIGHT + VERTICAL_SPACING)
        y2 = y1 + BOX_HEIGHT
        positions_by_level[level] = (x1, y1, x2, y2)
        draw_level_box(canvas, level, names[level], x1, y1, x2, y2)

    draw_energy_arrows(canvas, positions_by_level)
    draw_population_visuals(canvas, populations, positions_by_level)
    draw_population_legend(canvas, populations, canvas_width)


def draw_level_box(canvas, level: str, organism: str, x1: int, y1: int, x2: int, y2: int) -> None:
    """Draw one trophic level rectangle and text labels."""
    color = LEVEL_COLORS[level]

    canvas.create_rectangle(
        x1,
        y1,
        x2,
        y2,
        outline=color,
        width=3,
        fill="#f8f8f8",
    )

    canvas.create_text(
        x1 + 10,
        y1 + 20,
        text=level.title(),
        anchor="w",
        fill="#111111",
        font=("TkDefaultFont", 11, "bold"),
    )
    canvas.create_text(
        x1 + 10,
        y1 + 52,
        text=organism,
        anchor="w",
        fill="#000000",
        font=("TkDefaultFont", 12),
    )


def draw_energy_arrows(canvas, positions_by_level: Dict[str, Tuple[int, int, int, int]]) -> None:
    """Draw centered arrows between levels showing upward energy flow."""
    for index in range(len(LEVELS) - 1):
        lower = LEVELS[index]
        higher = LEVELS[index + 1]

        x1_low, y1_low, x2_low, _ = positions_by_level[lower]
        _, _, _, y2_high = positions_by_level[higher]
        center_x = (x1_low + x2_low) // 2

        canvas.create_line(
            center_x,
            y1_low,
            center_x,
            y2_high,
            arrow="last",
            width=2,
            fill="#333333",
        )
        canvas.create_text(
            center_x,
            (y1_low + y2_high) // 2,
            text="energy flow",
            fill="#333333",
            font=("TkDefaultFont", 9),
        )


def choose_square_unit(max_population: int) -> int:
    """Choose square symbol unit size for compact population drawing."""
    if max_population <= 200:
        return 10
    if max_population <= 1000:
        return 50
    if max_population <= 5000:
        return 100
    return 500


def draw_population_visuals(
    canvas,
    populations: Dict[str, int],
    positions_by_level: Dict[str, Tuple[int, int, int, int]],
) -> None:
    """Draw aligned population symbols without overlapping energy-flow labels."""
    max_population = max(populations.values()) if populations else 0
    square_unit = choose_square_unit(max_population)

    for level in LEVELS:
        _, y1, x2, y2 = positions_by_level[level]
        symbol_x = x2 + 40
        symbol_y = y1 + 12

        draw_population_symbols(
            canvas,
            population=populations[level],
            square_unit=square_unit,
            start_x=symbol_x,
            start_y=symbol_y,
            color=LEVEL_COLORS[level],
        )

        canvas.create_text(
            symbol_x,
            y2 - 10,
            anchor="w",
            text=f"pop: {populations[level]}",
            fill="#222222",
            font=("TkDefaultFont", 9),
        )


def draw_population_symbols(
    canvas,
    population: int,
    square_unit: int,
    start_x: int,
    start_y: int,
    color: str,
) -> None:
    """Draw square symbols for grouped units and dot symbols for single units."""
    squares = population // square_unit
    remainder = population % square_unit

    square_size = 8
    dot_size = 5
    gap = 4
    per_row = 10

    max_symbols = 40
    draw_squares = min(squares, max_symbols)

    for index in range(draw_squares):
        row = index // per_row
        col = index % per_row
        left = start_x + col * (square_size + gap)
        top = start_y + row * (square_size + gap)
        canvas.create_rectangle(
            left,
            top,
            left + square_size,
            top + square_size,
            fill=color,
            outline="",
        )

    if squares > max_symbols:
        canvas.create_text(
            start_x,
            start_y + 52,
            anchor="w",
            text=f"+ {squares - max_symbols} more",
            fill="#444444",
            font=("TkDefaultFont", 8),
        )

    dot_start_y = start_y + 52
    if remainder > 0:
        draw_dots = min(remainder, 20)
        for index in range(draw_dots):
            left = start_x + index * (dot_size + gap)
            canvas.create_oval(
                left,
                dot_start_y,
                left + dot_size,
                dot_start_y + dot_size,
                fill=color,
                outline="",
            )

        if remainder > 20:
            canvas.create_text(
                start_x + 125,
                dot_start_y + 2,
                anchor="w",
                text=f"+{remainder - 20}",
                fill="#444444",
                font=("TkDefaultFont", 8),
            )


def draw_population_legend(canvas, populations: Dict[str, int], canvas_width: int) -> None:
    """Draw color legend and unit legend for population visualization."""
    square_unit = choose_square_unit(max(populations.values()) if populations else 0)
    legend_x = canvas_width - 255
    legend_y = 20

    canvas.create_text(
        legend_x,
        legend_y,
        anchor="w",
        text="Population Legend",
        font=("TkDefaultFont", 10, "bold"),
        fill="#111111",
    )

    for offset, level in enumerate(LEVELS):
        y = legend_y + 18 + offset * 20
        canvas.create_rectangle(
            legend_x,
            y,
            legend_x + 12,
            y + 12,
            fill=LEVEL_COLORS[level],
            outline="",
        )
        canvas.create_text(
            legend_x + 18,
            y + 6,
            anchor="w",
            text=level.title(),
            fill="#111111",
            font=("TkDefaultFont", 9),
        )

    canvas.create_text(
        legend_x,
        legend_y + 108,
        anchor="w",
        text=f"■ = {square_unit} individuals",
        fill="#222222",
        font=("TkDefaultFont", 9, "italic"),
    )
    canvas.create_text(
        legend_x,
        legend_y + 126,
        anchor="w",
        text="• = 1 individual",
        fill="#222222",
        font=("TkDefaultFont", 9, "italic"),
    )

