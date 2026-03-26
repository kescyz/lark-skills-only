"""
Utility functions for lark-sheets skill.
Sheets has no timestamp fields — only A1 range helpers needed.
"""


def make_range(sheet_id: str, start: str, end: str = None) -> str:
    """Build A1 range string: '{sheet_id}!A1:C3' or '{sheet_id}!A1'.

    Args:
        sheet_id: Sheet ID from query_sheets() (not sheet title).
        start: Start cell reference (e.g. 'A1').
        end: Optional end cell reference (e.g. 'C3').

    Returns:
        Range string like 'abc123!A1:C3'.
    """
    if end:
        return f"{sheet_id}!{start}:{end}"
    return f"{sheet_id}!{start}"


def col_to_letter(col: int) -> str:
    """Convert 1-based column index to letter: 1->A, 26->Z, 27->AA.

    Args:
        col: 1-based column number.

    Returns:
        Column letter(s) like 'A', 'Z', 'AA'.
    """
    result = ""
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        result = chr(65 + remainder) + result
    return result


def letter_to_col(letter: str) -> int:
    """Convert column letter to 1-based index: A->1, Z->26, AA->27.

    Args:
        letter: Column letter(s) like 'A', 'AA'.

    Returns:
        1-based column number.
    """
    result = 0
    for ch in letter.upper():
        result = result * 26 + (ord(ch) - 64)
    return result
