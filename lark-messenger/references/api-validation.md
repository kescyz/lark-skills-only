# Lark Messenger API Validation Reference

> See [api-reference.md](./api-reference.md) for method signatures.
> See [api-examples.md](./api-examples.md) for code samples.

---

## Token Type

**All 16 methods** require `tenant_access_token` (bot token) only.
Obtained via MCP `get_tenant_token(app_name)`. Never use `get_lark_token` (user token).

---

## Enums

### msg_type
`text` | `post` | `image` | `file` | `audio` | `media` | `sticker` | `interactive` | `share_chat` | `share_user`

### file_type (upload_file)
`opus` | `mp4` | `pdf` | `doc` | `xls` | `ppt` | `stream`

### receive_id_type
`open_id` | `user_id` | `union_id` | `email` | `chat_id`

### chat_type
`private` | `public`

### member_id_type
`open_id` | `user_id` | `union_id` | `app_id`

### image_type
`message` | `avatar`

### sort_type (list_messages)
`ByCreateTimeAsc` | `ByCreateTimeDesc`

### Card header templates
`blue` | `green` | `red` | `orange` | `purple` | `indigo` | `turquoise` | `yellow` | `grey` | `wathet` | `violet` | `carmine`

### Card element tags
`markdown` | `hr` | `action` | `note` | `img` | `column_set`

---

## Field Constraints

| Field | Constraint |
|-------|-----------|
| Text content | Max 4096 chars |
| Post content | Max 40960 chars (title max 200) |
| Card content | Max 30KB total |
| File upload | Max 30MB |
| Image upload | Max 10MB. JPEG, PNG, GIF, BMP, TIFF, WEBP |
| Chat name | Max 100 chars |
| Chat description | Max 500 chars |
| Search query | Max 64 chars |
| Members per request | Max 50 (add/remove) |
| uuid (idempotency) | Dedup within 24h |

---

## Rate Limits

| Scope | Limit |
|-------|-------|
| Global (app) | 1000 requests/min |
| Per user/chat | 5 QPS for send_message |
| Card update | 5 QPS per message_id |
| File upload | 10 QPS |

Rate limit response code: `1254290` — auto-retried by client.

---

## Card Constraints

| Rule | Detail |
|------|--------|
| Updatable types | Only `interactive` (msg_type) |
| Update window | Max 14 days after send |
| Update rate | 5 QPS per message_id |
| `update_multi` | Set `true` in config for shared card updates (auto-set by `send_card`) |
| Max size | 30KB |
| Template cards | `ctp_xxx` IDs from Lark Card Builder UI |
| Action callbacks | Require webhook server (out of scope for this skill) |
| Retrieved vs sent | GET response card JSON differs from sent JSON — don't reuse |

---

## Timestamp Rules

| API | Format | Unit |
|-----|--------|------|
| `list_messages` | Unix timestamp | **SECONDS** (10 digits) |
| `create_time` / `update_time` (returned) | String | Milliseconds |

---

## Error Codes

### Message Errors (230xxx)
| Code | Description |
|------|-------------|
| 230001 | Message not found |
| 230002 | Bot not in chat — must add bot first |
| 230006 | Message sending rate limited |
| 230017 | Cannot delete — not bot's message |
| 230020 | receive_id invalid for given receive_id_type |
| 230031 | Card update > 14 days after send |
| 230054 | Cannot update non-interactive message |

### Chat Errors (232xxx)
| Code | Description |
|------|-------------|
| 232001 | Chat not found |
| 232009 | Chat name too long |
| 232011 | Bot not in chat |
| 232014 | Insufficient permissions for member operation |
| 232016 | Member already in chat |

### General Errors
| Code | Description |
|------|-------------|
| 99991663 | Token expired — refresh via MCP |
| 99991664 | Token invalid |
| 1254290 | Rate limited — auto-retried by client |

---

## Permission Model

- **Org admin required** — enforced by MCP `get_tenant_token`, not by this skill
- Bot sends as **app identity** — messages show bot name/avatar, not user
- Bot must be **member of chat** to send messages (error 230002 if not)
- `list_chats` returns **bot's chats**, not the requesting user's chats
- Required Lark app scopes: `im:message`, `im:message:send_as_bot`, `im:message:send_multi_users`, `im:message:send_multi_depts`, `im:chat`, `im:chat:readonly`, `im:resource`
