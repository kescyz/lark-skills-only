"""
Lark Docs API client — DocX v1 document and block operations.
25 methods: Document (4) + Block (6) + Convert & Import (4) + Convenience (3) + Table (7 via mixin) + Export (1 via mixin).

Usage:
    from lark_api import LarkDocsClient
    client = LarkDocsClient(access_token=TOKEN, user_open_id=OPEN_ID)
"""

from lark_api_base import LarkAPIBase
from importlib import import_module


# Import mixins from kebab-case filenames
_table_mod = import_module("lark-docs-table-mixin")
LarkDocsTableMixin = _table_mod.LarkDocsTableMixin

_export_mod = import_module("lark-docs-markdown-export-mixin")
LarkDocsMarkdownExportMixin = _export_mod.LarkDocsMarkdownExportMixin

_convert_mod = import_module("lark-docs-convert-mixin")
LarkDocsConvertMixin = _convert_mod.LarkDocsConvertMixin


class LarkDocsClient(LarkDocsMarkdownExportMixin, LarkDocsConvertMixin, LarkDocsTableMixin, LarkAPIBase):
    """DocX API client. Documents are block trees; page block_id == document_id.
    Convert & nested blocks (3 methods) provided by LarkDocsConvertMixin.
    Table operations (6 methods) provided by LarkDocsTableMixin.
    Markdown export (1 method) provided by LarkDocsMarkdownExportMixin."""

    BASE_PATH = "/docx/v1"

    # --- Private helpers ---

    def _text_element(self, content, bold=False, italic=False, link=None):
        """Build a TextRun element."""
        style = {}
        if bold:
            style["bold"] = True
        if italic:
            style["italic"] = True
        if link:
            style["link"] = {"url": link}
        element = {"text_run": {"content": content}}
        if style:
            element["text_run"]["text_element_style"] = style
        return element

    # --- Document operations (4) ---

    def create_document(self, title=None, folder_token=None):
        """Create a new document. Returns {document: {document_id, revision_id, title}}."""
        data = {}
        if title:
            data["title"] = title
        if folder_token:
            data["folder_token"] = folder_token
        return self._call_api("POST", f"{self.BASE_PATH}/documents", data=data)

    def get_document(self, document_id):
        """Get document metadata (document_id, revision_id, title)."""
        return self._call_api("GET", f"{self.BASE_PATH}/documents/{document_id}")

    def get_raw_content(self, document_id, lang=0):
        """Get plain-text content of entire document. lang: 0=all, 1=zh, 2=en, 3=ja."""
        return self._call_api(
            "GET", f"{self.BASE_PATH}/documents/{document_id}/raw_content",
            params={"lang": lang}
        )

    def list_blocks(self, document_id, page_size=500):
        """List ALL blocks in document (paginated, auto-fetches all pages)."""
        return self._fetch_all(
            f"{self.BASE_PATH}/documents/{document_id}/blocks",
            params={}, page_size=page_size
        )

    # --- Block operations (6) ---

    def get_block(self, document_id, block_id):
        """Get a single block by ID."""
        return self._call_api(
            "GET", f"{self.BASE_PATH}/documents/{document_id}/blocks/{block_id}"
        )

    def get_block_children(self, document_id, block_id, page_size=500):
        """Get direct children of a block (paginated, auto-fetches all)."""
        return self._fetch_all(
            f"{self.BASE_PATH}/documents/{document_id}/blocks/{block_id}/children",
            params={}, page_size=page_size
        )

    def create_blocks(self, document_id, block_id, children, index=None):
        """Create 1-50 child blocks under parent block. Returns created blocks."""
        data = {"children": children}
        params = {"document_revision_id": -1}
        if index is not None:
            data["index"] = index
        return self._call_api(
            "POST",
            f"{self.BASE_PATH}/documents/{document_id}/blocks/{block_id}/children",
            data=data, params=params
        )

    def update_block(self, document_id, block_id, update_text_elements=None,
                     update_table_property=None, update_text_style=None):
        """Update a block's content. Pass one operation type per call."""
        data = {}
        if update_text_elements is not None:
            data["update_text_elements"] = update_text_elements
        if update_table_property is not None:
            data["update_table_property"] = update_table_property
        if update_text_style is not None:
            data["update_text_style"] = update_text_style
        return self._call_api(
            "PATCH",
            f"{self.BASE_PATH}/documents/{document_id}/blocks/{block_id}",
            data=data, params={"document_revision_id": -1}
        )

    def batch_update_blocks(self, document_id, requests):
        """Batch update up to 200 blocks in one call."""
        return self._call_api(
            "PATCH",
            f"{self.BASE_PATH}/documents/{document_id}/blocks/batch_update",
            data={"requests": requests},
            params={"document_revision_id": -1}
        )

    def delete_blocks(self, document_id, block_id, start_index, end_index):
        """Delete children of block by index range [start, end). Uses parent block_id."""
        return self._call_api(
            "DELETE",
            f"{self.BASE_PATH}/documents/{document_id}/blocks/{block_id}/children/batch_delete",
            data={"start_index": start_index, "end_index": end_index},
            params={"document_revision_id": -1}
        )

    # --- Convert & Nested Blocks (3) via LarkDocsConvertMixin ---

    # --- Convenience helpers (3) ---

    def create_text_block(self, document_id, parent_block_id, text,
                          bold=False, italic=False):
        """Create a single text block with plain string content."""
        block = {
            "block_type": 2,
            "text": {"elements": [self._text_element(text, bold=bold, italic=italic)]}
        }
        return self.create_blocks(document_id, parent_block_id, [block])

    def create_heading_block(self, document_id, parent_block_id, text, level=1):
        """Create heading block. level 1-9 maps to block_type 3-11."""
        block_type = level + 2  # heading1=3, heading2=4, ...heading9=11
        key = f"heading{level}"
        block = {
            "block_type": block_type,
            key: {"elements": [self._text_element(text)]}
        }
        return self.create_blocks(document_id, parent_block_id, [block])

    def create_todo_block(self, document_id, parent_block_id, text, done=False):
        """Create todo/checklist block."""
        block = {
            "block_type": 17,
            "todo": {
                "elements": [self._text_element(text)],
                "style": {"done": done}
            }
        }
        return self.create_blocks(document_id, parent_block_id, [block])
