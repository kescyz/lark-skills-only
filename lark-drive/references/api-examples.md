# Lark Drive API Examples

Realistic code samples for common Drive workflows.

---

## Setup (always first)

```python
import subprocess, sys
subprocess.run(["cp", "-r", "/mnt/skills/user/lark-drive/scripts/", "/home/claude/"])
sys.path.insert(0, '/home/claude/scripts')

from lark_api import LarkDriveClient

# ACCESS_TOKEN and OPEN_ID from MCP get_lark_token / whoami
client = LarkDriveClient(access_token=ACCESS_TOKEN, user_open_id=OPEN_ID)
```

---

## Example 1: Browse My Space root folder

```python
# Get root folder token
root = client.get_root_folder()
root_token = root["token"]
print(f"Root token: {root_token}")

# List all files in root (paginated)
page_token = None
all_files = []
while True:
    result = client.list_files(root_token, page_size=200, page_token=page_token)
    all_files.extend(result.get("files") or [])
    if not result.get("has_more"):
        break
    page_token = result.get("next_page_token")

for f in all_files:
    print(f"  [{f['type']}] {f['name']} — {f['token']}")
```

---

## Example 2: Upload a local file to Drive

```python
import os

file_path = "/tmp/report.pdf"
file_size = os.path.getsize(file_path)

# Get destination folder
root = client.get_root_folder()

result = client.upload_file(
    file_name="Monthly Report.pdf",
    parent_token=root["token"],
    file_path=file_path,
    size=file_size
)
print(f"Uploaded! file_token: {result['file_token']}")
```

---

## Example 3: Download a file from Drive

```python
# Only works for uploaded binary files (token prefix: box)
# Does NOT work for doc/sheet/docx/bitable — use export for those

result = client.download_file(
    file_token="boxbc123abc456def",
    save_path="/tmp/downloaded_report.pdf"
)
print(f"Saved to: {result}")
```

---

## Example 4: Create a folder structure and new doc

```python
root = client.get_root_folder()
root_token = root["token"]

# Create a project folder
folder = client.create_folder("Q1 2026 Reports", root_token)
folder_token = folder["token"]

# Create a new sheet inside the folder
doc = client.create_file(
    folder_token=folder_token,
    title="Q1 Sales Data",
    file_type="sheet"
)
print(f"Sheet created: {doc['url']}")

# Create a new Lark Doc
doc2 = client.create_file(
    folder_token=folder_token,
    title="Q1 Meeting Notes",
    file_type="docx"
)
print(f"Doc created: {doc2['url']}")
```

---

## Example 5: Share a file with a collaborator

```python
# Share a file with a user (view access)
client.add_permission(
    token="boxbc123abc456def",
    file_type="file",
    member_type="openid",
    member_id="ou_abc123xyz",
    perm="view"
)

# Upgrade to edit access
client.update_permission(
    token="boxbc123abc456def",
    file_type="file",
    member_id="ou_abc123xyz",
    perm="edit",
    member_type="openid"
)

# Revoke access
client.delete_permission(
    token="boxbc123abc456def",
    file_type="file",
    member_id="ou_abc123xyz",
    member_type="openid"
)
```

---

## Example 6: Search for documents

```python
# Search requires user_access_token (not tenant token)
results = client.search_files(
    query="Q1 sales",
    docs_types=["sheet", "docx"],
    count=20
)
print(f"Found {results['total']} docs")
for doc in results.get("docs_entities") or []:
    print(f"  [{doc['type']}] {doc['title']} — {doc['token']}")
```

---

## Example 7: Copy and move a file

```python
# Copy a file to another folder
copied = client.copy_file(
    file_token="boxbc123abc456def",
    name="Report Copy",
    file_type="file",
    folder_token="fldXYZ789"
)
print(f"Copied: {copied['file']['token']}")

# Move a file to a new folder
result = client.move_file(
    file_token="boxbc123abc456def",
    file_type="file",
    folder_token="fldABC123"
)
# Folder moves are async — check for task_id
if "task_id" in result:
    print(f"Async move started, task_id: {result['task_id']}")
    # Poll: GET /drive/v1/files/task_check?task_id=<id>
```

---

## Example 8: Batch metadata query

```python
tokens = [
    {"doc_token": "boxbc123", "doc_type": "file"},
    {"doc_token": "shttabc456", "doc_type": "sheet"},
    {"doc_token": "docxyz789", "doc_type": "docx"},
]
meta = client.batch_query_meta(tokens, with_url=True)

for m in meta.get("metas") or []:
    print(f"{m['title']} — modified: {m['latest_modify_time']}")

for fail in meta.get("failed_list") or []:
    print(f"Failed: {fail['token']} — error {fail['code']}")
```
