# Lark Comment API Examples

## Add a comment to a document

```python
from lark_api import LarkCommentClient

client = LarkCommentClient(access_token=ACCESS_TOKEN)

# Add global comment to a docx file
comment = client.add_comment(
    file_token="doccnGp4UK1UskrOEJwBXd3xxxx",
    file_type="docx",
    content="Please review this section before publishing.",
)
# Returns: {"comment_id": "1234567890", "user_id": "...", "is_solved": false, ...}
comment_id = comment["comment_id"]
```

## List comments on a sheet

```python
# List all open (unsolved) comments on a sheet
comments = client.list_comments(
    file_token="shtcnGp4UK1UskrOEJwBXd3xxxx",
    file_type="sheet",
    is_solved=False,
)
# Returns: list of comment dicts
for c in comments:
    print(c["comment_id"], c["is_solved"], c["reply_list"]["replies"])
```

## Reply to a comment thread

```python
# Add a reply to an existing comment
reply = client.add_reply(
    file_token="doccnGp4UK1UskrOEJwBXd3xxxx",
    file_type="docx",
    comment_id="1234567890",
    content="Updated — see revision in section 3.",
)
# Returns: {"reply_id": "...", "user_id": "...", "create_time": ..., "content": {...}}
```

## Resolve a comment

```python
# Mark comment as resolved
client.solve_comment(
    file_token="doccnGp4UK1UskrOEJwBXd3xxxx",
    file_type="docx",
    comment_id="1234567890",
    is_solved=True,  # False to reopen
)
# Returns: True on success
```

## Using @mentions in comments

Content elements support `@user` mentions via the `mention_user` type. Build elements manually when mentions are needed:

```python
# Comment with @mention — build elements manually (bypass _build_text_elements helper)
elements = [
    {"type": "text_run", "text_run": {"text": "Hey "}},
    {
        "type": "mention_user",
        "mention_user": {
            "user_id": "ou_xxxxxxxxxxxxxxxx",  # lark_open_id
            "name": "Alice",
        },
    },
    {"type": "text_run", "text_run": {"text": " can you check this?"}},
]

body = {
    "reply_list": {
        "replies": [{"content": {"elements": elements}}]
    }
}
# Call _call_api directly:
result = client._call_api(
    "POST",
    f"/drive/v1/files/{file_token}/comments",
    data=body,
    params={"file_type": "docx"},
)
```
