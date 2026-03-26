# Lark Calendar API Examples

> All examples assume the client is initialized per [SKILL.md](../SKILL.md).
> See [api-reference.md](./api-reference.md) for param details.
> See [api-validation.md](./api-validation.md) for enums and error codes.

---

## 1. List Today's Events

```python
start_ms, end_ms = get_today_range_ms()
events = client.list_events(calendar_id, start_ms, end_ms)

for e in events:
    start = e.get("start_time", {}).get("timestamp", "")
    print(f"- {e.get('summary', '(no title)')} @ {format_timestamp_for_display(int(start) * 1000)}")
```

---

## 2. Create Simple Event

```python
from datetime import datetime, timedelta
from utils import datetime_to_calendar_timestamp, get_default_reminder

# Tomorrow at 2 PM, 1 hour duration
tomorrow_14 = (datetime.now() + timedelta(days=1)).replace(
    hour=14, minute=0, second=0, microsecond=0
)

event = client.create_event(calendar_id, {
    "summary": "Team Sync",
    "start_time": {"timestamp": datetime_to_calendar_timestamp(tomorrow_14)},
    "end_time": {"timestamp": datetime_to_calendar_timestamp(tomorrow_14 + timedelta(hours=1))},
    "description": "Weekly sync meeting",
    "visibility": "default",
    "free_busy_status": "busy",
    "reminders": [get_default_reminder()]   # 30 min before
})
event_id = event["event_id"]
```

---

## 3. Create Event with Attendees and Video Conference

```python
from datetime import datetime, timedelta

meeting_dt = (datetime.now() + timedelta(days=2)).replace(
    hour=10, minute=0, second=0, microsecond=0
)

# Step 1: Create event
event = client.create_event(calendar_id, {
    "summary": "Product Review",
    "start_time": {"timestamp": datetime_to_calendar_timestamp(meeting_dt)},
    "end_time": {"timestamp": datetime_to_calendar_timestamp(meeting_dt + timedelta(hours=1, minutes=30))},
    "description": "<b>Agenda:</b><br>1. Q1 review<br>2. Q2 planning",
    "attendee_ability": "can_see_others",
    "vchat": {"vc_type": "vc"},   # Auto-generate Lark VC link
    "reminders": [{"minutes": 15}],
    "need_notification": True
})

# Step 2: Add attendees (get lark_user_id from MCP search_users)
client.add_event_attendees(calendar_id, event["event_id"], [
    {"type": "user", "user_id": "user_id_alice"},
    {"type": "user", "user_id": "user_id_bob", "is_optional": True}
])
```

---

## 4. Create Recurring Event (Weekly Standup)

```python
monday_9am = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
# Adjust to next Monday
days_ahead = (7 - monday_9am.weekday()) % 7 or 7
monday_9am += timedelta(days=days_ahead)

event = client.create_event(calendar_id, {
    "summary": "Daily Standup",
    "start_time": {"timestamp": datetime_to_calendar_timestamp(monday_9am)},
    "end_time": {"timestamp": datetime_to_calendar_timestamp(monday_9am + timedelta(minutes=15))},
    "recurrence": "FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR",
    "reminders": [{"minutes": 5}]
})
print(f"Recurring event created: {event['event_id']}")
```

---

## 5. Update Event Time

```python
# Reschedule to 3 PM same day
new_start = tomorrow_14.replace(hour=15)

updated = client.update_event(calendar_id, event_id, {
    "start_time": {"timestamp": datetime_to_calendar_timestamp(new_start)},
    "end_time": {"timestamp": datetime_to_calendar_timestamp(new_start + timedelta(hours=1))},
    "need_notification": True   # Notify attendees of reschedule
})
print(f"Rescheduled to: {updated['start_time']['timestamp']}")
```

---

## 6. Delete Event

```python
success = client.delete_event(calendar_id, event_id)
if success:
    print("Event deleted")

# Verify it's gone
events = client.list_events(calendar_id, start_ms, end_ms)
assert not any(e["event_id"] == event_id for e in events)
```

---

## 7. Create All-Day Event

```python
# All-day event uses "date" field instead of "timestamp"
event = client.create_event(calendar_id, {
    "summary": "Team Offsite",
    "start_time": {"date": "2026-03-15"},
    "end_time": {"date": "2026-03-16"},   # End date is exclusive in display
    "visibility": "public"
})
```
