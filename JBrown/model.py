"""Data models and validation helpers for the Food Chain Simulator."""

from dataclasses import dataclass
from typing import Dict, List

LEVELS: List[str] = [
    "producer",
    "primary consumer",
    "secondary consumer",
    "tertiary consumer",
]

DEFAULT_POPULATIONS: Dict[str, int] = {
    "producer": 1000,
    "primary consumer": 100,
    "secondary consumer": 10,
    "tertiary consumer": 1,
}

EXAMPLE_CHAINS: List[Dict[str, str]] = [
    {
        "producer": "Grass",
        "primary consumer": "Rabbit",
        "secondary consumer": "Snake",
        "tertiary consumer": "Hawk",
    },
    {
        "producer": "Phytoplankton",
        "primary consumer": "Zooplankton",
        "secondary consumer": "Small Fish",
        "tertiary consumer": "Tuna",
    },
    {
        "producer": "Oak Tree",
        "primary consumer": "Caterpillar",
        "secondary consumer": "Robin",
        "tertiary consumer": "Fox",
    },
]

LEVEL_COLORS: Dict[str, str] = {
    "producer": "#2e7d32",
    "primary consumer": "#1565c0",
    "secondary consumer": "#ef6c00",
    "tertiary consumer": "#6a1b9a",
}


@dataclass
class FoodChain:
    """Represents a 4-level food chain with optional populations."""

    names: Dict[str, str]
    populations: Dict[str, int]


def validate_names(raw_names: Dict[str, str]) -> Dict[str, str]:
    """Validate and normalize organism names for each food chain level."""
    names: Dict[str, str] = {}
    for level in LEVELS:
        cleaned = raw_names.get(level, "").strip()
        if not cleaned:
            raise ValueError(f"Please enter an organism name for {level}.")
        names[level] = cleaned
    return names


def validate_populations(raw_populations: Dict[str, str]) -> Dict[str, int]:
    """Validate population text input and return integer populations."""
    populations: Dict[str, int] = {}
    for level in LEVELS:
        raw_value = raw_populations.get(level, "").strip()
        if raw_value == "":
            raise ValueError(f"Please enter a population for {level}.")

        try:
            numeric = int(raw_value)
        except ValueError as error:
            raise ValueError(
                f"Population for {level} must be a whole number."
            ) from error

        if numeric < 0:
            raise ValueError(f"Population for {level} must be 0 or higher.")
        populations[level] = numeric

    return populations


def build_chain(raw_names: Dict[str, str], raw_populations: Dict[str, str]) -> FoodChain:
    """Create a validated FoodChain object from raw UI inputs."""
    names = validate_names(raw_names)
    populations = validate_populations(raw_populations)
    return FoodChain(names=names, populations=populations)


def build_explain_text(chain: FoodChain) -> str:
    """Return a concise explanation string for the current food chain."""
    producer = chain.names["producer"]
    primary = chain.names["primary consumer"]
    secondary = chain.names["secondary consumer"]
    tertiary = chain.names["tertiary consumer"]

    lines = [
        f"{primary} eats {producer}, so energy flows from producer to primary consumer.",
        f"{secondary} eats {primary}, and {tertiary} eats {secondary}.",
        "Typically many producers support fewer consumers at higher levels.",
    ]
    return "\n".join(lines)
