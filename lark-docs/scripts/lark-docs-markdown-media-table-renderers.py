"""
Table and media rendering helpers for lark-docs markdown export.

Provides: render_table, render_image_block, render_file_block,
render_board_block, download_media_file.
"""

import os
import subprocess
import json
from importlib import import_module

_text = import_module("lark-docs-markdown-text-element-renderer")
render_elements = _text.render_elements


def render_table(table_block, blocks_map):
    """Build markdown table from DocX table block (type 31).

    Reads column_size from table.property, renders each cell's text children,
    then formats as pipe-delimited markdown table with header separator row.
    """
    table_data = table_block.get("table") or {}
    col_size = (table_data.get("property") or {}).get("column_size", 1)
    cell_ids = table_block.get("children") or []
    cells = [blocks_map[cid] for cid in cell_ids if cid in blocks_map]

    def render_cell(cell):
        parts = []
        for child_id in (cell.get("children") or []):
            child = blocks_map.get(child_id)
            if child:
                text_data = child.get("text") or {}
                parts.append(render_elements(text_data.get("elements") or []))
        return " ".join(p for p in parts if p)

    cell_texts = [render_cell(c) for c in cells]
    rows = [cell_texts[i:i + col_size] for i in range(0, len(cell_texts), col_size)]
    if not rows:
        return ""

    def fmt_row(row):
        padded = row + [""] * (col_size - len(row))
        return "| " + " | ".join(padded) + " |"

    lines = [fmt_row(rows[0])]
    lines.append("| " + " | ".join(["---"] * col_size) + " |")
    for row in rows[1:]:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def render_image_block(block, base_url, access_token, download_media, save_dir):
    """Render image block (type 27) to markdown."""
    token = (block.get("image") or {}).get("token", block.get("block_id", ""))
    if download_media and save_dir:
        path = download_media_file(token, save_dir, f"{token}.png", "image",
                                   base_url, access_token)
        return f"![image]({path})"
    return f"![image]({token})"


def render_file_block(block, base_url, access_token, download_media, save_dir):
    """Render file attachment block (type 23) to markdown."""
    file_data = block.get("file") or {}
    token = file_data.get("token", block.get("block_id", ""))
    filename = file_data.get("name", token)
    if download_media and save_dir:
        path = download_media_file(token, save_dir, filename, "file",
                                   base_url, access_token)
        return f"[\U0001f4ce {filename}]({path})"
    return f"[\U0001f4ce {filename}]({token})"


def render_board_block(block, base_url, access_token, download_media, save_dir):
    """Render whiteboard block (type 43) to markdown."""
    token = (block.get("board") or block.get("whiteboard") or {}).get("token", block.get("block_id", ""))
    if download_media and save_dir:
        path = download_media_file(token, save_dir, f"{token}.png", "board",
                                   base_url, access_token)
        return f"![board]({path})"
    return f"> \U0001f3a8 *Board: {token}*"


def download_media_file(token, save_dir, filename, media_type, base_url, access_token):
    """Download image/file/board via curl to save_dir. Returns relative path.

    Endpoints:
        board  → /board/v1/whiteboards/{token}/download_as_image
        others → /drive/v1/medias/{token}/download
    Follows redirects (-L) for Lark CDN. Raises on curl error or Lark JSON error.
    """
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    if media_type == "board":
        url = f"{base_url}/board/v1/whiteboards/{token}/download_as_image"
    else:
        url = f"{base_url}/drive/v1/medias/{token}/download"

    cmd = [
        "curl", "-s", "-X", "GET", url,
        "-H", f"Authorization: Bearer {access_token}",
        "-L",  # follow redirects to Lark CDN
        "-o", save_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise Exception(f"Media download failed: {result.stderr.decode()}")

    # Detect if Lark wrote a JSON error body instead of binary content
    if os.path.exists(save_path):
        with open(save_path, "rb") as f:
            head = f.read(32)
        if head.startswith(b'{"code"'):
            with open(save_path) as f:
                err = json.load(f)
            raise Exception(f"Lark media error: {err.get('msg')} (code={err.get('code')})")

    return os.path.relpath(save_path, save_dir)
