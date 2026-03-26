# Lark Calendar API Validation Reference

> See [api-reference.md](./api-reference.md) for method signatures.
> See [api-examples.md](./api-examples.md) for code samples.

---

## time_info Schema

Used in `start_time` and `end_time` for create/update. `timestamp` and `date` are **mutually exclusive**.

```python
# Timed event (seconds-precision Unix timestamp as string)
{"timestamp": "1602504000", "timezone": "Asia/Shanghai"}

# All-day event (RFC 3339 date string)
{"date": "2026-03-15"}
# Note: all-day events use UTC+0 timezone regardless of "timezone" field
```

**Timezone**: IANA format (e.g. `"Asia/Shanghai"`, `"America/New_York"`). Default for timed events: `"Asia/Shanghai"`.

---

## vchat Schema

Video conference configuration. `vc_type` controls which other fields apply.

```python
# Lark VC (auto-generate meeting link when first attendee added)
{"vc_type": "vc"}

# Third-party video link
{
    "vc_type": "third_party",
    "icon_type": "vc",          # vc | live | default
    "description": "Join Zoom", # max 500 chars
    "meeting_url": "https://zoom.us/j/xxx"  # 1-2000 chars
}

# No video conference
{"vc_type": "no_meeting"}
```

**vc_type values**: `vc` | `third_party` | `no_meeting` | `lark_live` (read-only) | `unknown` (read-only)

**meeting_settings** (only for `vc_type: vc`):
```python
{
    "join_meeting_permission": "anyone_can_join",  # see enum below
    "auto_record": False,
    "open_lobby": True,
    "allow_attendees_start": True   # MUST be True when organizer is bot
}
```
`join_meeting_permission`: `anyone_can_join` | `only_organization_employees` | `only_event_attendees`

---

## event_location Schema

```python
{
    "name": "Conference Room A",    # 1-512 chars
    "address": "Floor 3, Tower B",  # 1-255 chars
    "latitude": 31.2304,            # GCJ-02 for China; WGS84 for international
    "longitude": 121.4737
}
```

**Note**: `latitude`/`longitude` are float. China mainland uses GCJ-02 coordinate system; outside China use WGS84.

---

## visibility Enum

| Value | Description |
|-------|-------------|
| `default` | Follows calendar visibility; only availability shown to others |
| `public` | Full event details visible to others |
| `private` | Details visible only to current user |

**Note**: `visibility` at event creation applies to all invitees. Updates apply only to current user's view.

---

## attendee_ability Enum

| Value | Invitee Permissions |
|-------|---------------------|
| `none` | Cannot edit, invite, or see attendee list |
| `can_see_others` | Can view attendee list only |
| `can_invite_others` | Can invite others + view attendee list |
| `can_modify_event` | Full edit + invite + view permissions |

---

## free_busy_status Enum

| Value | Meaning |
|-------|---------|
| `busy` | Marks user as busy during event (default) |
| `free` | User appears available during event |

---

## reminder Constraints

```python
{"minutes": 30}   # 30 minutes before event
{"minutes": -60}  # 60 minutes AFTER event start (negative = after)
```

- Range: `-20160` to `20160` minutes (14 days before/after)
- Per-user only: reminders do not propagate to other attendees

---

## recurrence (RRULE) Rules

Format per RFC 5545. Key constraints:
- **COUNT and UNTIL are mutually exclusive** — use only one
- Room bookings: recurring events cannot span > 2 years
- Max length: 2000 characters

```
FREQ=DAILY;INTERVAL=1                      # Daily
FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR  # Every weekday
FREQ=WEEKLY;INTERVAL=2;BYDAY=MO            # Bi-weekly Monday
FREQ=MONTHLY;BYMONTHDAY=15                 # Monthly on 15th
FREQ=DAILY;COUNT=10                        # Daily, 10 occurrences
FREQ=WEEKLY;UNTIL=20261231T000000Z         # Weekly until date
```

---

## Rate Limits

| Limit | Value |
|-------|-------|
| create/update/delete events | 1000/min, 50/sec |
| list events | 1000/min, 50/sec |
| add attendees | 1000/min, 50/sec |

---

## Error Code Reference

| Code | HTTP | Message | Fix |
|------|------|---------|-----|
| 190002 | 400 | invalid parameters in request | Check field names, types, required fields |
| 190003 | 500 | internal service error | Retry; contact support if persistent |
| 190004 | 429 | method rate limited | Backoff and reduce QPS |
| 190005 | 429 | app rate limited | Backoff and reduce QPS |
| 190007 | 404 | app bot_id not found | Enable bot capability in app settings |
| 191000 | 404 | calendar not found | Verify calendar_id from MCP `whoami` |
| 191001 | 400 | invalid calendar_id | Check calendar_id format |
| 191002 | 403 | no calendar access_role | Ensure token has calendar read/write access |
| 191003 | 403 | calendar is deleted | Use a different calendar_id |
| 191004 | 403 | invalid calendar type | Only `primary` and `shared` types supported |
| 193000 | 400 | invalid event_id | Verify event_id from create/list |
| 193001 | 404 | event not found | Check event_id; may have been deleted |
| 193002 | 403 | no permission to operate event | Must be organizer or have write permission |
| 193003 | 403 | event is deleted | Event already deleted |
| 193101 | 400 | organizer is bot — allow_attendees_start must be true | Set `allow_attendees_start: true` in meeting_settings |
| 194002 | 403 | no permission to create event attendees | Must be organizer or have `can_invite_others` |
| 194004 | 400 | invalid attendee type | Valid: user, chat, resource, third_party |
| 195100 | 404 | user not in tenant | Verify user_id via MCP `search_users` |
