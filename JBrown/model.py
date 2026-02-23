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

POPULATION_MODELS: Dict[str, Dict[str, float]] = {
    "Balanced": {"prey_weight": 0.65, "predator_weight": 0.65},
    "Predator Pressure": {"prey_weight": 0.55, "predator_weight": 0.95},
    "Bottom-Up": {"prey_weight": 0.95, "predator_weight": 0.40},
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


def validate_population_value(text_value: str, level: str) -> int:
    """Validate one population value for dynamic change actions."""
    try:
        numeric = int(text_value.strip())
    except ValueError as error:
        raise ValueError(f"Population for {level} must be a whole number.") from error

    if numeric < 0:
        raise ValueError(f"Population for {level} must be 0 or higher.")
    return numeric


def build_chain(raw_names: Dict[str, str], raw_populations: Dict[str, str]) -> FoodChain:
    """Create a validated FoodChain object from raw UI inputs."""
    names = validate_names(raw_names)
    populations = validate_populations(raw_populations)
    return FoodChain(names=names, populations=populations)


def safe_ratio(new_value: int, old_value: int) -> float:
    """Return a stable ratio for population-change math."""
    if old_value <= 0:
        return 1.0 if new_value <= 0 else 1.0 + min(new_value / 10.0, 5.0)
    return max(new_value / old_value, 0.0)


def _compute_factor(
    level: str,
    ratios: Dict[str, float],
    prey_weight: float,
    predator_weight: float,
) -> float:
    """Compute multiplicative population factor for one trophic level."""
    prey_map = {
        "producer": None,
        "primary consumer": "producer",
        "secondary consumer": "primary consumer",
        "tertiary consumer": "secondary consumer",
    }
    predator_map = {
        "producer": "primary consumer",
        "primary consumer": "secondary consumer",
        "secondary consumer": "tertiary consumer",
        "tertiary consumer": None,
    }

    factor = 1.0
    prey_level = prey_map[level]
    predator_level = predator_map[level]

    if prey_level is not None:
        factor *= ratios[prey_level] ** prey_weight
    if predator_level is not None:
        factor *= ratios[predator_level] ** (-predator_weight)

    return factor


def apply_population_change(
    current_populations: Dict[str, int],
    changed_level: str,
    new_value: int,
    model_name: str,
) -> Dict[str, int]:
    """Apply a population change and propagate realistic updates across levels."""
    if model_name not in POPULATION_MODELS:
        raise ValueError("Please choose a valid population update model.")

    old = dict(current_populations)
    updated = dict(current_populations)
    updated[changed_level] = new_value

    model = POPULATION_MODELS[model_name]
    prey_weight = model["prey_weight"]
    predator_weight = model["predator_weight"]

    for _ in range(3):
        ratios = {level: safe_ratio(updated[level], old[level]) for level in LEVELS}
        for level in LEVELS:
            if level == changed_level:
                continue

            factor = _compute_factor(level, ratios, prey_weight, predator_weight)
            next_value = int(round(max(0.0, old[level] * factor)))
            updated[level] = max(0, next_value)

    return updated


def build_explain_text(chain: FoodChain, model_name: str | None = None) -> str:
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

    if model_name:
        lines.append(f"Dynamic population model in use: {model_name}.")

    return "\n".join(lines)

