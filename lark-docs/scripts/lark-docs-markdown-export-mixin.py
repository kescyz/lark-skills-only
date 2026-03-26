"""
Lark Docs markdown export mixin — export DocX documents to a markdown string.

Delegates block/media rendering to lark-docs-markdown-block-renderers module.
Supports: text, headings, bullet/ordered lists, code, quotes, todos, callouts,
dividers, grids, images, files, tables, task/bitable/sheet placeholders.

Limitations:
    - Tasklist embed (block 999): not supported by Lark API
    - Task (35): outputs placeholder
    - Sheet (30): outputs placeholder (cross-skill read not implemented)
    - Bitable (18): outputs placeholder (cross-skill read not implemented)
"""

import os
from importlib import import_module

_renderers = import_module("lark-docs-markdown-block-renderers")


class LarkDocsMarkdownExportMixin:
    """Mixin for LarkDocsClient — adds export_to_markdown method.

    Requires from base/client:
        list_blocks(document_id) -> list[dict]
        BASE_URL: str
        access_token: str
    """

    def export_to_markdown(self, document_id, download_media=False, save_dir=None):
        """Export document to markdown string.

        Args:
            document_id: DocX document ID
            download_media: If True, download images/files/board screenshots to save_dir
            save_dir: Directory to save media files (required if download_media=True)

        Returns:
            str: Full document as markdown

        Limitations:
            - Tasklist embed (block 999): not supported by API
            - Task (35): outputs [Task: task_id] placeholder
            - Sheet (30): outputs placeholder (cross-skill read not implemented)
            - Bitable (18): outputs placeholder (cross-skill read not implemented)
        """
        if download_media and save_dir:
            os.makedirs(save_dir, exist_ok=True)

        blocks = self.list_blocks(document_id)
        blocks_map = {b["block_id"]: b for b in blocks}

        # Find root page block (type 1)
        root = next((b for b in blocks if b.get("block_type") == 1), None)
        if not root:
            return ""

        lines = []
        for child_id in (root.get("children") or []):
            child = blocks_map.get(child_id)
            if child:
                rendered = _renderers.render_block(
                    child, blocks_map,
                    base_url=self.BASE_URL,
                    access_token=self.access_token,
                    download_media=download_media,
                    save_dir=save_dir,
                )
                if rendered is not None:
                    lines.append(rendered)

        return "\n\n".join(line for line in lines if line is not None)
