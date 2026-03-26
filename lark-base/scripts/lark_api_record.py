"""Lark Base Record CRUD with batch operations."""

from lark_api_base import LarkAPIBase


class LarkRecordClient(LarkAPIBase):
    """Record-level CRUD. Batch create max 500, update/delete max 1000.
    All batch ops are all-or-nothing: one bad record fails entire batch."""

    def list_records(self, app_token, table_id, view_id=None, filter=None,
                     sort=None, field_names=None, page_size=100,
                     automatic_fields=False):
        """List records with optional filter/sort.
        filter: formula syntax e.g. 'CurrentValue.[Status]="Active"'
        sort: JSON string e.g. '[{"field_name":"Name","desc":false}]'
        field_names: JSON string of field names to return."""
        params = {"page_size": page_size}
        if view_id:
            params["view_id"] = view_id
        if filter:
            params["filter"] = filter
        if sort:
            params["sort"] = sort
        if field_names:
            params["field_names"] = field_names
        if automatic_fields:
            params["automatic_fields"] = "true"
        return self._fetch_all(
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records",
            params=params, page_size=page_size
        )

    def get_record(self, app_token, table_id, record_id):
        """Get single record by ID."""
        return self._call_api(
            "GET",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        )

    def create_record(self, app_token, table_id, fields):
        """Create single record. fields: dict of field_name -> value."""
        return self._call_api(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records",
            data={"fields": fields}
        )

    def batch_create_records(self, app_token, table_id, records,
                             client_token=None):
        """Create up to 500 records. All-or-nothing semantics.
        records: list of {"fields": {...}} dicts.
        client_token: UUID for idempotent retry."""
        params = {}
        if client_token:
            params["client_token"] = client_token
        return self._call_api(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
            data={"records": records},
            params=params if params else None
        )

    def update_record(self, app_token, table_id, record_id, fields):
        """Update single record. Only specified fields are changed."""
        return self._call_api(
            "PUT",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
            data={"fields": fields}
        )

    def batch_update_records(self, app_token, table_id, records):
        """Update up to 1000 records.
        records: list of {"record_id": ..., "fields": {...}}."""
        return self._call_api(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update",
            data={"records": records}
        )

    def delete_record(self, app_token, table_id, record_id):
        """Delete single record."""
        return self._call_api(
            "DELETE",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        )

    def batch_delete_records(self, app_token, table_id, record_ids):
        """Delete up to 1000 records."""
        return self._call_api(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete",
            data={"records": record_ids}
        )
