"""Lark Base unified client — combines all modules via multiple inheritance."""

from lark_api_app_table import LarkAppClient, LarkTableClient
from lark_api_field_view import LarkFieldClient, LarkViewClient
from lark_api_record import LarkRecordClient
from lark_api_permission import LarkRoleClient, LarkRoleMemberClient


class LarkBaseClient(
    LarkAppClient,
    LarkTableClient,
    LarkFieldClient,
    LarkViewClient,
    LarkRecordClient,
    LarkRoleClient,
    LarkRoleMemberClient
):
    """Unified Lark Bitable API client.

    36 methods across 6 domains: App, Table, Field, View, Record, Permission.
    All methods use self._call_api() or self._fetch_all() from LarkAPIBase.

    Usage:
        client = LarkBaseClient(access_token, user_open_id)
        tables = client.list_tables(app_token)
        records = client.list_records(app_token, table_id, filter='...')
    """
    pass
