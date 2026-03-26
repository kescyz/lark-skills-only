# Lark Messenger API Reference

> All methods use `tenant_access_token` (bot token) from MCP `get_tenant_token`.
> See [api-examples.md](./api-examples.md) for code samples.
> See [api-validation.md](./api-validation.md) for enums, schemas, error codes.

## LarkMessengerClient

```python
from lark_api import LarkMessengerClient
client = LarkMessengerClient(access_token="t-xxx", user_open_id="ou_xxx")
```

---

## Messages

### send_message(receive_id, msg_type, content, receive_id_type, uuid)

Send a message. Bot must be in the chat. `content` must be a JSON-escaped string.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| receive_id | string | **Yes** | Target ID | Format depends on `receive_id_type` |
| msg_type | string | **Yes** | Message type | `text`\|`post`\|`image`\|`file`\|`audio`\|`media`\|`sticker`\|`interactive`\|`share_chat`\|`share_user` |
| content | string | **Yes** | JSON-escaped string | Use `build_text_content()` etc. Max varies by type |
| receive_id_type | string | No | ID type (default: `chat_id`) | `open_id`\|`user_id`\|`union_id`\|`email`\|`chat_id` |
| uuid | string | No | Idempotency key | Dedup within 24h |

**Returns**: `Dict` — message object with `message_id`, `root_id`, `parent_id`, `create_time`, `update_time`, `msg_type`, `body`

### reply_message(message_id, msg_type, content, reply_in_thread, uuid)

Reply to a message by its `message_id`.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| message_id | string | **Yes** | Message to reply to | `om_xxx` format |
| msg_type | string | **Yes** | Message type | Same as send_message |
| content | string | **Yes** | JSON-escaped string | Same as send_message |
| reply_in_thread | bool | No | Thread reply (default: `False`) | Creates/continues thread |
| uuid | string | No | Idempotency key | Dedup within 24h |

**Returns**: `Dict` — message object

### list_messages(container_id, start_time, end_time, container_id_type, sort_type)

List messages in a chat. **Timestamps in SECONDS** (not milliseconds). Paginated via `_fetch_all`.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| container_id | string | **Yes** | Chat ID | `oc_xxx` format |
| start_time | int | No | Start time in **seconds** | Unix timestamp |
| end_time | int | No | End time in **seconds** | Must be > start_time |
| container_id_type | string | No | Default: `chat` | Only `chat` supported |
| sort_type | string | No | Default: `ByCreateTimeAsc` | `ByCreateTimeAsc`\|`ByCreateTimeDesc` |

**Returns**: `List[Dict]` — message objects

### get_message(message_id)

Get a single message. Returns `items` array (multiple items for merge_forward messages).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message_id | string | **Yes** | `om_xxx` format |

**Returns**: `Dict` with `items` array

### delete_message(message_id)

Delete a bot-sent message. Only works for messages sent by the bot.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message_id | string | **Yes** | `om_xxx` format |

**Returns**: `True` on success
**Errors**: 230001 (not found), 230017 (not bot's message)

### get_read_users(message_id)

Get users who read a bot-sent message. Only works within 7-day window.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message_id | string | **Yes** | `om_xxx` format |

**Returns**: `List[Dict]` — `{user_id_type, user_id, timestamp, tenant_key}`

---

## Cards

### send_card(receive_id, card_content, receive_id_type, uuid)

Send interactive card message. Wraps `send_message` with `msg_type="interactive"`.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| receive_id | string | **Yes** | Target ID | Same as send_message |
| card_content | dict\|string | **Yes** | Card content | Dict auto-escaped + `update_multi` auto-set. String used as-is. |
| receive_id_type | string | No | Default: `chat_id` | Same as send_message |
| uuid | string | No | Idempotency key | Dedup within 24h |

**Returns**: `Dict` — message object with `message_id` (save for `update_card`)

### update_card(message_id, card_content)

Update a previously sent interactive card via PATCH.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| message_id | string | **Yes** | Card message ID | `om_xxx` format |
| card_content | dict\|string | **Yes** | Updated card | Dict auto-escaped. String used as-is. |

**Constraints**: Only `interactive` type, max 14 days after send, 5 QPS per message.
**Returns**: `Dict` — updated message object
**Errors**: 230031 (>14 days), 230054 (non-interactive)

---

## Media

### upload_image(image_path, image_type)

Upload image via multipart/form-data. Returns `image_key` for use in messages.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| image_path | string | **Yes** | Local file path | JPEG, PNG, GIF, BMP, TIFF, WEBP. Max 10MB |
| image_type | string | No | Default: `message` | `message`\|`avatar` |

**Returns**: `str` — `image_key`

### upload_file(file_path, file_type, file_name, duration)

Upload file via multipart/form-data. Returns `file_key` for use in messages.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| file_path | string | **Yes** | Local file path | Max 30MB |
| file_type | string | **Yes** | File category | `opus`\|`mp4`\|`pdf`\|`doc`\|`xls`\|`ppt`\|`stream` |
| file_name | string | No | Display name | Auto-detected from path if omitted |
| duration | int | No | Audio/video duration (ms) | Required for `opus`\|`mp4` |

**Returns**: `str` — `file_key`

---

## Chats

### create_chat(name, user_id_list, chat_type, owner_id, description)

Create a group chat. Bot auto-joins as member.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| name | string | No | Chat name | Auto-generated if omitted |
| user_id_list | list[str] | No | Initial members (open_id) | Max 50 per request |
| chat_type | string | No | Default: `private` | `private`\|`public` |
| owner_id | string | No | Chat owner (open_id) | Bot if omitted |
| description | string | No | Chat description | Max 500 chars |

**Returns**: `Dict` — `{chat_id, name, ...}`

### get_chat(chat_id)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| chat_id | string | **Yes** | `oc_xxx` format |

**Returns**: `Dict` — chat object with `name`, `description`, `owner_id`, `chat_type`, `member_count`

### list_chats(page_size)

List bot's chats (not user's chats — since using tenant token). Paginated.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| page_size | int | No | Default: 50 |

**Returns**: `List[Dict]` — chat objects

### search_chats(query, page_size)

Search chats by name. Paginated.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| query | string | **Yes** | Search term | Max 64 chars |
| page_size | int | No | Default: 50 | |

**Returns**: `List[Dict]` — matching chat objects

### add_chat_members(chat_id, member_ids, member_id_type)

Add members to chat. Uses `succeed_type=1` for partial success.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| chat_id | string | **Yes** | Target chat | `oc_xxx` format |
| member_ids | list[str] | **Yes** | Member IDs to add | Max 50 per request |
| member_id_type | string | No | Default: `open_id` | `open_id`\|`user_id`\|`union_id`\|`app_id` |

**Returns**: `Dict` — `{invalid_id_list, not_existed_id_list}`
**Errors**: 232011 (bot not in chat), 232014 (insufficient permissions)

### remove_chat_members(chat_id, member_ids, member_id_type)

Remove members from chat.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| chat_id | string | **Yes** | Target chat | `oc_xxx` format |
| member_ids | list[str] | **Yes** | Member IDs to remove | Max 50 per request |
| member_id_type | string | No | Default: `open_id` | `open_id`\|`user_id`\|`union_id`\|`app_id` |

**Returns**: `Dict` — `{invalid_id_list}`

---

---

## Webhook Bot (standalone, no token needed)

### send_webhook(webhook_url, msg_type, content, secret)

Send a message to a Lark custom bot webhook URL. No `tenant_access_token` required.

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| webhook_url | string | **Yes** | Full webhook URL | `https://open.larksuite.com/open-apis/bot/v2/hook/{hook_id}` |
| msg_type | string | **Yes** | Message type | `text`\|`post`\|`interactive`\|`image` |
| content | dict | **Yes** | Message content | e.g. `{"text": "Hello"}` for text type |
| secret | string | No | Signing secret | HMAC-SHA256 signing — adds `timestamp` + `sign` to body |

**Returns**: `Dict` — `{"code": 0, "msg": "success"}` on success

**Raises**: `RuntimeError` on HTTP error or non-zero Lark code

**Signing**: When `secret` is provided, signs with `base64(hmac_sha256(key="{timestamp}\n{secret}", msg=""))` per Lark spec.

---

## Utilities (utils.py)

### Content Builders

All return JSON-escaped strings ready for `send_message` `content` param.

| Function | Args | Output JSON |
|----------|------|-------------|
| `build_text_content(text)` | text string | `{"text": "..."}` |
| `build_image_content(image_key)` | key from `upload_image` | `{"image_key": "..."}` |
| `build_file_content(file_key)` | key from `upload_file` | `{"file_key": "..."}` |
| `build_post_content(title, blocks, lang)` | title, content blocks, lang (`en_us`\|`zh_cn`) | `{"en_us": {"title": "...", "content": [...]}}` |
| `build_share_chat_content(chat_id)` | chat_id string | `{"chat_id": "..."}` |

### Webhook Content Builders

Return `dict` — pass directly as `content` param to `send_webhook()`.

| Function | Args | Output |
|----------|------|--------|
| `build_webhook_text(text)` | text string | `{"text": "..."}` |
| `build_webhook_card(title, elements, header_template)` | title, element list, color | card dict with config+header+elements |

### Card Builders

All return `dict` — pass directly to `send_card()` which handles JSON escaping.

| Function | Args | Description |
|----------|------|-------------|
| `build_card_content(title, elements, template, update_multi)` | Base builder | Generic card with header + elements |
| `build_template_card(template_id, variables)` | Pre-built template | Uses Lark Card Builder templates (`ctp_xxx`) |
| `build_birthday_card(name, message)` | Name, greeting | Purple birthday card |
| `build_ranking_card(title, items)` | Title, `[(rank, name, value)]` | Orange leaderboard card |
| `build_notification_card(title, body, actions)` | Title, body, optional buttons | Blue notification with actions |
| `build_report_card(title, metrics, footer)` | Title, `[(label, value)]`, footer | Green report/summary card |

---

## Card Structure

```python
{
    "config": {"update_multi": True},
    "header": {
        "title": {"tag": "plain_text", "content": "Header Text"},
        "template": "blue"  # color theme
    },
    "elements": [
        {"tag": "markdown", "content": "**bold** text"},
        {"tag": "hr"},
        {"tag": "action", "actions": [
            {"tag": "button", "text": {"tag": "plain_text", "content": "Click"}, "type": "primary"}
        ]},
        {"tag": "note", "elements": [{"tag": "plain_text", "content": "footnote"}]},
        {"tag": "img", "img_key": "img_xxx", "alt": {"tag": "plain_text", "content": "alt text"}}
    ]
}
```

**Max card size**: 30KB

---

## Message Object (returned by send/reply/get)

```python
{
    "message_id": "om_xxx",
    "root_id": "om_xxx",        # thread root
    "parent_id": "om_xxx",      # direct parent
    "msg_type": "text",
    "create_time": "1609459200",
    "update_time": "1609459200",
    "body": {"content": "{\"text\": \"hello\"}"}
}
```
