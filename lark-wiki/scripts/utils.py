"""
Lark Wiki constants: object types, node types, member roles.
Used across lark_api_space.py, lark_api_node.py, lark_api_member.py.
"""

# Document/object type identifiers for Wiki nodes
OBJ_TYPE_DOC = "doc"
OBJ_TYPE_SHEET = "sheet"
OBJ_TYPE_MINDNOTE = "mindnote"
OBJ_TYPE_BITABLE = "bitable"
OBJ_TYPE_FILE = "file"
OBJ_TYPE_DOCX = "docx"

# Node type: origin = real node, shortcut = alias pointing to another node
NODE_TYPE_ORIGIN = "origin"
NODE_TYPE_SHORTCUT = "shortcut"

# Space member roles
MEMBER_ROLE_ADMIN = "admin"
MEMBER_ROLE_MEMBER = "member"

# Member type identifiers
MEMBER_TYPE_USER = "userid"
MEMBER_TYPE_EMAIL = "email"
MEMBER_TYPE_OPEN_ID = "openid"
MEMBER_TYPE_UNION_ID = "unionid"
MEMBER_TYPE_DEPARTMENT = "departmentid"
MEMBER_TYPE_CHAT = "openchatid"

# Space setting values
SETTING_ALLOW = "allow"
SETTING_NOT_ALLOW = "not_allow"

# Types that support update_title — sheet/bitable/mindnote do NOT
TITLE_UPDATABLE_TYPES = {"doc", "docx"}
