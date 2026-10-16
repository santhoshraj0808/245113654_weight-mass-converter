"""Conversion logic for the Weight / Mass Converter application.

This module is completely separate from the GUI. It handles all
weight/mass conversions using kilogram (kg) as the base unit.
"""

UNITS = {
    "Kilogram": 1.0,
    "Gram": 0.001,
    "Tonne": 1000.0,
}

ERROR_EMPTY = "Please enter a valid positive number."
ERROR_INVALID = "Please enter a valid positive number."
ERROR_NON_POSITIVE = "Please enter a valid positive number."
ERROR_UNKNOWN_UNIT = "Unknown unit '{}'. Choose from: {}"


def convert_weight(value, from_unit, to_unit):
    """Convert ``value`` from ``from_unit`` to ``to_unit``.

    Steps:
        1. Turn the input value into kilograms.
        2. Turn kilograms into the target unit.
        3. Return the converted result.

    Args:
        value (float): Numeric amount to convert.
        from_unit (str): Source unit, key of UNITS.
        to_unit (str): Target unit, key of UNITS.

    Returns:
        float: The converted value.

    Raises:
        KeyError: If either unit is not one of the UNITS keys.
        (GuiMainWindow validates input before calling this function.)
    """
    if from_unit not in UNITS:
        raise KeyError(ERROR_UNKNOWN_UNIT.format(from_unit, ", ".join(UNITS)))
    if to_unit not in UNITS:
        raise KeyError(ERROR_UNKNOWN_UNIT.format(to_unit, ", ".join(UNITS)))

    value_in_kg = value * UNITS[from_unit]
    result = value_in_kg / UNITS[to_unit]
    return result