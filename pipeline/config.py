# config.py
from enum import Enum


def is_valid_payment_status(value: str) -> bool:
    return value in ALLOWED_PAYMENT_STATUS


def is_valid_payment_method(value: str) -> bool:
    return value in ALLOWED_PAYMENT_METHODS


REQUIRED_COLUMNS = [
    "job_id",
    "date",
    "client_name",
    "service_type",
    "labor_amount",
    "total_amount",
    "payment_status",
]

OPTIONAL_COLUMNS = [
    "materials_amount",
    "tax_amount",
    "payment_method",
    "source",
    "notes",
]

EXPECTED_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS

EXPECTED_COLUMN_COUNT = len(EXPECTED_COLUMNS)

ALLOWED_PAYMENT_STATUS = {"paid", "unpaid", "partial"}

ALLOWED_PAYMENT_METHODS = {
    "cash",
    "card",
    "bank_transfer",
    "check",
    "online",
}

TOTAL_TOLERANCE = 0.05

DATE_FORMAT = "%Y-%m-%d"

class ErrorType(str, Enum):
    """Enumeration for standardized error codes."""
    MISSING_REQUIRED = "missing_required_field"
    INVALID_DATE = "invalid_date"
    INVALID_NUMERIC = "invalid_numeric"
    INVALID_STATUS = "invalid_payment_status"
    INVALID_SCHEMA = "invalid_schema"
    MALFORMED_ROW = "malformed_row"
    TOTAL_MISMATCH = "total_mismatch"

# Usage: error_type = ErrorType.INVALID_DATE.value)

