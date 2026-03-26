# Lark Comment API Reference

All endpoints under: `https://open.larksuite.com/open-apis/drive/v1/files/:file_token/`

**Common query param:** `file_type` (required) — `doc` | `docx` | `sheet` | `file`
**Common header:** `Authorization: Bearer <access_token>`

---

## 1. Add a Global Comment

**POST** `/drive/v1/files/:file_token/comments`

Rate limit: 1000/min, 50/sec

### Query params
| Param | Required | Description |
|-------|----------|-------------|
| file_type | Yes | doc, docx, sheet, file |
| user_id_type | No | open_id (default), union_id, user_id |

### Request body
```json
{
    "reply_list": {
        "replies": [
            {
                "content": {
                    "elements": [
                        {
                            "type": "text_run",
                            "text_run": {"text": "comment text"}
                        }
                    ]
                }
            }
        ]
    }
}
```

Element types:
- `text_run` — plain text: `{"text": "..."}`
- `docs_link` — doc mention: `{"url": "https://..."}`
- `person` — user mention: `{"user_id": "ou_..."}`

### Response
```json
{
    "code": 0,
    "data": {
        "comment_id": "6916106822734512356",
        "user_id": "ou_...",
        "create_time": 1610281603,
        "update_time": 1610281603,
        "is_solved": false,
        "is_whole": true,
        "quote": "quoted text from doc",
        "reply_list": {
            "replies": [{"reply_id": "...", "content": {...}, "user_id": "...", "create_time": 0, "update_time": 0}]
        }
    }
}
```

### Required scopes (any one)
`docs:doc`, `docs:doc:readonly`, `drive:drive`, `drive:drive:readonly`, `sheets:spreadsheet`, `sheets:spreadsheet:readonly`

---

## 2. Get Document Comments in Pages

**GET** `/drive/v1/files/:file_token/comments`

Rate limit: 1000/min, 50/sec. Default 50 comments per page, max 100.

### Query params
| Param | Required | Description |
|-------|----------|-------------|
| file_type | Yes | doc, docx, sheet, file |
| is_whole | No | true = global comments only |
| is_solved | No | true = solved only, false = open only |
| page_token | No | Pagination token from previous response |
| page_size | No | Max 100, default 50 |
| user_id_type | No | open_id (default) |

### Response
```json
{
    "code": 0,
    "data": {
        "has_more": true,
        "page_token": "6916106822734512356",
        "items": [
            {
                "comment_id": "...",
                "user_id": "ou_...",
                "create_time": 1610281603,
                "update_time": 1610281603,
                "is_solved": false,
                "is_whole": true,
                "quote": "...",
                "reply_list": {"replies": [...]}
            }
        ]
    }
}
```

### Required scopes (any one)
`docs:doc`, `docs:doc:readonly`, `drive:drive`, `drive:drive:readonly`, `sheets:spreadsheet`, `sheets:spreadsheet:readonly`

---

## 3. Get a Global Comment

**GET** `/drive/v1/files/:file_token/comments/:comment_id`

Rate limit: 1000/min, 50/sec. Only supports global comments (not local/inline).

### Path params
| Param | Description |
|-------|-------------|
| file_token | Document token |
| comment_id | Comment ID |

### Query params
| Param | Required |
|-------|----------|
| file_type | Yes |
| user_id_type | No |

### Response
Same structure as single item in list endpoint (comment object with reply_list).

### Required scopes (any one)
`docs:doc`, `docs:doc:readonly`, `drive:drive`, `drive:drive:readonly`, `sheets:spreadsheet`, `sheets:spreadsheet:readonly`

---

## 4. Batch Query Comments

**POST** `/drive/v1/files/:file_token/comments/batch_query`

Rate limit: 100/min. Fetch multiple comments by ID list. Supports both global and local comments.

### Query params
| Param | Required |
|-------|----------|
| file_type | Yes |
| user_id_type | No |

### Request body
```json
{
    "comment_ids": ["1654857036541812356", "6916106822734512356"]
}
```

### Response
```json
{
    "code": 0,
    "data": {
        "items": [
            {
                "comment_id": "...",
                "is_solved": false,
                "is_whole": true,
                "reply_list": {"replies": [...]}
            }
        ]
    }
}
```

### Required scopes (any one)
`docs:document.comment:read`, `drive:drive`, `drive:drive:readonly`

---

## 5. Get Replies List

**GET** `/drive/v1/files/:file_token/comments/:comment_id/replies`

Rate limit: 100/min. Paginate through replies of a specific comment.

### Path params
| Param | Description |
|-------|-------------|
| file_token | Document token |
| comment_id | Comment ID |

### Query params
| Param | Required | Notes |
|-------|----------|-------|
| file_type | Yes | |
| page_size | No | Max 100 |
| page_token | No | Pagination |
| user_id_type | No | |

### Response
```json
{
    "code": 0,
    "data": {
        "items": [
            {
                "reply_id": "6916106822734512356",
                "user_id": "ou_...",
                "create_time": 1610281603,
                "update_time": 1610281603,
                "content": {
                    "elements": [
                        {"type": "text_run", "text_run": {"text": "comment text"}}
                    ]
                },
                "extra": {"image_list": []}
            }
        ],
        "page_token": "...",
        "has_more": false
    }
}
```

### Required scopes (any one)
`docs:document.comment:read`, `drive:drive`, `drive:drive:readonly`

---

## 6. Add Reply

**POST** `/drive/v1/files/:file_token/comments/:comment_id/replies`

Add a reply to an existing comment thread.

### Query params
| Param | Required |
|-------|----------|
| file_type | Yes |
| user_id_type | No |

### Request body
```json
{
    "content": {
        "elements": [
            {"type": "text_run", "text_run": {"text": "reply text"}}
        ]
    }
}
```

Note: Unlike `add_comment`, reply body wraps directly in `content` (not `reply_list.replies`).

### Response
Reply object with `reply_id`, `user_id`, `create_time`, `update_time`, `content`.

### Required scopes (any one)
`docs:doc`, `drive:drive`, `drive:drive:readonly`

---

## 7. Update Reply

**PUT** `/drive/v1/files/:file_token/comments/:comment_id/replies/:reply_id`

Rate limit: 1000/min, 50/sec. Full replacement of reply content.

### Path params
| Param | Description |
|-------|-------------|
| file_token | Document token |
| comment_id | Comment ID |
| reply_id | Reply ID |

### Query params
| Param | Required |
|-------|----------|
| file_type | Yes |
| user_id_type | No |

### Request body
```json
{
    "content": {
        "elements": [
            {"type": "text_run", "text_run": {"text": "updated reply text"}}
        ]
    }
}
```

### Response
```json
{"code": 0, "msg": "success", "data": {}}
```

### Required scopes (any one)
`docs:doc`, `docs:doc:readonly`, `drive:drive`, `drive:drive:readonly`, `sheets:spreadsheet`, `sheets:spreadsheet:readonly`

---

## 8. Delete Reply

**DELETE** `/drive/v1/files/:file_token/comments/:comment_id/replies/:reply_id`

Rate limit: 1000/min, 50/sec.

### Path params
| Param | Description |
|-------|-------------|
| file_token | Document token |
| comment_id | Comment ID |
| reply_id | Reply ID to delete |

### Query params
| Param | Required |
|-------|----------|
| file_type | Yes |

### Response
```json
{"code": 0, "msg": "success", "data": {}}
```

### Required scopes (any one)
`docs:doc`, `docs:doc:readonly`, `drive:drive`, `drive:drive:readonly`, `sheets:spreadsheet`, `sheets:spreadsheet:readonly`

---

## 9. Solve or Restore a Comment

**PATCH** `/drive/v1/files/:file_token/comments/:comment_id`

Rate limit: 1000/min, 50/sec.

### Query params
| Param | Required |
|-------|----------|
| file_type | Yes |

### Request body
```json
{"is_solved": true}
```

Pass `false` to restore/reopen a resolved comment.

### Response
```json
{"code": 0, "msg": "success", "data": {}}
```

### Required scopes (any one)
`docs:doc`, `docs:doc:readonly`, `drive:drive`, `drive:drive:readonly`, `sheets:spreadsheet`, `sheets:spreadsheet:readonly`

---

## Common Error Codes

| HTTP | Code | Description | Fix |
|------|------|-------------|-----|
| 400 | 1069301 | General failure | Retry; contact support if persists |
| 400 | 1069302 | Invalid parameter | Check file_token, file_type, comment_id |
| 403 | 1069303 | Forbidden | Check comment permission on document |
| 400 | 1069304 | Document deleted | Document no longer exists |
| 400 | 1069305 | Document not found | Check access to the document |
| 400 | 1069306 | Content review failed | Comment contains invalid/prohibited content |
| 404 | 1069307 | Not found | Check comment_id, @mentioned user/doc exists |
| 400 | 1069308 | Exceeded limit | Comment count limit reached |
| 400 | 1069399 | Internal error | Retry; contact support if persists |
| 400 | 1064230 | Data migration lock | Retry after migration completes |
