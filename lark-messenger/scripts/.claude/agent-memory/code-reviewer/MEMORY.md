# Code Reviewer Memory

## Project Structure
- Monorepo at `/home/kescy/project/lark-skill/` with plugins under `plugins/`
- Each plugin: `plugins/{name}/skills/{name}/scripts/` contains Python files
- Shared base: `lark_api_base.py` (LarkAPIBase) copied into each plugin's scripts dir
- Plans at `plans/` with research reports in `plans/reports/`
- 200 LOC file limit per project convention

## Lark API Patterns
- Base class uses `curl` subprocess for HTTP (not requests library)
- `_call_api()` handles JSON body; multipart uploads need custom `_upload_multipart()`
- Rate limit code `1254290` triggers retry in base class
- Image upload field name is `image`, file upload field name is `file` (different!)
- `receive_id_type` is always a query param, not body
- `list_messages` timestamps in SECONDS (not ms)
- Card content: `msg_type="interactive"`, content is JSON-escaped string
- `update_multi: true` in card config needed for shared card updates

## Common Review Findings
- Falsy checks (`if x:`) vs None checks (`if x is not None:`) for optional int params
- Missing JSON parse error handling on curl stdout
- File existence validation before upload operations
- Union types (dict|str) should be annotated, not just documented

## Reference Files
- Calendar client pattern: `plugins/lark-calendar/skills/lark-calendar/scripts/lark_api.py`
- Base class: `plugins/lark-calendar/skills/lark-calendar/scripts/lark_api_base.py`
- IM API analysis: `plans/reports/researcher-260302-0209-im-messaging-api-analysis.md`
- Group chat API analysis: `plans/reports/researcher-260302-0209-group-chat-api-analysis.md`
