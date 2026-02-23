"""Entry point for the Food Chain Simulator desktop app."""

import tkinter as tk

from ui import FoodChainApp


def main() -> None:
    """Create and run the Tkinter application."""
    root = tk.Tk()
    root.geometry("1100x700")
    FoodChainApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

