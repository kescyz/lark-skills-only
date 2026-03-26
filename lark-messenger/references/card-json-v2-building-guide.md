# Lark Card JSON 2.0 Building Guide

## Overview

Lark Card JSON 2.0 (schema `"2.0"`) is the only supported format for Card OpenAPI and `send_message(msg_type="interactive")`.
Cards embed structured content (text, buttons, images, columns) into chat messages.

## How to Send a Card

```python
# Option A: send_card() — dict auto-escaped, sets update_multi=True
client.send_card(chat_id, card_dict)

# Option B: send_message() — content must be JSON string
import json
client.send_message(chat_id, "interactive", json.dumps(card_dict))

# Option C: webhook (no token needed)
send_webhook(url, "interactive", card_dict)
```

## Basic Structure

```json
{
  "schema": "2.0",
  "config": {
    "update_multi": true,
    "enable_forward": true
  },
  "header": {
    "title": { "tag": "plain_text", "content": "Card Title" },
    "template": "blue"
  },
  "body": {
    "elements": []
  }
}
```

**Top-level keys:**
- `schema` — required, always `"2.0"`
- `config` — optional settings (`update_multi`, `enable_forward`, `width_mode`)
- `header` — optional colored header with title
- `body.elements` — list of element objects (max 200)

## Header Colors (`template`)

| Value | Color |
|---|---|
| `"blue"` | Blue (info) |
| `"green"` | Green (success) |
| `"red"` | Red (error/alert) |
| `"orange"` | Orange (warning) |
| `"yellow"` | Yellow |
| `"turquoise"` | Teal |
| `"purple"` | Purple |
| `"indigo"` | Indigo |
| `"wathet"` | Light blue |
| `"carmine"` | Dark red |
| `"neutral"` | Grey (default) |

## Element Types

### Text (markdown)

Supports Lark markdown: `**bold**`, `*italic*`, `~~strike~~`, `[link](url)`, inline code.

```json
{ "tag": "markdown", "content": "**Bold** text with [link](https://example.com)" }
```

### Text (plain_text)

No markdown, literal display only.

```json
{ "tag": "plain_text", "content": "Plain text content" }
```

### Divider

```json
{ "tag": "hr" }
```

### Image

```json
{
  "tag": "img",
  "img_key": "{{image_key}}",
  "alt": { "tag": "plain_text", "content": "Image description" },
  "mode": "fit_horizontal"
}
```

Note: `img_key` obtained via `upload_image()` — not a URL.

### Button

```json
{
  "tag": "button",
  "text": { "tag": "plain_text", "content": "Click Me" },
  "type": "primary",
  "url": "https://example.com"
}
```

`type` options: `"primary"` (blue), `"danger"` (red), `"default"` (grey)

For action callbacks (not URL): use `"action"` field — requires interactive callback setup.

### Column Set (side-by-side layout)

```json
{
  "tag": "column_set",
  "flex_mode": "none",
  "columns": [
    {
      "tag": "column",
      "width": "weighted",
      "weight": 1,
      "elements": [
        { "tag": "markdown", "content": "Left content" }
      ]
    },
    {
      "tag": "column",
      "width": "weighted",
      "weight": 1,
      "elements": [
        { "tag": "markdown", "content": "Right content" }
      ]
    }
  ]
}
```

`flex_mode`: `"none"` | `"stretch"` | `"flow"` | `"bisect"` | `"trisect"`

### Select Menu (static options — display only, needs callback for real interaction)

```json
{
  "tag": "select_static",
  "placeholder": { "tag": "plain_text", "content": "Choose..." },
  "options": [
    { "text": { "tag": "plain_text", "content": "Option A" }, "value": "a" },
    { "text": { "tag": "plain_text", "content": "Option B" }, "value": "b" }
  ]
}
```

## @Mentions in Card Text

Use Lark markdown mention syntax inside `markdown` elements:

```json
{ "tag": "markdown", "content": "<at id=ou_xxxx></at> Please review this." }
```

- `id` = user's `open_id` (starts with `ou_`)
- Use `<at id=all></at>` to @everyone in the group

## Notes

- Card JSON size limit: 30KB
- Max 200 elements per card
- `send_card()` auto-sets `config.update_multi = true` — required for card update via `update_card()`
- `update_card()`: PATCH to same message_id, max 14 days after send, 5 QPS per message
- For interactive callbacks (button actions, select changes): requires `action` field + webhook/callback URL setup — not covered here
