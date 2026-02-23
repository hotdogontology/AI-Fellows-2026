"""Tkinter UI for the Food Chain Simulator."""

import random
import tkinter as tk
from tkinter import messagebox

import draw
from model import (
    DEFAULT_POPULATIONS,
    EXAMPLE_CHAINS,
    LEVELS,
    POPULATION_MODELS,
    FoodChain,
    apply_population_change,
    build_chain,
    build_explain_text,
    validate_population_value,
)


class FoodChainApp:
    """Main application class for user interaction and drawing updates."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("food chain simulator")
        self.current_chain: FoodChain | None = None

        self.name_entries: dict[str, tk.Entry] = {}
        self.population_entries: dict[str, tk.Entry] = {}

        self._build_layout()
        self._bind_resize_redraw()

    def _build_layout(self) -> None:
        """Create all UI widgets and layout containers."""
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)

        self.left_frame = tk.Frame(self.root, padx=12, pady=12)
        self.left_frame.grid(row=0, column=0, sticky="ns")

        self.right_frame = tk.Frame(self.root, padx=8, pady=8)
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.rowconfigure(0, weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        self._build_form_panel()
        self._build_canvas_panel()

    def _build_form_panel(self) -> None:
        """Create input controls, action buttons, and explanation area."""
        tk.Label(
            self.left_frame,
            text="Build Your Food Chain",
            font=("TkDefaultFont", 12, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        row = 1
        for level in LEVELS:
            tk.Label(self.left_frame, text=level.title() + ":").grid(
                row=row, column=0, sticky="w", padx=(0, 6), pady=4
            )
            name_entry = tk.Entry(self.left_frame, width=22)
            name_entry.grid(row=row, column=1, sticky="ew", pady=4)
            self.name_entries[level] = name_entry
            row += 1

        tk.Label(
            self.left_frame,
            text="Population Sizes",
            font=("TkDefaultFont", 10, "bold"),
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(12, 4))
        row += 1

        for level in LEVELS:
            tk.Label(self.left_frame, text=level.title() + ":").grid(
                row=row, column=0, sticky="w", padx=(0, 6), pady=3
            )
            pop_entry = tk.Entry(self.left_frame, width=12)
            pop_entry.grid(row=row, column=1, sticky="w", pady=3)
            self.population_entries[level] = pop_entry
            row += 1

        tk.Button(self.left_frame, text="Build Chain", command=self.on_build_chain).grid(
            row=row, column=0, sticky="ew", pady=(12, 4)
        )
        tk.Button(self.left_frame, text="Reset", command=self.on_reset).grid(
            row=row, column=1, sticky="ew", pady=(12, 4)
        )
        row += 1

        tk.Button(
            self.left_frame,
            text="Load Example",
            command=self.on_load_example,
        ).grid(row=row, column=0, sticky="ew", pady=4)
        tk.Button(
            self.left_frame,
            text="Default Populations",
            command=self.on_apply_default_populations,
        ).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        tk.Label(
            self.left_frame,
            text="Dynamic Population Update",
            font=("TkDefaultFont", 10, "bold"),
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(12, 4))
        row += 1

        tk.Label(self.left_frame, text="Model:").grid(row=row, column=0, sticky="w", pady=2)
        self.model_var = tk.StringVar(value="Balanced")
        tk.OptionMenu(self.left_frame, self.model_var, *POPULATION_MODELS.keys()).grid(
            row=row, column=1, sticky="ew", pady=2
        )
        row += 1

        tk.Label(self.left_frame, text="Change Level:").grid(
            row=row, column=0, sticky="w", pady=2
        )
        self.change_level_var = tk.StringVar(value="primary consumer")
        tk.OptionMenu(self.left_frame, self.change_level_var, *LEVELS).grid(
            row=row, column=1, sticky="ew", pady=2
        )
        row += 1

        tk.Label(self.left_frame, text="New Value:").grid(row=row, column=0, sticky="w", pady=2)
        self.change_value_entry = tk.Entry(self.left_frame, width=12)
        self.change_value_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        tk.Button(
            self.left_frame,
            text="Apply Change Across Web",
            command=self.on_apply_population_change,
        ).grid(row=row, column=0, columnspan=2, sticky="ew", pady=(4, 8))
        row += 1

        tk.Label(
            self.left_frame,
            text="Explain",
            font=("TkDefaultFont", 10, "bold"),
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(8, 4))
        row += 1

        self.explain_label = tk.Label(
            self.left_frame,
            text="Build a chain to see an explanation.",
            justify="left",
            wraplength=300,
            anchor="w",
            fg="#333333",
        )
        self.explain_label.grid(row=row, column=0, columnspan=2, sticky="ew")

    def _build_canvas_panel(self) -> None:
        """Create the right-side drawing canvas."""
        self.canvas = tk.Canvas(self.right_frame, bg="white", highlightthickness=1)
        self.canvas.grid(row=0, column=0, sticky="nsew")

    def _bind_resize_redraw(self) -> None:
        """Redraw the diagram when the canvas size changes."""
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def on_canvas_resize(self, _event) -> None:
        """Handle canvas resizing by redrawing current chain if available."""
        if self.current_chain is not None:
            draw.draw_chain(
                self.canvas,
                self.current_chain.names,
                self.current_chain.populations,
            )

    def on_build_chain(self) -> None:
        """Validate current form inputs and draw the full chain."""
        raw_names = {level: self.name_entries[level].get() for level in LEVELS}
        raw_populations = {
            level: self.population_entries[level].get() for level in LEVELS
        }

        try:
            chain = build_chain(raw_names, raw_populations)
        except ValueError as error:
            messagebox.showerror("Input problem", str(error))
            return

        self.current_chain = chain
        draw.draw_chain(self.canvas, chain.names, chain.populations)
        self.explain_label.configure(
            text=build_explain_text(chain, model_name=self.model_var.get())
        )

    def on_apply_population_change(self) -> None:
        """Apply a dynamic population update model after changing one level."""
        if self.current_chain is None:
            messagebox.showinfo("Build first", "Please build the food chain first.")
            return

        changed_level = self.change_level_var.get()
        try:
            new_value = validate_population_value(
                self.change_value_entry.get(), changed_level
            )
        except ValueError as error:
            messagebox.showerror("Input problem", str(error))
            return

        model_name = self.model_var.get()
        try:
            updated_populations = apply_population_change(
                self.current_chain.populations,
                changed_level,
                new_value,
                model_name,
            )
        except ValueError as error:
            messagebox.showerror("Model problem", str(error))
            return

        self.current_chain.populations = updated_populations
        for level in LEVELS:
            self.population_entries[level].delete(0, tk.END)
            self.population_entries[level].insert(0, str(updated_populations[level]))

        draw.draw_chain(
            self.canvas,
            self.current_chain.names,
            self.current_chain.populations,
        )
        self.explain_label.configure(
            text=(
                build_explain_text(self.current_chain, model_name=model_name)
                + f"\nChanged {changed_level} to {new_value}, then updated linked levels."
            )
        )

    def on_reset(self) -> None:
        """Clear all input fields, explanation text, and drawing canvas."""
        for entry in self.name_entries.values():
            entry.delete(0, tk.END)

        for entry in self.population_entries.values():
            entry.delete(0, tk.END)

        self.change_value_entry.delete(0, tk.END)
        self.change_level_var.set("primary consumer")
        self.model_var.set("Balanced")

        self.current_chain = None
        self.explain_label.configure(text="Build a chain to see an explanation.")
        draw.clear_canvas(self.canvas)

    def on_load_example(self) -> None:
        """Fill name fields with one of the built-in example chains."""
        example = random.choice(EXAMPLE_CHAINS)
        for level in LEVELS:
            self.name_entries[level].delete(0, tk.END)
            self.name_entries[level].insert(0, example[level])

    def on_apply_default_populations(self) -> None:
        """Populate population entries with a default energy pyramid pattern."""
        for level in LEVELS:
            self.population_entries[level].delete(0, tk.END)
            self.population_entries[level].insert(0, str(DEFAULT_POPULATIONS[level]))

