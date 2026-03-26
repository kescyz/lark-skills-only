"""Utility helpers for Lark Base field types and record operations."""

# Field type constants (Lark Bitable type codes)
FIELD_TEXT = 1
FIELD_NUMBER = 2
FIELD_SINGLE_SELECT = 3
FIELD_MULTI_SELECT = 4
FIELD_DATE = 5
FIELD_CHECKBOX = 7
FIELD_USER = 11
FIELD_PHONE = 13
FIELD_URL = 15
FIELD_ATTACHMENT = 17
FIELD_SINGLE_LINK = 18
FIELD_LOOKUP = 19
FIELD_FORMULA = 20
FIELD_DUPLEX_LINK = 21
FIELD_LOCATION = 22
FIELD_GROUP_CHAT = 23
FIELD_CREATED_TIME = 1001
FIELD_MODIFIED_TIME = 1002
FIELD_CREATED_USER = 1003
FIELD_MODIFIED_USER = 1004
FIELD_AUTO_NUMBER = 1005

# UI type variants (same base type, different display)
# Note: "Email" ui_type is NOT accepted by Lark API (only settable via Lark UI).
# Use plain FIELD_TEXT (type=1) for email fields instead.
UI_TYPE_MAP = {
    "Barcode": (1, "Barcode"),
    "Currency": (2, "Currency"),
    "Progress": (2, "Progress"),
    "Rating": (2, "Rating"),
}

# Convenience constants for UI type variants
FIELD_BARCODE = (1, "Barcode")
FIELD_CURRENCY = (2, "Currency")
FIELD_PROGRESS = (2, "Progress")
FIELD_RATING = (2, "Rating")


def build_select_options(options, start_color=0):
    """Build single/multi select property for create_field/create_table.
    options: list of option name strings.
    Returns: {"options": [{name, color}, ...]} — ready to use as field property."""
    return {
        "options": [
            {"name": opt, "color": (start_color + i) % 54}
            for i, opt in enumerate(options)
        ]
    }


def build_link_property(table_id, multiple=True, back_field_name=None):
    """Build property for SingleLink (type 18) or DuplexLink (type 21).
    back_field_name: set for DuplexLink to auto-create reverse link field."""
    prop = {"table_id": table_id, "multiple": multiple}
    if back_field_name:
        prop["back_field_name"] = back_field_name
    return prop


def build_formula_property(expression, formatter="0"):
    """Build property for Formula field (type 20).
    formatter: number format string."""
    return {"formula_expression": expression, "formatter": formatter}


def build_date_property(date_format="yyyy-MM-dd", auto_fill=False):
    """Build property for Date field (type 5).
    auto_fill: True to auto-fill with current date on record creation."""
    return {"date_formatter": date_format, "auto_fill": auto_fill}


def chunk_records(records, chunk_size=500):
    """Split records into chunks for batch_create (max 500/request).
    Returns list of record lists."""
    return [records[i:i + chunk_size] for i in range(0, len(records), chunk_size)]
