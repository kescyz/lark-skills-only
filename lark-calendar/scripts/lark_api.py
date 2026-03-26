"""
Lark Calendar API client.
Handles Calendar events and attendee management.
"""

from typing import Optional, Dict, Any, List
from lark_api_base import LarkAPIBase


class LarkCalendarClient(LarkAPIBase):
    """Client for Lark Calendar APIs."""

    def list_events(self, calendar_id: str, start_time_ms: int, end_time_ms: int) -> List[Dict[str, Any]]:
        """List events in calendar within time range.

        Note: Calendar API uses SECONDS, but this function accepts milliseconds
        for consistency with Task API. Conversion is done internally.
        """
        start_sec = start_time_ms // 1000
        end_sec = end_time_ms // 1000
        params = {
            "start_time": str(start_sec),
            "end_time": str(end_sec)
        }
        data = self._call_api("GET", f"/calendar/v4/calendars/{calendar_id}/events", params=params)
        return data.get("items", [])

    def create_event(self, calendar_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create calendar event. Auto-adds creator and other attendees."""
        attendees = list(event_data.get("attendees", []) or [])
        create_data = {k: v for k, v in event_data.items() if k != "attendees"}

        if self.user_id:
            creator_exists = any(
                a.get("user_id") == self.user_id or a.get("is_organizer")
                for a in attendees
            )
            if not creator_exists:
                attendees.insert(0, {"type": "user", "user_id": self.user_id})

        result = self._call_api("POST", f"/calendar/v4/calendars/{calendar_id}/events", data=create_data)

        if attendees and result.get("event", {}).get("event_id"):
            event_id = result["event"]["event_id"]
            self.add_event_attendees(calendar_id, event_id, attendees)

        return result

    def add_event_attendees(self, calendar_id: str, event_id: str, attendees: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add attendees to an existing event. Uses user_id format."""
        attendee_data = {"attendees": attendees}
        return self._call_api(
            "POST",
            f"/calendar/v4/calendars/{calendar_id}/events/{event_id}/attendees",
            data=attendee_data,
            params={"user_id_type": "user_id"}
        )

    def update_event(self, calendar_id: str, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update calendar event."""
        return self._call_api("PATCH", f"/calendar/v4/calendars/{calendar_id}/events/{event_id}", data=event_data)

    def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Delete calendar event."""
        self._call_api("DELETE", f"/calendar/v4/calendars/{calendar_id}/events/{event_id}")
        return True

    def get_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        """Get a single calendar event by ID."""
        data = self._call_api("GET", f"/calendar/v4/calendars/{calendar_id}/events/{event_id}")
        return data.get("event", {})

    def search_events(
        self,
        calendar_id: str,
        query: str,
        start_time_ms: Optional[int] = None,
        end_time_ms: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search events in calendar by keyword with optional time range filter.

        Note: Calendar API uses SECONDS; input times are milliseconds.
        """
        body: Dict[str, Any] = {"query": query}
        if start_time_ms is not None and end_time_ms is not None:
            start_sec = start_time_ms // 1000
            end_sec = end_time_ms // 1000
            body["filter"] = {
                "start_time": {"timestamp": str(start_sec)},
                "end_time": {"timestamp": str(end_sec)}
            }
        data = self._call_api("POST", f"/calendar/v4/calendars/{calendar_id}/events/search", data=body)
        return data.get("items", [])

    def query_freebusy(
        self,
        user_ids: List[str],
        start_time_ms: int,
        end_time_ms: int
    ) -> Dict[str, Any]:
        """Query free/busy status for multiple users.

        Note: freebusy API requires RFC 3339 format. Converts ms timestamps to ISO 8601 UTC.
        Returns dict keyed by user_id with freebusy_list per user.
        """
        import datetime
        start_dt = datetime.datetime.utcfromtimestamp(start_time_ms / 1000)
        end_dt = datetime.datetime.utcfromtimestamp(end_time_ms / 1000)
        time_min = start_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        time_max = end_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

        results: Dict[str, Any] = {}
        for user_id in user_ids:
            body = {"time_min": time_min, "time_max": time_max, "user_id": user_id}
            data = self._call_api("POST", "/calendar/v4/freebusy/list", data=body)
            results[user_id] = data.get("freebusy_list", [])
        return results

    def get_attendee_list(self, calendar_id: str, event_id: str) -> List[Dict[str, Any]]:
        """Get all attendees of a calendar event (paginated)."""
        return self._fetch_all(
            f"/calendar/v4/calendars/{calendar_id}/events/{event_id}/attendees",
            params={"user_id_type": "user_id"}
        )

    def delete_attendees(
        self, calendar_id: str, event_id: str, attendee_ids: List[str]
    ) -> bool:
        """Delete attendees from a calendar event by their attendee IDs."""
        self._call_api(
            "POST",
            f"/calendar/v4/calendars/{calendar_id}/events/{event_id}/attendees/batch_delete",
            data={"attendee_ids": attendee_ids}
        )
        return True

    def get_calendar_list(self) -> List[Dict[str, Any]]:
        """Get all calendars accessible by the current identity (paginated).

        Note: Response key is 'calendar_list' not 'items', so _fetch_all not used.
        """
        all_calendars: List[Dict[str, Any]] = []
        params: Dict[str, Any] = {"page_size": 500}
        while True:
            data = self._call_api("GET", "/calendar/v4/calendars", params=params)
            all_calendars.extend(data.get("calendar_list") or [])
            if not data.get("has_more"):
                break
            page_token = data.get("page_token")
            if not page_token:
                break
            params["page_token"] = page_token
        return all_calendars

    def get_calendar(self, calendar_id: str) -> Dict[str, Any]:
        """Get information for a specific calendar."""
        data = self._call_api("GET", f"/calendar/v4/calendars/{calendar_id}")
        return data.get("calendar", data)  # endpoint returns calendar fields directly in data
