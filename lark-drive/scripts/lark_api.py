"""Lark Drive unified client — combines all domain modules via multiple inheritance."""

from lark_api_file import LarkDriveFileClient
from lark_api_upload_download import LarkDriveUploadDownloadClient
from lark_api_permission import LarkDrivePermissionClient
from lark_api_export import LarkDriveExportClient


class LarkDriveClient(
    LarkDriveFileClient,
    LarkDriveUploadDownloadClient,
    LarkDrivePermissionClient,
    LarkDriveExportClient,
):
    """Unified Lark Drive API client. 17 methods across 4 domains.

    Domains:
        File (7):      list_files, get_file_meta, batch_query_meta,
                       create_file, copy_file, move_file, delete_file
        Upload (4):    get_root_folder, create_folder, upload_file, download_file
        Permission (4):search_files, add_permission, update_permission, delete_permission
        Export (2):    export_file, get_export_result

    Usage:
        client = LarkDriveClient(access_token=TOKEN, user_open_id=OPEN_ID)
        root = client.get_root_folder()
        files = client.list_files(folder_token=root["token"])
        ticket = client.export_file(file_token, file_type="docx", export_type="pdf")
        result = client.get_export_result(ticket, file_token)
    """
    pass
