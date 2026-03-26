"""
Shared Lark API base client with retry logic and pagination.
Token provided externally via MCP (no internal auth management).
Uses urllib for HTTP (avoids curl subprocess token truncation with long JWTs).
"""

import json
import time
import urllib.request
import urllib.error
from urllib.parse import urlencode
from typing import Optional, Dict, Any, List


class LarkAPIBase:
    """Base client for Lark APIs. Provides HTTP, retry, and pagination."""

    BASE_URL = "https://open.larksuite.com/open-apis"

    def __init__(
        self,
        access_token: str,
        user_open_id: str,
        user_id: str = None
    ):
        self.access_token = access_token
        self.user_open_id = user_open_id
        self.user_id = user_id

    def _call_api(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Call Lark API with auto-retry and rate limit handling."""
        url = f"{self.BASE_URL}{endpoint}"

        if params:
            url += f"?{urlencode(params, doseq=True)}"

        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = None
        if data:
            headers["Content-Type"] = "application/json"
            body = json.dumps(data).encode()

        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, data=body, headers=headers, method=method)
                with urllib.request.urlopen(req) as resp:
                    response = json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                error_body = e.read().decode()
                try:
                    response = json.loads(error_body)
                except (json.JSONDecodeError, ValueError):
                    if attempt < max_retries - 1:
                        time.sleep(1 * (attempt + 1))
                        continue
                    raise Exception(f"API call failed: HTTP {e.code} {error_body[:200]}")
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))
                    continue
                raise Exception(f"API call failed: {e}")

            if response.get("code") == 1254290:
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue

            if response.get("code") != 0:
                raise Exception(f"Lark API error: {response.get('msg')}")

            return response.get("data") or {}

        raise Exception("Max retries exceeded")

    def _fetch_all(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        page_size: int = 50
    ) -> List[Dict[str, Any]]:
        """Fetch all items from paginated endpoint."""
        all_items = []
        page_params = dict(params) if params else {}
        page_params["page_size"] = page_size

        while True:
            data = self._call_api("GET", endpoint, params=page_params)
            items = data.get("items") or []
            all_items.extend(items)

            if not data.get("has_more"):
                break

            page_token = data.get("page_token")
            if not page_token:
                break
            page_params["page_token"] = page_token

        return all_items
