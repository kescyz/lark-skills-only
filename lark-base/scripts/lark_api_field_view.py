"""Lark Base Field and View operations."""

from lark_api_base import LarkAPIBase


class LarkFieldClient(LarkAPIBase):
    """Field-level CRUD. 26+ field types with property config."""

    def list_fields(self, app_token, table_id, page_size=100):
        """List all fields in table (max 300 per table)."""
        return self._fetch_all(
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
            page_size=page_size
        )

    def create_field(self, app_token, table_id, field_name, field_type,
                     ui_type=None, description=None, property=None):
        """Create field. type: int (1=Text, 2=Number, 3=SingleSelect, etc.).
        See utils.py FIELD_* constants for all type codes."""
        data = {"field_name": field_name, "type": field_type}
        if ui_type:
            data["ui_type"] = ui_type
        if description:
            data["description"] = description
        if property:
            data["property"] = property
        return self._call_api(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
            data=data
        )

    def update_field(self, app_token, table_id, field_id, field_name,
                     field_type, ui_type=None, description=None, property=None):
        """Update field (full replace). Must include all desired properties."""
        data = {"field_name": field_name, "type": field_type}
        if ui_type:
            data["ui_type"] = ui_type
        if description:
            data["description"] = description
        if property:
            data["property"] = property
        return self._call_api(
            "PUT",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}",
            data=data
        )

    def delete_field(self, app_token, table_id, field_id):
        """Delete field. Cannot delete primary field."""
        return self._call_api(
            "DELETE",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}"
        )


class LarkViewClient(LarkAPIBase):
    """View-level CRUD. Types: grid, kanban, gallery, gantt, form."""

    def list_views(self, app_token, table_id, page_size=100):
        """List all views in table (max 200)."""
        return self._fetch_all(
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/views",
            page_size=page_size
        )

    def get_view(self, app_token, table_id, view_id):
        """Get view details (name, type, property)."""
        return self._call_api(
            "GET",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/views/{view_id}"
        )

    def create_view(self, app_token, table_id, view_name, view_type):
        """Create view. view_type: grid, kanban, gallery, gantt, form."""
        return self._call_api(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/views",
            data={"view_name": view_name, "view_type": view_type}
        )

    def update_view(self, app_token, table_id, view_id, view_name):
        """Rename view."""
        return self._call_api(
            "PATCH",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/views/{view_id}",
            data={"view_name": view_name}
        )

    def delete_view(self, app_token, table_id, view_id):
        """Delete view. Cannot delete last view in table."""
        return self._call_api(
            "DELETE",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/views/{view_id}"
        )
