# Lark Messenger API Examples

> All examples assume the client is initialized per [SKILL.md](../SKILL.md).
> See [api-reference.md](./api-reference.md) for param details.
> See [api-validation.md](./api-validation.md) for enums and error codes.
>
> **Webhook examples** (9-10) require no token — just a webhook URL from Lark custom bot settings.

---

## 1. Send Text Message

```python
from utils import build_text_content

# Send to a group chat
content = build_text_content("Hello team! Daily standup in 5 minutes.")
result = client.send_message(chat_id, "text", content)
msg_id = result.get("message_id")

# Send to a specific user by open_id
client.send_message(user_open_id, "text", build_text_content("Hi! Your report is ready."),
                    receive_id_type="open_id")
```

---

## 2. Create Group Chat and Send First Message

```python
from utils import build_text_content

# Create private group with initial members
chat = client.create_chat(
    name="Project Alpha",
    user_id_list=[user1_open_id, user2_open_id, user3_open_id],
    chat_type="private",
    description="Project Alpha coordination group"
)
new_chat_id = chat.get("chat_id")

# Send welcome message
client.send_message(new_chat_id, "text",
                    build_text_content("Welcome to Project Alpha! Let's get started."))
```

---

## 3. Upload Image and Send

```python
from utils import build_image_content

# Upload image first
image_key = client.upload_image("/tmp/chart.png")

# Send as image message
client.send_message(chat_id, "image", build_image_content(image_key))
```

---

## 4. List Recent Chat History

```python
import time

# Get messages from last 24 hours (timestamps in SECONDS)
now = int(time.time())
yesterday = now - 86400

messages = client.list_messages(chat_id, start_time=yesterday, end_time=now)

for msg in messages:
    sender = msg.get("sender", {}).get("id", "unknown")
    msg_type = msg.get("msg_type", "")
    print(f"[{msg_type}] from {sender}: {msg.get('body', {}).get('content', '')[:50]}")
```

---

## 5. Send Birthday Card

```python
from utils import build_birthday_card

card = build_birthday_card("Nguyen Van A", "Happy Birthday!")
result = client.send_card(chat_id, card)
# Card sent with purple header, birthday emoji, and team greeting
```

---

## 6. Send KPI Ranking Card

```python
from utils import build_ranking_card

items = [
    (1, "Team Alpha", "98.5%"),
    (2, "Team Beta", "95.2%"),
    (3, "Team Gamma", "91.8%"),
    (4, "Team Delta", "88.3%"),
]
card = build_ranking_card("Q1 2026 Performance Rankings", items)
client.send_card(chat_id, card)
```

---

## 7. Send Notification Card with Actions, Then Update

```python
from utils import build_notification_card

# Send deploy notification with action button
card = build_notification_card(
    "Deploy Started",
    "Deploying **v2.1.0** to production...\n\nBranch: `main`\nCommit: `abc1234`",
    actions=[{"text": "View Pipeline", "value": {"url": "https://ci.example.com/123"}}]
)
result = client.send_card(chat_id, card)
msg_id = result.get("message_id")

# ... after deploy completes, update the card
updated_card = build_notification_card(
    "Deploy Complete",
    "Successfully deployed **v2.1.0** to production.\n\nDuration: 3m 42s\nStatus: All checks passed"
)
client.update_card(msg_id, updated_card)
```

---

## 8. Full Workflow: Group + Members + Card + Cleanup

```python
from utils import build_text_content, build_report_card

# 1. Create group
chat = client.create_chat(name="Sprint Review", user_id_list=[pm_open_id])
cid = chat.get("chat_id")

# 2. Add more members
result = client.add_chat_members(cid, [dev1_open_id, dev2_open_id, qa_open_id])
if result.get("invalid_id_list"):
    print(f"Invalid IDs: {result['invalid_id_list']}")

# 3. Send report card
card = build_report_card("Sprint 14 Summary", [
    ("Velocity", "42 points"),
    ("Completed", "18/21 stories"),
    ("Bugs Fixed", "7"),
    ("Test Coverage", "89%"),
], footer="Next sprint starts Monday. Retro at 3 PM today.")
card_result = client.send_card(cid, card)

# 4. Upload and share detailed report
file_key = client.upload_file("/tmp/sprint-14-report.pdf", "pdf")
from utils import build_file_content
client.send_message(cid, "file", build_file_content(file_key))

# 5. After sprint review, remove temp members
client.remove_chat_members(cid, [qa_open_id])
```

---

## 9. Webhook: CI/CD Notification (No Token)

```python
from lark_api import send_webhook
from utils import build_webhook_text

WEBHOOK_URL = "https://open.larksuite.com/open-apis/bot/v2/hook/your_hook_id"

# Simple deploy notification — no token, no client initialization needed
send_webhook(WEBHOOK_URL, "text", build_webhook_text("Deploy v2.1.0 complete! All checks passed."))
```

---

## 10. Webhook: Signed Alert Card

```python
from lark_api import send_webhook
from utils import build_webhook_card

WEBHOOK_URL = "https://open.larksuite.com/open-apis/bot/v2/hook/your_hook_id"
WEBHOOK_SECRET = "your_signing_secret"  # from Lark bot settings

# Build an alert card
card = build_webhook_card(
    "Build Failed",
    [
        {"tag": "markdown", "content": "**Branch**: `feature/login`\n**Error**: Unit tests failed (3/47)"},
        {"tag": "hr"},
        {"tag": "markdown", "content": "Check CI pipeline for details."}
    ],
    header_template="red"
)

# Send with HMAC signing — adds timestamp + sign to body
send_webhook(WEBHOOK_URL, "interactive", card, secret=WEBHOOK_SECRET)
```
