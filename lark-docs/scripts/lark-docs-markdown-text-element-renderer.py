"""
Text element rendering helpers for Lark DocX blocks.

Handles: text_run (with all styles), mention_user, mention_doc, equation.
Style application order: inline_code > bold > italic > strikethrough > underline > link.
"""


def render_elements(elements):
    """Render list of Lark text elements to a markdown string."""
    parts = []
    for el in (elements or []):
        if "text_run" in el:
            tr = el["text_run"]
            text = tr.get("content", "")
            style = tr.get("text_element_style") or {}
            parts.append(_apply_style(text, style))
        elif "mention_user" in el:
            uid = el["mention_user"].get("user_id", "")
            parts.append(f"@{uid}")
        elif "mention_doc" in el:
            md = el["mention_doc"]
            url = md.get("url", "")
            token = md.get("token", "")
            parts.append(f"[doc]({url})" if url else f"@{token}")
        elif "equation" in el:
            latex = el["equation"].get("content", "")
            parts.append(f"${latex}$")
    return "".join(parts)


def _apply_style(text, style):
    """Apply markdown formatting styles to a text string.

    inline_code takes full precedence — all other styles are ignored when set.
    Remaining styles applied in order: bold, italic, strikethrough, underline, link (outermost).
    """
    if not text:
        return text
    if style.get("inline_code"):
        return f"`{text}`"
    if style.get("bold"):
        text = f"**{text}**"
    if style.get("italic"):
        text = f"*{text}*"
    if style.get("strikethrough"):
        text = f"~~{text}~~"
    if style.get("underline"):
        text = f"<u>{text}</u>"
    link = style.get("link")
    if link:
        url = link.get("url", "") if isinstance(link, dict) else ""
        text = f"[{text}]({url})"
    return text
