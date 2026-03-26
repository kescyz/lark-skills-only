# Secondary APIs (not implemented as tools)

Endpoints available via raw `_call_api()` but not wrapped as skill methods.
Agent can call these directly when needed using the LarkAPIBase pattern.

## Calendar Management
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /calendar/v4/calendars | POST | Create a shared calendar | both |
| /calendar/v4/calendars/:calendar_id | DELETE | Delete a shared calendar | both |
| /calendar/v4/calendars/:calendar_id | PATCH | Update calendar info (title, description, permissions) | both |
| /calendar/v4/calendars/:calendar_id/subscribe | POST | Subscribe to a calendar | both |
| /calendar/v4/calendars/:calendar_id/unsubscribe | POST | Unsubscribe from a calendar | both |
| /calendar/v4/calendars/search | POST | Search for calendars by keyword | both |
| /calendar/v4/calendars/:calendar_id/subscription | POST | Subscribe to calendar change events | both |
| /calendar/v4/calendars/:calendar_id/subscription | DELETE | Unsubscribe from calendar change events | both |

## Calendar ACL (Access Control)
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /calendar/v4/calendars/:calendar_id/acls | POST | Add access control (member permission) to calendar | both |
| /calendar/v4/calendars/:calendar_id/acls/:acl_id | DELETE | Delete an access control entry | both |
| /calendar/v4/calendars/:calendar_id/acls | GET | List all ACL entries for a calendar | both |

## Time Off Events
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /calendar/v4/timeoff_events | POST | Create a leave/time-off event for a user | tenant |
| /calendar/v4/timeoff_events/:timeoff_event_id | DELETE | Delete a leave/time-off event | tenant |

## Meeting Chat & Minute
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /calendar/v4/calendars/:calendar_id/events/:event_id/meeting_chat | POST | Create a meeting group chat for an event | both |
| /calendar/v4/calendars/:calendar_id/events/:event_id/meeting_chat | DELETE | Unbind meeting group chat from event | both |
| /calendar/v4/calendars/:calendar_id/events/:event_id/meeting_minute | POST | Create meeting minutes document for event | both |

## Meeting Room
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /meeting_room/freebusy/batch_get | GET | Query busy/free status of meeting rooms | tenant |
| /meeting_room/summary/batch_get | POST | Query meeting room event topics and details | tenant |

## Local Calendar Sync
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /calendar/v4/settings/generate_caldav_conf | POST | Generate CalDAV config for local device sync | user |
