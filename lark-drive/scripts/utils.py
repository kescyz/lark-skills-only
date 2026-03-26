"""Utility constants and helpers for Lark Drive operations."""

# ── File type constants ────────────────────────────────────────────────────────
FILE_TYPE_DOC = "doc"          # Legacy Lark Doc
FILE_TYPE_DOCX = "docx"        # New Lark Doc
FILE_TYPE_SHEET = "sheet"      # Lark Sheet
FILE_TYPE_MINDNOTE = "mindnote"  # Mind map
FILE_TYPE_BITABLE = "bitable"  # Lark Base
FILE_TYPE_FILE = "file"        # Binary/uploaded file
FILE_TYPE_FOLDER = "folder"    # Folder
FILE_TYPE_WIKI = "wiki"        # Wiki node

# File types that can be created via create_file()
CREATABLE_FILE_TYPES = {FILE_TYPE_DOC, FILE_TYPE_DOCX, FILE_TYPE_SHEET,
                        FILE_TYPE_MINDNOTE, FILE_TYPE_BITABLE}

# All valid file types for meta queries and permission ops
VALID_FILE_TYPES = {FILE_TYPE_DOC, FILE_TYPE_DOCX, FILE_TYPE_SHEET,
                    FILE_TYPE_MINDNOTE, FILE_TYPE_BITABLE,
                    FILE_TYPE_FILE, FILE_TYPE_FOLDER, FILE_TYPE_WIKI}

# ── Permission constants ───────────────────────────────────────────────────────
PERM_VIEW = "view"
PERM_EDIT = "edit"
PERM_FULL_ACCESS = "full_access"

VALID_PERM_TYPES = {PERM_VIEW, PERM_EDIT, PERM_FULL_ACCESS}

# ── Member type constants ──────────────────────────────────────────────────────
MEMBER_TYPE_EMAIL = "email"
MEMBER_TYPE_OPENID = "openid"
MEMBER_TYPE_OPENCHAT = "openchat"
MEMBER_TYPE_DEPT = "opendepartmentid"
MEMBER_TYPE_USERID = "userid"

VALID_MEMBER_TYPES = {MEMBER_TYPE_EMAIL, MEMBER_TYPE_OPENID, MEMBER_TYPE_OPENCHAT,
                      MEMBER_TYPE_DEPT, MEMBER_TYPE_USERID}

# ── Search doc types ───────────────────────────────────────────────────────────
SEARCH_DOC_TYPES = {"doc", "sheet", "slide", "bitable", "mindnote", "file"}


def validate_file_type(file_type: str) -> None:
    """Raise ValueError if file_type is not a known Lark file type."""
    if file_type not in VALID_FILE_TYPES:
        raise ValueError(
            f"Invalid file_type '{file_type}'. "
            f"Valid: {sorted(VALID_FILE_TYPES)}"
        )


def validate_perm(perm: str) -> None:
    """Raise ValueError if perm is not view/edit/full_access."""
    if perm not in VALID_PERM_TYPES:
        raise ValueError(
            f"Invalid perm '{perm}'. Valid: {sorted(VALID_PERM_TYPES)}"
        )
