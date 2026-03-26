"""
Block dispatch and children rendering helpers for lark-docs-markdown-export-mixin.

Text element rendering: lark-docs-markdown-text-element-renderer
Table/media rendering:  lark-docs-markdown-media-table-renderers
Provides: LANG_MAP, render_block, render_children.
"""

from importlib import import_module

_text = import_module("lark-docs-markdown-text-element-renderer")
render_elements = _text.render_elements

_media = import_module("lark-docs-markdown-media-table-renderers")
render_table = _media.render_table
render_image_block = _media.render_image_block
render_file_block = _media.render_file_block
render_board_block = _media.render_board_block

# Lark code block language codes → markdown fence language
LANG_MAP = {
    1: "plaintext", 7: "bash", 8: "csharp", 9: "cpp", 10: "c",
    12: "css", 22: "go", 24: "html", 28: "json", 29: "java",
    30: "javascript", 32: "kotlin", 39: "markdown", 43: "php",
    49: "python", 52: "ruby", 53: "rust", 56: "sql", 58: "scheme",
    61: "swift", 63: "typescript", 66: "xml", 67: "yaml",
}


def render_block(block, blocks_map, base_url, access_token,
                 download_media=False, save_dir=None):
    """Dispatch block to renderer by block_type. Returns markdown string or None."""
    btype = block.get("block_type")
    ctx = dict(base_url=base_url, access_token=access_token,
               download_media=download_media, save_dir=save_dir)

    if btype == 1:  # Page root — skip
        return None
    elif btype == 2:  # Text
        return render_elements((block.get("text") or {}).get("elements") or [])
    elif 3 <= btype <= 11:  # Heading 1-9
        level = btype - 2
        heading_data = block.get(f"heading{level}") or {}
        text = render_elements(heading_data.get("elements") or [])
        return f"{'#' * level} {text}"
    elif btype == 12:  # Bullet
        text = render_elements((block.get("bullet") or {}).get("elements") or [])
        return f"- {text}"
    elif btype == 13:  # Ordered list
        text = render_elements((block.get("ordered") or {}).get("elements") or [])
        return f"1. {text}"
    elif btype == 14:  # Code block
        code_data = block.get("code") or {}
        lang_code = (code_data.get("style") or {}).get("language", 1)
        lang = LANG_MAP.get(lang_code, "plaintext")
        text = render_elements(code_data.get("elements") or [])
        return f"```{lang}\n{text}\n```"
    elif btype == 15:  # Quote
        text = render_elements((block.get("quote") or {}).get("elements") or [])
        return f"> {text}"
    elif btype == 17:  # Todo/checkbox
        todo_data = block.get("todo") or {}
        done = (todo_data.get("style") or {}).get("done", False)
        check = "x" if done else " "
        text = render_elements(todo_data.get("elements") or [])
        return f"- [{check}] {text}"
    elif btype == 18:  # Bitable embed
        token = (block.get("bitable") or {}).get("token", block.get("block_id", ""))
        return f"> \U0001f4ca *Embedded Bitable: {token}*"
    elif btype == 19:  # Callout
        callout_data = block.get("callout") or {}
        emoji = (callout_data.get("style") or {}).get("emoji_id", "")
        child_lines = render_children(block, blocks_map, **ctx)
        inner = "\n> ".join(child_lines) if child_lines else ""
        prefix = f"> **{emoji}** " if emoji else "> "
        return f"{prefix}{inner}"
    elif btype == 22:  # Divider
        return "---"
    elif btype == 23:  # File attachment
        return render_file_block(block, base_url, access_token, download_media, save_dir)
    elif btype in (24, 25):  # Grid / GridColumn — render children sequentially
        child_lines = render_children(block, blocks_map, **ctx)
        return "\n\n".join(child_lines)
    elif btype == 27:  # Image
        return render_image_block(block, base_url, access_token, download_media, save_dir)
    elif btype == 30:  # Embedded Sheet
        token = (block.get("sheet") or {}).get("token", block.get("block_id", ""))
        return f"> \U0001f4cb *Embedded Sheet: {token}*"
    elif btype == 31:  # Table
        return render_table(block, blocks_map)
    elif btype == 32:  # TableCell — inline render for table builder
        child_lines = render_children(block, blocks_map, **ctx)
        return " ".join(child_lines)
    elif btype == 34:  # QuoteContainer
        child_lines = render_children(block, blocks_map, **ctx)
        return "\n".join(f"> {line}" for line in child_lines)
    elif btype == 35:  # Task reference
        task_id = (block.get("task") or {}).get("task_id", block.get("block_id", ""))
        return f"> \U0001f4cb *Task: {task_id}*"
    elif btype == 43:  # Whiteboard/Board
        return render_board_block(block, base_url, access_token, download_media, save_dir)
    elif btype == 53:  # Bitable View
        token = (block.get("bitable_view") or {}).get("token", block.get("block_id", ""))
        return f"> \U0001f4ca *Bitable View: {token}*"
    elif btype == 999:  # Tasklist embed — not supported by Lark API
        return "<!-- Unsupported block -->"
    else:
        return f"<!-- Unknown block type {btype} -->"


def render_children(block, blocks_map, base_url, access_token,
                    download_media=False, save_dir=None):
    """Render all children of a block, return list of non-empty strings."""
    lines = []
    for child_id in (block.get("children") or []):
        child = blocks_map.get(child_id)
        if child:
            rendered = render_block(child, blocks_map, base_url, access_token,
                                    download_media=download_media, save_dir=save_dir)
            if rendered:
                lines.append(rendered)
    return lines


