"""
Shared Lark API base client with retry logic and pagination.
Token provided externally via MCP (no internal auth management).
Uses urllib for HTTP (avoids curl subprocess token truncation with long JWTs).
Messenger-specific: includes _upload_multipart for multipart/form-data file uploads
(images, files) which still use curl -F as urllib does not natively support multipart.
"""

import json
import os
import subprocess
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

    def _upload_multipart(self, endpoint: str, file_path: str,
                          form_fields: Dict[str, str] = None,
                          file_field_name: str = "file") -> Dict[str, Any]:
        """Upload via multipart/form-data (curl -F). field_name: 'image' or 'file'.
        Uses curl because urllib does not natively support multipart/form-data."""
        url = f"{self.BASE_URL}{endpoint}"
        cmd = ["curl", "-s", "-X", "POST", url,
               "-H", f"Authorization: Bearer {self.access_token}"]
        if form_fields:
            for key, value in form_fields.items():
                cmd += ["-F", f"{key}={value}"]
        fname = os.path.basename(file_path)
        cmd += ["-F", f"{file_field_name}=@{file_path};filename={fname}"]

        for attempt in range(3):
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                if attempt < 2:
                    time.sleep(1 * (attempt + 1))
                    continue
                raise Exception(f"Upload failed: {result.stderr}")
            try:
                response = json.loads(result.stdout)
            except json.JSONDecodeError:
                if attempt < 2:
                    time.sleep(1 * (attempt + 1))
                    continue
                raise Exception(f"Non-JSON response: {result.stdout[:200]}")
            # Rate limit retry
            if response.get("code") == 1254290 and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            if response.get("code") != 0:
                raise Exception(f"Lark upload error: {response.get('msg')}")
            return response.get("data", {})
        raise Exception("Upload max retries exceeded")
