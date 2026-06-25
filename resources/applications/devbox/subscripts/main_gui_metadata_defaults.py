from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from subscripts.main_gui_metadata_common import (
    INTERNAL_MANUFACTURER_NAME,
    MANUFACTURER_TABLE_NAME,
    PRODUCT_TABLE_NAME,
    as_text,
    first_value,
    project_family,
    quote_identifier,
    real_manufacturer_row,
    table_columns,
    table_exists,
    utc_timestamp,
)
from subscripts.main_gui_metadata_manufacturer import (
    MANUFACTURER_READ_ONLY_COLUMNS,
    manufacturer_create_values,
    manufacturer_update_values,
    sync_manufacturer_defaults,
)
from subscripts.main_gui_metadata_product import (
    PRODUCT_READ_ONLY_COLUMNS,
    product_create_values,
    product_update_values,
    sync_product_defaults,
    sync_project_family,
)


__all__ = [
    "INTERNAL_MANUFACTURER_NAME", "MANUFACTURER_TABLE_NAME", "PRODUCT_TABLE_NAME",
    "MANUFACTURER_READ_ONLY_COLUMNS", "PRODUCT_READ_ONLY_COLUMNS", "as_text",
    "first_value", "project_family", "quote_identifier", "real_manufacturer_row",
    "table_columns", "table_exists", "utc_timestamp", "manufacturer_create_values",
    "manufacturer_update_values", "sync_manufacturer_defaults", "product_create_values",
    "product_update_values", "sync_product_defaults", "sync_project_family",
]
