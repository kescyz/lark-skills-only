# Secondary APIs (not implemented as tools)

Endpoints available via raw `_call_api()` but not wrapped as skill methods.
Agent can call these directly when needed using the LarkAPIBase pattern.

## User Management
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /contact/v3/users/:user_id/resurrect | POST | Restore a deleted user | tenant |

## Department Management
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /contact/v3/departments/parent | GET | Get parent department chain for a department | both |
| /contact/v3/departments/unbind_department_chat | POST | Convert department group to a regular group chat | tenant |

## User Groups
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /contact/v3/group | POST | Create a user group | tenant |
| /contact/v3/group/:group_id | PATCH | Update a user group | tenant |
| /contact/v3/group/:group_id | DELETE | Delete a user group | tenant |
| /contact/v3/group/:group_id | GET | Get user group details | tenant |
| /contact/v3/group/simplelist | GET | List all user groups (simplified) | tenant |
| /contact/v3/group/:group_id/member/batch_add | POST | Batch add members to a user group | tenant |
| /contact/v3/group/:group_id/member/batch_remove | POST | Batch remove members from a user group | tenant |

## Workforce Types
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /contact/v3/employee_type_enums | POST | Create a workforce type enum | tenant |
| /contact/v3/employee_type_enums/:enum_id | PUT | Update a workforce type enum | tenant |
| /contact/v3/employee_type_enums/:enum_id | DELETE | Delete a workforce type enum | tenant |
| /contact/v3/employee_type_enums | GET | List all workforce type enums | tenant |

## Roles
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /contact/v3/functional_roles | POST | Create a role | tenant |
| /contact/v3/functional_roles/:role_id | DELETE | Delete a role | tenant |
| /contact/v3/functional_roles/:role_id | PATCH | Update a role name | tenant |

## Role Members
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /contact/v3/functional_roles/:role_id/members/batch_create | POST | Batch add members to a role | tenant |
| /contact/v3/functional_roles/:role_id/members/scopes | PATCH | Batch update role member admin scopes | tenant |
| /contact/v3/functional_roles/:role_id/members/batch_delete | PATCH | Remove members from a role | tenant |
| /contact/v3/functional_roles/:role_id/members | GET | List all members under a role | tenant |
| /contact/v3/functional_roles/:role_id/members/:member_id | GET | Get admin scope of a role member | tenant |
