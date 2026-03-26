"""
Unified Lark Wiki API client — combines all 3 mixin modules.
15 methods: Space (4) + Node (6) + Member/Search/Task (5).

Usage:
    from lark_api import LarkWikiClient
    client = LarkWikiClient(access_token=TOKEN, user_open_id=OPEN_ID)
"""

from lark_api_space import LarkWikiSpaceClient
from lark_api_node import LarkWikiNodeClient
from lark_api_member import LarkWikiMemberClient


class LarkWikiClient(LarkWikiSpaceClient, LarkWikiNodeClient, LarkWikiMemberClient):
    """
    Unified Lark Wiki API client. 15 methods across 3 domains.

    Space (4):  list_spaces, get_space, create_space, update_space_setting
    Node (6):   create_node, get_node, list_nodes, move_node, copy_node, update_title
    Member (5): add_member, delete_member, search_wiki, move_docs_to_wiki, get_task
    """
    pass
