---
name: lark-token-manager
description: Manage Lark/Feishu OAuth tokens via MCP. Use when needing Lark API access tokens, managing orgs/apps/users, or authorizing Lark apps. Requires lark-token-manager MCP server.
---

# Lark Token Manager

Manage Lark/Feishu user OAuth tokens through the `lark-token-manager` MCP server. This skill enables Claude to retrieve valid Lark access tokens for API calls, manage organizations, apps, and users.

## When to Use

- Getting a Lark access token to call Lark/Feishu APIs
- Checking current member identity and token status
- Starting OAuth authorization flow for a Lark app
- Managing orgs, apps, or users (admin only)

## MCP Server Connection

The MCP server must be configured in `.mcp.json`:

```json
{
  "mcpServers": {
    "lark-token-manager": {
      "type": "http",
      "url": "https://<project-ref>.supabase.co/functions/v1/mcp-server"
    }
  }
}
```

Authentication uses **OAuth 2.1** (PKCE). On first connection, your MCP client (Claude.ai, Claude Desktop, Antigravity) will redirect you to login via Supabase Auth. Your email/phone must be pre-registered as a member - contact Hưng Kescy (hungkescy@gmail.com / 039.345.4795) to register.

## Encoding (Non-ASCII Data)

ALWAYS use the Python scripts (`scripts/`) for ALL API calls. NEVER use `curl` in Bash for requests containing non-ASCII characters (Vietnamese, Chinese, Japanese, etc.). Windows terminal encoding (cp1252) corrupts UTF-8 data, causing mojibake. The Python scripts use `urllib.request` with proper `ensure_ascii=False` encoding - this is the correct and safe approach.

## Available Tools

### Token Tools (all members)

| Tool | Purpose | Key Params |
|------|---------|------------|
| `whoami` | Identity, orgs, linked users, token status | none |
| `get_lark_token` | Get valid access token for Lark API calls | `app_name` |
| `refresh_lark_token` | Force-refresh when token rejected by Lark | `app_name` |
| `start_oauth` | Generate OAuth URL for user authorization | `app_name`, `scopes?` |
| `get_tenant_token` | Get bot token (tenant_access_token) for IM/messaging ops. **Org admins only.** | `app_name` |

### Admin Tools (admin members only)

| Tool | Purpose | Key Params |
|------|---------|------------|
| `list_orgs` | List all organizations | none |
| `create_org` | Create organization | `name`, `slug?` |
| `update_org` | Update organization | `org_id`, `name?`, `slug?` |
| `delete_org` | Delete org + all data | `org_id` |
| `list_apps` | List Lark apps | `org_id?` |
| `create_app` | Register Lark app | `org_id`, `lark_app_id`, `app_secret`, `redirect_uri`, `display_name` |
| `update_app` | Update app config | `app_id`, fields to update |
| `delete_app` | Delete app + tokens | `app_id` |
| `list_users` | List Lark users | `org_id?` |
| `create_user` | Create user record | `org_id`, `lark_open_id`, `name`, `email` |
| `update_user` | Update user record | `user_id`, fields to update |
| `delete_user` | Delete user + tokens | `user_id` |

## Common Workflows

### Get a Lark Token for API Calls

```
1. Call `whoami` to check token status
2. If token is valid: call `get_lark_token` with app_name
3. If token is expired: call `refresh_lark_token` with app_name
4. If refresh fails (no refresh token): call `start_oauth` → user visits URL → retry
5. Use the returned access_token in Lark API Authorization header
```

### Using Token with Lark APIs

After getting a token via `get_lark_token`, use it as:
```
Authorization: Bearer <access_token>
```

For Lark Base MCP tools that require `user_access_token`, pass the token directly.

### First-Time OAuth Setup

```
1. Call `start_oauth` with the app_name
2. Present the authorization URL to the user
3. User opens URL in browser, authorizes the app
4. n8n webhook handles callback and stores tokens
5. Call `get_lark_token` to verify token is available
```

## Error Handling

- **Token expired**: Call `refresh_lark_token` first. If that fails, use `start_oauth`.
- **Admin required**: Non-admin members only see 4 tools (token tools). Admin tools return error.
- **401 Unauthorized**: OAuth token invalid/expired — MCP client will auto-redirect to login.
- **403 Not registered**: Email/phone not in members table — contact admin to register.
- **App not found**: Verify app `display_name` matches exactly (case-sensitive).

## Integration with Lark Base MCP

When using `Lark_Base_MCP_Server` tools that require `user_access_token`:

1. Call `get_lark_token` with the app name (e.g., "Lichee Bot")
2. Extract `access_token` from the response
3. Pass it as `user_access_token` parameter to Lark Base tools

## Building New Lark Skills

To create a new skill that uses Lark APIs (calendar, tasks, base, HR, etc.):
- **Primary**: Use `lark-skill-creator` dev tool — `.claude/skills/lark-skill-creator/SKILL.md` — automated scaffold, validate, and eval (7-step workflow)
- See: `references/lark-skill-builder-guide.md` — legacy manual guide (deprecated, superseded by lark-skill-creator)
- See: `references/lark-api-domains.md` — 13 Lark API domains with scopes and suggested skill groupings
