"""
Lark Docs convert and nested blocks mixin - convert markdown/HTML to blocks,
clean convert output, and insert nested blocks via /descendant endpoint.

Official workflow (per Lark API docs):
  1. convert_to_blocks(markdown) -> blocks + first_level_block_ids
  2. clean_convert_output(blocks, for_descendant=True) -> remove merge_info only
  3. create_nested_blocks(doc_id, doc_id, first_level_block_ids, cleaned_blocks)

Or use import_markdown(doc_id, markdown_str) for one-call convenience.
"""

import copy
import time


class LarkDocsConvertMixin:
    """Mixin for LarkDocsClient - adds convert, clean, nested blocks, and
    import_markdown methods.
    Requires: _call_api, BASE_PATH, create_blocks, create_large_table from base/mixins."""

    @staticmethod
    def clean_convert_output(blocks, for_descendant=False):
        """Clean convert_to_blocks output for insertion. Returns new list.

        for_descendant=True (primary - /descendant endpoint):
          Only removes merge_info from table.property (per official Lark API docs).
          Keeps block_id, parent_id, children, cells, table_cell blocks intact.

        for_descendant=False (fallback - /children endpoint):
          Strips block_id, parent_id, children. Filters table_cell (type 32).
          Removes merge_info and cells from table blocks.
        """
        cleaned = []
        for b in copy.deepcopy(blocks):
            if for_descendant:
                # Descendant: only remove merge_info (official docs requirement)
                if b.get("block_type") == 31:
                    tbl = b.get("table", {})
                    tbl.get("property", {}).pop("merge_info", None)
            else:
                # create_blocks fallback: strip IDs, filter cells, clean tables
                if b.get("block_type") == 32:
                    continue
                if b.get("block_type") == 31:
                    tbl = b.get("table", {})
                    tbl.get("property", {}).pop("merge_info", None)
                    tbl.pop("cells", None)
                b.pop("block_id", None)
                b.pop("parent_id", None)
                b.pop("children", None)
            cleaned.append(b)
        return cleaned

    def convert_to_blocks(self, content, content_type="markdown"):
        """Convert markdown/HTML to block array.
        content_type: "markdown" or "html" (string, NOT integer).
        Returns {"blocks": [...], "first_level_block_ids": [...]}
        Scope required: docx:document.block:convert
        """
        return self._call_api(
            "POST", f"{self.BASE_PATH}/documents/blocks/convert",
            data={"content_type": content_type, "content": content}
        )

    def create_nested_blocks(self, document_id, block_id, children_id,
                             descendants, index=None):
        """Insert up to 1000 nested blocks via /descendant endpoint.

        Args:
            document_id: Target document ID
            block_id: Parent block ID (use document_id for root)
            children_id: Temp IDs for top-level blocks (1-1000 items).
                Use first_level_block_ids from convert_to_blocks output.
            descendants: Block objects with block_id/children tree structure.
                Use clean_convert_output(blocks, for_descendant=True).
            index: Insertion position (-1=last, 0=first). Default: -1
        """
        data = {"children_id": children_id, "descendants": descendants}
        if index is not None:
            data["index"] = index
        return self._call_api(
            "POST",
            f"{self.BASE_PATH}/documents/{document_id}/blocks/{block_id}/descendant",
            data=data, params={"document_revision_id": -1}
        )

    def import_markdown(self, document_id, content, content_type="markdown"):
        """Import markdown/HTML into a Lark document. One-call convenience method.

        Primary path: convert -> clean(for_descendant) -> create_nested_blocks
        Fallback: convert -> clean(flat) -> create_blocks in batches of 50

        Args:
            document_id: Target document ID
            content: Markdown or HTML string
            content_type: "markdown" (default) or "html"

        Returns: API response from insertion
        """
        # Step 1: Convert content to blocks
        result = self.convert_to_blocks(content, content_type)
        blocks = result.get("blocks", [])
        top_level_ids = result.get("first_level_block_ids", [])

        if not blocks:
            return {"blocks_inserted": 0, "method": "none"}

        # Step 2: Try descendant endpoint (primary - handles tables, up to 1000)
        if top_level_ids:
            cleaned = self.clean_convert_output(blocks, for_descendant=True)
            try:
                res = self.create_nested_blocks(
                    document_id, document_id,
                    children_id=top_level_ids,
                    descendants=cleaned
                )
                res["_method"] = "descendant"
                res["_blocks_count"] = len(cleaned)
                return res
            except Exception:
                pass  # fallback below

        # Step 3: Fallback - batch create_blocks (no nested tables)
        flat_blocks = self.clean_convert_output(blocks, for_descendant=False)
        inserted = 0
        for i in range(0, len(flat_blocks), 50):
            batch = flat_blocks[i:i + 50]
            self.create_blocks(document_id, document_id, batch)
            inserted += len(batch)
            if i + 50 < len(flat_blocks):
                time.sleep(0.4)

        return {"_method": "create_blocks_fallback", "_blocks_count": inserted}
