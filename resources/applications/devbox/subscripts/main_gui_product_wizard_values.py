from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from typing import Mapping


def apply_wizard_values(
    values: dict[str, object],
    available_columns: Mapping[str, object],
    wizard_values: Mapping[str, object],
) -> dict[str, object]:
    columns = {
        str(column).lower(): str(column)
        for column in available_columns
    }

    defaults = {
        "product_family": wizard_values.get("product_family", ""),
        "product_type": wizard_values.get("product_type", ""),
    }

    for key, value in defaults.items():
        column = columns.get(key)

        if column is not None:
            values[column] = value

    return values
