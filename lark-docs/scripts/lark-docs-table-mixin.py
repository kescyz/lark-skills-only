"""
Lark Docs table operations mixin — create, grow, fill, merge, delete table rows/columns.

Tables have a ~29-cell creation limit. For larger tables, create small then
grow with insert_table_row. Fill cells by updating existing empty text blocks
(not create_blocks, which causes extra blank lines).
"""

import time


class LarkDocsTableMixin:
    """Mixin for LarkDocsClient — adds 6 table convenience methods.
    Requires: create_blocks, batch_update_blocks, list_blocks from base class."""

    def create_table(self, document_id, parent_block_id, row_size, column_size,
                     column_width=None):
        """Create a table block. Max ~29 cells at creation (e.g. 7x4=28 OK, 10x3=30 FAIL).
        For larger tables, create small then use insert_table_row to grow.
        Returns created table block with auto-generated cells."""
        prop = {"row_size": row_size, "column_size": column_size}
        if column_width:
            prop["column_width"] = column_width
        block = {"block_type": 31, "table": {"property": prop}}
        return self.create_blocks(document_id, parent_block_id, [block])

    def insert_table_row(self, document_id, table_block_id, row_index):
        """Insert a new row at row_index in an existing table.
        New cells are auto-generated with empty text blocks."""
        return self.batch_update_blocks(document_id, [{
            "block_id": table_block_id,
            "insert_table_row": {"row_index": row_index}
        }])

    def insert_table_column(self, document_id, table_block_id, column_index):
        """Insert a new column at column_index in an existing table."""
        return self.batch_update_blocks(document_id, [{
            "block_id": table_block_id,
            "insert_table_column": {"column_index": column_index}
        }])

    def delete_table_rows(self, document_id, table_block_id,
                          row_start_index, row_end_index):
        """Delete rows [start, end) from an existing table."""
        return self.batch_update_blocks(document_id, [{
            "block_id": table_block_id,
            "delete_table_rows": {
                "row_start_index": row_start_index,
                "row_end_index": row_end_index
            }
        }])

    def merge_table_cells(self, document_id, table_block_id,
                          row_start, row_end, col_start, col_end):
        """Merge cells in range [row_start, row_end) x [col_start, col_end)."""
        return self.batch_update_blocks(document_id, [{
            "block_id": table_block_id,
            "merge_table_cells": {
                "row_start_index": row_start,
                "row_end_index": row_end,
                "column_start_index": col_start,
                "column_end_index": col_end
            }
        }])

    def fill_table_cells(self, document_id, table_block_id, data_rows):
        """Fill table cells with content. data_rows is list of rows,
        each row is list of dicts: {"text": str, "bold": bool} or plain str.

        Algorithm:
        1. list_blocks() to find empty text blocks inside cells
        2. batch_update_blocks to update existing empty text blocks
        This avoids extra blank lines caused by create_blocks in cells.
        """
        # Get all blocks to build cell→text_block map
        all_blocks = self.list_blocks(document_id)
        # Find cells (type 32) under this table
        cells = [b for b in all_blocks
                 if b.get("block_type") == 32
                 and b.get("parent_id") == table_block_id]
        cell_ids = {c["block_id"] for c in cells}
        # Map cell_id → first child text block_id
        cell_text_map = {}
        for b in all_blocks:
            pid = b.get("parent_id")
            if pid in cell_ids and pid not in cell_text_map:
                cell_text_map[pid] = b["block_id"]

        # Determine column count from table block properties
        table_block = next(
            (b for b in all_blocks if b.get("block_id") == table_block_id), None
        )
        col_size = (table_block["table"]["property"]["column_size"]
                    if table_block else len(data_rows[0]))

        # Build batch requests (max 200 per call)
        batch = []
        for row_idx, row in enumerate(data_rows):
            for col_idx, cell_data in enumerate(row):
                cell_idx = row_idx * col_size + col_idx
                if cell_idx >= len(cells):
                    break
                cell_id = cells[cell_idx]["block_id"]
                text_block_id = cell_text_map.get(cell_id)
                if not text_block_id:
                    continue
                text = cell_data if isinstance(cell_data, str) else cell_data.get("text", "")
                bold = False if isinstance(cell_data, str) else cell_data.get("bold", False)
                style = {}
                if bold:
                    style["bold"] = True
                element = {"text_run": {"content": text}}
                if style:
                    element["text_run"]["text_element_style"] = style
                batch.append({
                    "block_id": text_block_id,
                    "update_text_elements": {"elements": [element]}
                })

        # Execute in chunks of 200
        results = []
        for i in range(0, len(batch), 200):
            chunk = batch[i:i + 200]
            result = self.batch_update_blocks(document_id, chunk)
            results.append(result)
            if i + 200 < len(batch):
                time.sleep(0.4)
        return results

    def create_large_table(self, document_id, parent_block_id, row_size,
                           column_size, data_rows=None, index=None):
        """Create table of any size with optional data. Auto-handles >29 cell limit.

        Args:
            document_id: Document ID
            parent_block_id: Parent block (usually document_id for root)
            row_size: Total rows needed
            column_size: Total columns needed
            data_rows: Optional list of rows, each row is list of str or
                {"text": str, "bold": bool}
            index: Insert position (None=append)

        Returns: table block_id (str)
        """
        cells = row_size * column_size
        initial_rows = row_size if cells <= 29 else max(1, 29 // column_size)

        # Step 1: Create initial table
        result = self.create_table(document_id, parent_block_id,
                                   initial_rows, column_size)
        table_id = result["children"][0]["block_id"]

        # Step 2: Grow to target rows if needed
        for r in range(initial_rows, row_size):
            time.sleep(0.4)
            self.insert_table_row(document_id, table_id, r)

        # Step 3: Fill data if provided
        if data_rows:
            time.sleep(0.4)
            self.fill_table_cells(document_id, table_id, data_rows)

        return table_id
