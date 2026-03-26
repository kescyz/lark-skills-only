---
name: lark-messenger
description: LarkSuite messenger - send messages as bot, manage group chats, share files and cards. Use when user asks about sending messages, group chats, or cards. Requires lark-token-manager MCP.
---

# Lark Messenger

Send messages, interactive cards, and files as a bot. Manage group chats. All messages sent as bot identity, not user.

## Prerequisites

- `lark-token-manager` MCP server configured in `.mcp.json`
- `LARK_SKILL_API_KEY` exported before launching Claude Code
- Lark app with `im:message`, `im:message:send_as_bot`, `im:message:send_multi_users`, `im:message:send_multi_depts`, `im:chat`, `im:chat:readonly`, `im:resource` scopes
- **Org admin status** (enforced by MCP `get_tenant_token`)

## Permission Model

Most methods use `tenant_access_token` (bot token). Messages appear from the **bot app**, not from any user. The bot must be a member of a chat to send messages there. Some methods (`list_chat_members`, `is_in_chat`, `delete_chat`, `add_reaction`, `list_reactions`) also support `user_access_token`.

`send_webhook` requires **no token** — only the webhook URL from your Lark custom bot settings.

## Initialization

### Step 1: Get user info from MCP

Call MCP `whoami` -> `linked_users[].lark_open_id` (for context only, not required for bot ops)

### Step 2: Get TENANT token from MCP (NOT get_lark_token)

Call MCP `get_tenant_token(app_name=LARK_APP_NAME)` -> `{tenant_access_token, expire}`

### Step 3: Initialize client

```python
import sys, os

# Find scripts path relative to SKILL.md location
skill_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(skill_dir, 'scripts'))

from lark_api import LarkMessengerClient
from utils import build_text_content, build_card_content, build_birthday_card

client = LarkMessengerClient(
    access_token=TENANT_TOKEN_FROM_MCP,    # tenant_access_token, NOT user token
    user_open_id=OPEN_ID_FROM_WHOAMI       # optional, for context
)
```

## Encoding (Non-ASCII Data)

ALWAYS use the Python scripts (`scripts/`) for ALL API calls. NEVER use `curl` in Bash for requests containing non-ASCII characters (Vietnamese, Chinese, Japanese, etc.). Windows terminal encoding (cp1252) corrupts UTF-8 data, causing mojibake. The Python scripts use `urllib.request` with proper `ensure_ascii=False` encoding - this is the correct and safe approach.

## API Methods

| Method | Description |
|--------|-------------|
| `send_message(receive_id, msg_type, content, receive_id_type, uuid)` | Send message. `content` must be JSON-escaped string (use `build_text_content()` etc). `receive_id_type`: `chat_id`\|`open_id`\|`user_id`\|`email`. Returns message object with `message_id`. |
| `reply_message(message_id, msg_type, content, reply_in_thread, uuid)` | Reply to a message. Set `reply_in_thread=True` for thread reply. |
| `list_messages(container_id, start_time, end_time, ...)` | List messages in chat. **Timestamps in SECONDS** (not ms). Uses pagination. |
| `get_message(message_id)` | Get message by ID. Returns `items` array (multiple for merge_forward). |
| `delete_message(message_id)` | Delete a bot-sent message. Returns `True`. |
| `get_read_users(message_id)` | Get users who read a bot-sent message. 7-day window only. Paginated. |
| `send_card(receive_id, card_content, receive_id_type, uuid)` | Send interactive card. `card_content`: dict (auto-escaped, `update_multi` auto-set) or JSON string. Returns `message_id` for later updates. |
| `update_card(message_id, card_content)` | Update sent card via PATCH. Only `interactive` type. Max 14 days, 5 QPS/message. |
| `upload_image(image_path, image_type)` | Upload image via multipart. Returns `image_key`. |
| `upload_file(file_path, file_type, file_name, duration)` | Upload file via multipart. `file_type`: `opus`\|`mp4`\|`pdf`\|`doc`\|`xls`\|`ppt`\|`stream`. Returns `file_key`. |
| `create_chat(name, user_id_list, chat_type, owner_id, description)` | Create group chat. Bot auto-joins. `chat_type`: `private`\|`public`. |
| `get_chat(chat_id)` | Get chat info. |
| `list_chats(page_size)` | List bot's chats (not user's). Paginated. |
| `search_chats(query, page_size)` | Search chats by name. Query max 64 chars. |
| `add_chat_members(chat_id, member_ids, member_id_type)` | Add members. `succeed_type=1` for partial success. Returns invalid/not_existed IDs. |
| `remove_chat_members(chat_id, member_ids, member_id_type)` | Remove members from chat. |
| `list_chat_members(chat_id, member_id_type="open_id")` | List all members in a group. Bot not included. Supports tenant and user tokens. |
| `is_in_chat(chat_id)` | Check if current bot/user is a member of the group. Returns `bool`. Supports tenant and user tokens. |
| `update_chat(chat_id, **kwargs)` | Update group name, description, avatar, owner, etc. **Tenant token only.** |
| `delete_chat(chat_id)` | Disband a group. Bot must be owner/admin. Returns `bool`. Supports tenant and user tokens. |
| `forward_message(message_id, receive_id, receive_id_type="chat_id")` | Forward a message to user or group. **Tenant token only.** |
| `add_reaction(message_id, emoji_type)` | Add emoji reaction (e.g. `"THUMBSUP"`). Supports tenant and user tokens. Returns reaction dict with `reaction_id`. |
| `list_reactions(message_id, reaction_type=None)` | List reactions on a message. Optional filter by emoji type. Supports tenant and user tokens. |
| `pin_message(message_id)` | Pin a message in its group. **Tenant token only.** Returns pin data. |
| `batch_send(msg_type, content, dept_ids=None, open_ids=None)` | Async broadcast to up to 200 users or departments. **Tenant token only.** 500k/day limit. |

## Webhook Bot

Send messages to Lark custom bot webhooks (no token needed). Custom bots are configured in Lark group settings.

| Function | Description |
|----------|-------------|
| `send_webhook(webhook_url, msg_type, content, secret)` | Send to custom bot. No auth needed. Optional HMAC signing. |
| `build_webhook_text(text)` | Build `content` dict for text webhook message. |
| `build_webhook_card(title, elements, header_template)` | Build `content` dict for interactive card webhook message. |

### Webhook Example

```python
from lark_api import send_webhook
from utils import build_webhook_text, build_webhook_card

# Simple text
send_webhook("https://open.larksuite.com/open-apis/bot/v2/hook/xxx", "text", build_webhook_text("Deploy complete!"))

# With signing secret
send_webhook(url, "text", build_webhook_text("Secure message"), secret="my-secret-key")

# Interactive card
card = build_webhook_card("Alert", [{"tag": "markdown", "content": "**Build failed** on branch main"}], "red")
send_webhook(url, "interactive", card)
```

## Content Types

| msg_type | Content helper | Description |
|----------|---------------|-------------|
| `text` | `build_text_content(text)` | Plain text with @mention support |
| `image` | `build_image_content(image_key)` | Image (upload first) |
| `file` | `build_file_content(file_key)` | File attachment (upload first) |
| `post` | `build_post_content(title, blocks, lang)` | Rich text with formatting |
| `share_chat` | `build_share_chat_content(chat_id)` | Share a group chat |
| `interactive` | `build_card_content(...)` or card builders | Interactive card |

## Card Builders

`build_card_content(title, elements, template, update_multi)` — base builder. Also: `build_birthday_card`, `build_ranking_card`, `build_notification_card`, `build_report_card`, `build_template_card`. Cards max 30KB.

## Quick Examples

### Send text message
```python
content = build_text_content("Hello from bot!")
client.send_message(chat_id, "text", content)
```

### Send card and update it
```python
card = build_notification_card("Deploy Alert", "v2.1 deployed to prod", [{"text": "View Logs"}])
result = client.send_card(chat_id, card)
msg_id = result.get("message_id")
# Later: update the card
updated = build_notification_card("Deploy Alert", "v2.1 deploy **complete**")
client.update_card(msg_id, updated)
```

### Create group and send message
```python
chat = client.create_chat(name="Project Alpha", user_id_list=[user1_open_id, user2_open_id])
new_chat_id = chat.get("chat_id")
client.send_message(new_chat_id, "text", build_text_content("Welcome to Project Alpha!"))
```

## Personnel Lookup

Use MCP tools directly - no Python needed:

**Find specific people:**
```
search_users(query="Huong") -> [{name, email, department, lark_user_id, open_id, ...}]
```

**Invite entire department** (e.g., "toàn bộ phòng Engineering"):
```
list_departments() -> [{department_id, name, ...}]
list_department_users(department_id) -> [{user_id, open_id, name, ...}]
```
Then use each `open_id` in `user_id_list` for `create_chat` or `add_chat_members`.

## References

- [api-reference.md](./references/api-reference.md) — Full method params, return types, constraints
- [api-examples.md](./references/api-examples.md) — 8 realistic code scenarios
- [api-validation.md](./references/api-validation.md) — Enums, schemas, error codes, rate limits
