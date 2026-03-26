"""
Lark Messenger utility helpers.
Message content builders (escaped JSON) and card template builders.
"""

import json


# --- Message content builders (return escaped JSON strings) ---

def build_text_content(text: str) -> str:
    """Build escaped JSON content for text message."""
    return json.dumps({"text": text})


def build_image_content(image_key: str) -> str:
    """Build escaped JSON content for image message."""
    return json.dumps({"image_key": image_key})


def build_file_content(file_key: str) -> str:
    """Build escaped JSON content for file message."""
    return json.dumps({"file_key": file_key})


def build_post_content(title: str, content_blocks: list, lang: str = "en_us") -> str:
    """Build escaped JSON content for rich text (post) message."""
    return json.dumps({lang: {"title": title, "content": content_blocks}})


def build_share_chat_content(chat_id: str) -> str:
    """Build escaped JSON content for share_chat message."""
    return json.dumps({"chat_id": chat_id})


# --- Card content builders (return dicts, send_card handles escaping) ---

def build_card_content(header_title: str, elements: list,
                       header_template: str = "blue",
                       update_multi: bool = True) -> dict:
    """Build card JSON dict. send_card() handles escaping.

    header_template colors: blue|green|red|orange|purple|indigo|turquoise|yellow|grey|wathet|violet|carmine
    """
    return {
        "config": {"update_multi": update_multi},
        "header": {
            "title": {"tag": "plain_text", "content": header_title},
            "template": header_template
        },
        "elements": elements
    }


def build_template_card(template_id: str, variables: dict = None) -> dict:
    """Build template card content for pre-built Lark card templates."""
    return {
        "type": "template",
        "data": {"template_id": template_id, "template_variable": variables or {}}
    }


def build_birthday_card(name: str, message: str = "Happy Birthday!") -> dict:
    """Build birthday greeting card."""
    return build_card_content(
        f"🎂 {message}",
        [
            {"tag": "markdown", "content": f"**{name}**, wishing you a wonderful birthday! 🎉"},
            {"tag": "hr"},
            {"tag": "markdown", "content": "From all of us at the team 💐"}
        ],
        header_template="purple"
    )


def build_ranking_card(title: str, items: list) -> dict:
    """Build ranking/leaderboard card. items: list of (rank, name, value) tuples."""
    rows = "\n".join(f"**#{r}** {n} — {v}" for r, n, v in items)
    return build_card_content(title, [{"tag": "markdown", "content": rows}],
                              header_template="orange")


def build_notification_card(title: str, body: str, actions: list = None) -> dict:
    """Build notification card with optional action buttons.

    actions: list of {"text": str, "value": str} dicts
    """
    elements = [{"tag": "markdown", "content": body}]
    if actions:
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "action",
            "actions": [
                {"tag": "button",
                 "text": {"tag": "plain_text", "content": a["text"]},
                 "value": a.get("value", {}),
                 "type": "primary" if i == 0 else "default"}
                for i, a in enumerate(actions)
            ]
        })
    return build_card_content(title, elements, header_template="blue")


def build_report_card(title: str, metrics: list, footer: str = None) -> dict:
    """Build report/summary card. metrics: list of (label, value) tuples."""
    rows = "\n".join(f"**{label}**: {value}" for label, value in metrics)
    elements = [{"tag": "markdown", "content": rows}]
    if footer:
        elements.append({"tag": "hr"})
        elements.append({"tag": "markdown", "content": footer})
    return build_card_content(title, elements, header_template="green")


# --- Webhook content helpers (return dicts for send_webhook content param) ---

def build_webhook_text(text: str) -> dict:
    """Build content dict for webhook text message.

    Usage: send_webhook(url, "text", build_webhook_text("Hello!"))
    """
    return {"text": text}


def build_webhook_card(title: str, elements: list,
                       header_template: str = "blue") -> dict:
    """Build content dict for webhook interactive card message.

    elements: list of card element dicts (same format as build_card_content)
    Usage: send_webhook(url, "interactive", build_webhook_card("Alert", [...]))
    """
    return {
        "config": {"update_multi": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": header_template
        },
        "elements": elements
    }
