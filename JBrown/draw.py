"""Canvas drawing helpers for the Food Chain Simulator."""

from typing import Dict, List, Tuple

from model import LEVELS, LEVEL_COLORS

BOX_WIDTH = 320
BOX_HEIGHT = 85
LEFT_MARGIN = 30
RIGHT_MARGIN = 240
TOP_MARGIN = 30
VERTICAL_SPACING = 35


def clear_canvas(canvas) -> None:
    """Remove all canvas items."""
    canvas.delete("all")


def draw_chain(canvas, names: Dict[str, str], populations: Dict[str, int]) -> None:
    """Draw the chain boxes, arrows, and population visuals on the canvas."""
    clear_canvas(canvas)

    canvas_width = max(canvas.winfo_width(), 650)
    x1 = LEFT_MARGIN
    x2 = min(x1 + BOX_WIDTH, canvas_width - RIGHT_MARGIN)

    box_positions: List[Tuple[int, int, int, int]] = []
    for index, level in enumerate(LEVELS):
        y1 = TOP_MARGIN + index * (BOX_HEIGHT + VERTICAL_SPACING)
        y2 = y1 + BOX_HEIGHT
        box_positions.append((x1, y1, x2, y2))
        draw_level_box(canvas, level, names[level], x1, y1, x2, y2)

    draw_energy_arrows(canvas, box_positions)
    draw_population_visuals(canvas, populations, box_positions)
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


def draw_energy_arrows(canvas, box_positions: List[Tuple[int, int, int, int]]) -> None:
    """Draw arrows between levels with labels showing energy flow direction."""
    for index in range(len(box_positions) - 1):
        _, _, x2_top, y2_top = box_positions[index]
        _, y1_bottom, x2_bottom, _ = box_positions[index + 1]
        mid_x = (x2_top + x2_bottom) // 2

        canvas.create_line(
            mid_x,
            y2_top,
            mid_x,
            y1_bottom,
            arrow="last",
            width=2,
            fill="#333333",
        )
        canvas.create_text(
            mid_x + 65,
            (y2_top + y1_bottom) // 2,
            text="energy flow",
            fill="#333333",
            font=("TkDefaultFont", 9),
        )


def draw_population_visuals(canvas, populations: Dict[str, int], box_positions) -> None:
    """Draw a compact dot-grid population chart aligned with each level box."""
    max_population = max(populations.values()) if populations else 0
    scale = choose_dot_scale(max_population)

    for index, level in enumerate(LEVELS):
        x1, y1, x2, y2 = box_positions[index]
        dots_value = populations[level]
        dot_count = 0 if dots_value == 0 else max(1, dots_value // scale)
        if dots_value > 0 and dots_value % scale != 0:
            dot_count += 1
        dot_count = min(dot_count, 80)

        draw_dot_grid(
            canvas,
            start_x=x2 + 28,
            start_y=y1 + 12,
            dot_count=dot_count,
            color=LEVEL_COLORS[level],
        )

        canvas.create_text(
            x2 + 28,
            y2 - 8,
            anchor="w",
            text=f"pop: {dots_value}",
            fill="#222222",
            font=("TkDefaultFont", 9),
        )


def draw_dot_grid(canvas, start_x: int, start_y: int, dot_count: int, color: str) -> None:
    """Draw small circles in a grid to represent population size."""
    dot_size = 7
    gap = 4
    per_row = 10

    for index in range(dot_count):
        row = index // per_row
        col = index % per_row
        left = start_x + col * (dot_size + gap)
        top = start_y + row * (dot_size + gap)
        canvas.create_oval(
            left,
            top,
            left + dot_size,
            top + dot_size,
            fill=color,
            outline="",
        )


def choose_dot_scale(max_population: int) -> int:
    """Choose a dot scaling value that keeps dot counts manageable."""
    if max_population <= 120:
        return 1
    if max_population <= 500:
        return 5
    if max_population <= 1000:
        return 10
    if max_population <= 5000:
        return 50
    return 100


def draw_population_legend(canvas, populations: Dict[str, int], canvas_width: int) -> None:
    """Draw color and scale legend for population visualization."""
    scale = choose_dot_scale(max(populations.values()) if populations else 0)
    legend_x = canvas_width - 220
    legend_y = 18

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
        text=f"1 dot = {scale} individuals",
        fill="#222222",
        font=("TkDefaultFont", 9, "italic"),
    )
