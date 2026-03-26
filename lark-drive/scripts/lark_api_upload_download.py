"""Lark Drive upload/download and folder operations — root, create folder, upload, download."""

import json
import os
import subprocess
from typing import Dict, Any
from lark_api_base import LarkAPIBase


class LarkDriveUploadDownloadClient(LarkAPIBase):
    """Root folder, folder creation, file upload (multipart/form-data), binary download.

    Upload uses curl -F (not JSON) because Lark requires multipart/form-data.
    Download uses curl -o (binary stream) — online docs are NOT downloadable here.
    """

    def get_root_folder(self) -> Dict[str, Any]:
        """Get My Space root folder metadata.

        Returns:
            {token: str, id: str}  — token is the root folder_token
        """
        return self._call_api("GET", "/drive/explorer/v2/root_folder/meta")

    def create_folder(self, name: str, folder_token: str) -> Dict[str, Any]:
        """Create a new folder inside an existing folder.

        Args:
            name: Folder name (max 250 chars).
            folder_token: Parent folder token.

        Returns:
            {token: str, id: str}
        """
        return self._call_api(
            "POST", "/drive/v1/files/create_folder",
            data={"name": name, "folder_token": folder_token}
        )

    def upload_file(
        self,
        file_name: str,
        parent_token: str,
        file_path: str,
        size: int
    ) -> Dict[str, Any]:
        """Upload a file to Drive (max 20 MB). Uses multipart/form-data via curl.

        Args:
            file_name: Name to save the file as (max 250 chars).
            parent_token: Destination folder token.
            file_path: Absolute local path to the file.
            size: File size in bytes (must be accurate, max 20971520).

        Returns:
            {file_token: str}

        Raises:
            ValueError: If file not found or exceeds 20 MB.
            Exception: On API or curl failure.
        """
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        actual_size = os.path.getsize(file_path)
        if size != actual_size:
            raise ValueError(f"size={size} doesn't match actual file size={actual_size}")
        if size > 20 * 1024 * 1024:
            raise ValueError(f"File size {size} bytes exceeds 20 MB limit. Use multipart upload.")

        url = f"{self.BASE_URL}/drive/v1/files/upload_all"
        cmd = [
            "curl", "-s", "-X", "POST", url,
            "-H", f"Authorization: Bearer {self.access_token}",
            "-F", f"file_name={file_name}",
            "-F", "parent_type=explorer",
            "-F", f"parent_node={parent_token}",
            "-F", f"size={size}",
            "-F", f"file=@{file_path}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Upload failed: {result.stderr}")

        response = json.loads(result.stdout)
        if response.get("code") != 0:
            raise Exception(f"Lark upload error: {response.get('msg')} (code={response.get('code')})")

        return response.get("data") or {}

    def download_file(self, file_token: str, save_path: str) -> str:
        """Download a file from Drive to local path (binary stream via curl).

        Only works for uploaded binary files (type=file).
        Online docs (doc/sheet/docx/bitable) are NOT supported — use export instead.

        Args:
            file_token: File token (prefix: box).
            save_path: Absolute local path to write the file.

        Returns:
            save_path on success.

        Raises:
            Exception: On curl failure or API error.
        """
        url = f"{self.BASE_URL}/drive/v1/files/{file_token}/download"
        cmd = [
            "curl", "-s", "-X", "GET", url,
            "-H", f"Authorization: Bearer {self.access_token}",
            "-L",          # follow redirects (Lark may redirect to CDN)
            "-o", save_path,
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exception(f"Download failed: {result.stderr.decode()}")

        # Detect if Lark returned a JSON error instead of binary content
        if os.path.exists(save_path):
            with open(save_path, "rb") as f:
                head = f.read(32)
            if head.startswith(b'{"code"'):
                with open(save_path) as f:
                    err = json.load(f)
                raise Exception(f"Lark download error: {err.get('msg')} (code={err.get('code')})")

        return save_path
