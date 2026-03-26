"""Lark Base App and Table CRUD operations."""

from lark_api_base import LarkAPIBase


class LarkAppClient(LarkAPIBase):
    """App-level operations: get, create, update, copy."""

    def get_app(self, app_token):
        """Get Base metadata (name, revision, is_advanced)."""
        resp = self._call_api("GET", f"/bitable/v1/apps/{app_token}")
        return resp.get("app", {})

    def create_app(self, name=None, folder_token=None):
        """Create new Base. Returns app_token, name, url.
        Note: auto-creates 1 default table + 5 records."""
        data = {}
        if name:
            data["name"] = name
        if folder_token:
            data["folder_token"] = folder_token
        return self._call_api("POST", "/bitable/v1/apps", data=data)

    def update_app(self, app_token, name=None, is_advanced=None):
        """Update Base metadata. Set is_advanced=True to enable advanced permissions."""
        data = {}
        if name is not None:
            data["name"] = name
        if is_advanced is not None:
            data["is_advanced"] = is_advanced
        return self._call_api("PUT", f"/bitable/v1/apps/{app_token}", data=data)

    def copy_app(self, app_token, name=None, folder_token=None, without_content=False):
        """Copy Base. without_content=True copies structure only."""
        data = {"without_content": without_content}
        if name:
            data["name"] = name
        if folder_token:
            data["folder_token"] = folder_token
        return self._call_api("POST", f"/bitable/v1/apps/{app_token}/copy", data=data)


class LarkTableClient(LarkAPIBase):
    """Table-level CRUD operations."""

    def list_tables(self, app_token, page_size=100):
        """List all tables in Base (paginated)."""
        return self._fetch_all(
            f"/bitable/v1/apps/{app_token}/tables",
            page_size=page_size
        )

    def create_table(self, app_token, name, fields=None):
        """Create table. fields: list of {field_name, type, ui_type?, property?}."""
        data = {"table": {"name": name}}
        if fields:
            data["table"]["fields"] = fields
        return self._call_api(
            "POST", f"/bitable/v1/apps/{app_token}/tables", data=data
        )

    def batch_create_tables(self, app_token, tables):
        """Create multiple tables. tables: list of {name, fields?}."""
        entries = []
        for t in tables:
            entry = {"name": t["name"]}
            if t.get("fields"):
                entry["fields"] = t["fields"]
            entries.append(entry)
        data = {"tables": entries}
        return self._call_api(
            "POST", f"/bitable/v1/apps/{app_token}/tables/batch_create",
            data=data
        )

    def update_table(self, app_token, table_id, name):
        """Rename table."""
        return self._call_api(
            "PATCH", f"/bitable/v1/apps/{app_token}/tables/{table_id}",
            data={"name": name}
        )

    def delete_table(self, app_token, table_id):
        """Delete single table."""
        return self._call_api(
            "DELETE", f"/bitable/v1/apps/{app_token}/tables/{table_id}"
        )

    def batch_delete_tables(self, app_token, table_ids):
        """Delete multiple tables (max 1000)."""
        return self._call_api(
            "POST", f"/bitable/v1/apps/{app_token}/tables/batch_delete",
            data={"table_ids": table_ids}
        )
