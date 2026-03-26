# Lark Calendar API Reference

> Token management handled by `lark-token-manager` MCP server.
> See [api-examples.md](./api-examples.md) for code samples.
> See [api-validation.md](./api-validation.md) for full enums, schemas, error codes.

## LarkCalendarClient

```python
from lark_api import LarkCalendarClient
client = LarkCalendarClient(access_token="u-xxx", user_open_id="ou_xxx", user_id="xxx")
```

---

## list_events(calendar_id, start_time_ms, end_time_ms)

List events within a time range. Accepts milliseconds and converts to seconds internally before calling the API. Returns up to 500 events per call (no pagination for time-range queries).

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| calendar_id | string | **Yes** | Calendar ID from MCP `whoami` | e.g. `"larksuite.com_xxx@group.calendar.larksuite.com"` |
| start_time_ms | int | **Yes** | Range start (milliseconds) | Converted to seconds internally |
| end_time_ms | int | **Yes** | Range end (milliseconds) | Must be > start_time_ms |

**Returns**: `List[Dict]` — event objects (see Event Object below)
**Errors**: 191000 (calendar not found), 191002 (no access), 190002 (bad params)

---

## create_event(calendar_id, event_data)

Create a calendar event. Auto-adds the authenticated user as an attendee if `user_id` is set on the client. To add additional attendees, call `add_event_attendees` after creation.

**Params (event_data)**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| summary | string | No | Event title | max 1000 chars |
| start_time | time_info | **Yes** | Event start | Use `timestamp` (seconds) for timed events, `date` (YYYY-MM-DD) for all-day |
| end_time | time_info | **Yes** | Event end | Must be > start_time; `timestamp` and `date` are mutually exclusive |
| description | string | No | Event description | max 40960 chars; supports HTML tags |
| need_notification | boolean | No | Notify attendees on create | default: `true` |
| visibility | string | No | Visibility scope | `default`\|`public`\|`private` |
| attendee_ability | string | No | Invitee permissions | `none`\|`can_see_others`\|`can_invite_others`\|`can_modify_event` (default: `none`) |
| free_busy_status | string | No | Availability status | `busy`\|`free` (default: `busy`) |
| location | event_location | No | Event location | `{name, address, latitude, longitude}` |
| vchat | vchat | No | Video conference settings | See vchat schema in api-validation.md |
| reminders | reminder[] | No | Reminder list | `[{"minutes": int}]`; range -20160~20160 |
| recurrence | string | No | RRULE recurrence rule | RFC 5545; max 2000 chars; COUNT and UNTIL are mutually exclusive |
| color | int | No | Event color (RGB int32) | `0` or `-1` = follow calendar color |

**time_info fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| timestamp | string | No | Unix seconds as string e.g. `"1602504000"` — use for timed events |
| date | string | No | Date string `"YYYY-MM-DD"` — use for all-day events only |
| timezone | string | No | IANA timezone e.g. `"Asia/Shanghai"` (default for non-all-day events) |

**Returns**: `Dict` — created event object with `event_id`
**Errors**: 190002 (bad params), 191002 (no calendar access), 193002 (no event permission), 195100 (user not in tenant)

---

## add_event_attendees(calendar_id, event_id, attendees)

Add one or more attendees to an existing event. Supports users, chat groups, meeting rooms, and external emails. Maximum 1000 attendees per request; max 3000 total per event.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| calendar_id | string | **Yes** | Calendar ID | Must be organizer's calendar |
| event_id | string | **Yes** | Event ID from create/list | — |
| attendees | attendee[] | **Yes** | List of attendees to add | See attendee fields below |

**Attendee fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | No | `user`\|`chat`\|`resource`\|`third_party` |
| user_id | string | No | Required when type=`user`; use `lark_user_id` from MCP |
| chat_id | string | No | Required when type=`chat` |
| room_id | string | No | Required when type=`resource` (meeting room) |
| third_party_email | string | No | Required when type=`third_party` |
| is_optional | boolean | No | Optional attendee flag (default: `false`) |

**Returns**: `List[Dict]` — updated full attendee list with RSVP statuses
**Errors**: 194002 (no permission to add), 194004 (invalid type), 193001 (event not found)

---

## update_event(calendar_id, event_id, event_data)

Partial update of event fields. Only fields provided in event_data are updated — all others remain unchanged. Organizers can update all fields; invitees can only update `visibility`, `free_busy_status`, `color`, `reminders`.

**Params**:
| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| calendar_id | string | **Yes** | Calendar ID | — |
| event_id | string | **Yes** | Event ID | — |
| summary | string | No | New title | max 1000 chars |
| start_time | time_info | No | New start time | Must also provide end_time |
| end_time | time_info | No | New end time | Must also provide start_time |
| description | string | No | New description | max 40960 chars |
| visibility | string | No | Visibility | `default`\|`public`\|`private` |
| free_busy_status | string | No | Availability | `busy`\|`free` |
| reminders | reminder[] | No | Replace reminders list | Only affects current identity |
| recurrence | string | No | RRULE string | max 2000 chars |
| location | event_location | No | Location object | — |
| color | int | No | Color int | `0` or `-1` = calendar default |
| need_notification | boolean | No | Notify attendees | — |

**Returns**: `Dict` — updated event object
**Errors**: 193002 (no permission), 193001 (not found), 193003 (deleted)

---

## delete_event(calendar_id, event_id)

Delete an event. Only the event organizer can delete. Sends bot notification to attendees by default.

**Params**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| calendar_id | string | **Yes** | Calendar ID |
| event_id | string | **Yes** | Event ID |

**Returns**: `bool` — `True` on success
**Errors**: 193002 (no permission, must be organizer), 193001 (not found), 193003 (already deleted)

---

## Utilities

| Function | Input | Output | Note |
|----------|-------|--------|------|
| `datetime_to_calendar_timestamp(dt)` | datetime | str | Seconds string — for start_time/end_time |
| `datetime_to_timestamp_ms(dt)` | datetime | int | Milliseconds — for list_events() params |
| `get_today_range_ms()` | — | (int, int) | start_ms, end_ms for today |
| `get_default_reminder()` | — | dict | `{"minutes": 30}` |
| `format_timestamp_for_display(ts_ms)` | int | str | `"YYYY-MM-DD HH:MM"` |

---

## Event Object (returned by all methods)

```python
{
    "event_id": "00592a0e-..._0",
    "summary": "Team Meeting",
    "start_time": {"timestamp": "1704355200", "timezone": "Asia/Shanghai"},
    "end_time": {"timestamp": "1704358800", "timezone": "Asia/Shanghai"},
    "visibility": "default",
    "attendee_ability": "none",
    "free_busy_status": "busy",
    "status": "confirmed",        # tentative | confirmed | cancelled
    "is_exception": False,
    "recurring_event_id": None,
    "reminders": [{"minutes": 30}],
    "recurrence": "FREQ=WEEKLY;INTERVAL=1;BYDAY=MO"  # or None
}
```
