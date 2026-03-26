# Lark Wiki API Examples

> Common code patterns. See [api-reference.md](./api-reference.md) for full params. See [api-validation.md](./api-validation.md) for error codes.

## Setup

```python
import subprocess
subprocess.run(["cp", "-r", "/mnt/skills/user/lark-wiki/scripts/", "/home/claude/"])

import sys
sys.path.insert(0, '/home/claude/scripts')

from lark_api import LarkWikiClient
from utils import OBJ_TYPE_DOCX, NODE_TYPE_ORIGIN, MEMBER_ROLE_ADMIN, MEMBER_TYPE_OPEN_ID

# ACCESS_TOKEN and OPEN_ID from lark-token-manager MCP
client = LarkWikiClient(access_token=ACCESS_TOKEN, user_open_id=OPEN_ID)
```

---

## Space Operations

```python
# List all spaces (paginated)
result = client.list_spaces(page_size=20)
for space in result["items"]:
    print(space["space_id"], space["name"])

# Get one space
space = client.get_space("7abc123")
print(space["name"], space["space_type"])  # "team" or "personal"

# Create space (user_access_token only)
new_space = client.create_space(name="Product Docs", description="Internal wiki")
space_id = new_space["space_id"]

# Restrict who can create pages (admin only)
client.update_space_setting(
    space_id=space_id,
    create_setting="not_allow",   # only admins create pages
    comment_setting="allow",
)
```

---

## Node (Page) Operations

```python
# Create page at root level
node = client.create_node(
    space_id="7abc123",
    obj_type=OBJ_TYPE_DOCX,
    title="Getting Started",
)
node_token = node["node_token"]

# Create child page under existing node
child = client.create_node(
    space_id="7abc123",
    obj_type=OBJ_TYPE_DOCX,
    parent_node_token=node_token,
    title="Installation Guide",
)

# Get node metadata (NOTE: uses ?token= query param)
info = client.get_node(token=node_token)
print(info["title"], info["obj_type"], info["parent_node_token"])

# List root-level pages
result = client.list_nodes(space_id="7abc123")
for node in result["items"]:
    print(node["node_token"], node["title"])

# List children of a specific node
children = client.list_nodes(
    space_id="7abc123",
    parent_node_token=node_token,
)

# Move page to different parent
client.move_node(
    space_id="7abc123",
    node_token="wikiXXX",
    target_parent_token="wikiYYY",  # None = move to root
)

# Copy page to another space
copy = client.copy_node(
    space_id="7abc123",
    node_token="wikiXXX",
    target_space_id="7def456",
    title="Copy of Getting Started",
)

# Rename page (doc/docx/shortcut only — NOT sheet/bitable/mindnote)
client.update_title(
    space_id="7abc123",
    node_token="wikiXXX",
    title="New Page Title",
)
```

---

## Member Management

```python
# Add admin to public space
client.add_member(
    space_id="7abc123",
    member_type=MEMBER_TYPE_OPEN_ID,
    member_id="ou_abc123",
    member_role=MEMBER_ROLE_ADMIN,
    need_notification=True,
)

# Remove member (body required in DELETE — handled automatically)
client.delete_member(
    space_id="7abc123",
    member_id="ou_abc123",
    member_type=MEMBER_TYPE_OPEN_ID,
    member_role=MEMBER_ROLE_ADMIN,
)
```

---

## Search

```python
# Search all accessible Wiki spaces (user_access_token only)
results = client.search_wiki(query="onboarding guide")
for item in results["items"]:
    print(item["title"], item["url"])

# Search within specific space
results = client.search_wiki(
    query="API authentication",
    space_id="7abc123",
    page_size=10,
)
```

---

## Move Docs to Wiki (Async)

```python
import time

result = client.move_docs_to_wiki(
    space_id="7abc123",
    obj_type=OBJ_TYPE_DOCX,
    obj_token="doxcnXXX",
    parent_wiki_token="wikiYYY",  # None = move to root
)

if "wiki_token" in result:
    # Migration completed immediately
    print("Done:", result["wiki_token"])
elif "task_id" in result:
    # Poll for completion
    task_id = result["task_id"]
    for _ in range(10):
        task = client.get_task(task_id)
        if task.get("status") == "done":
            print("Done:", task)
            break
        elif task.get("status") == "failed":
            print("Failed:", task)
            break
        time.sleep(2)
```
