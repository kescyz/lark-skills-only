# Secondary APIs (not implemented as tools)

Endpoints available via raw `_call_api()` but not wrapped as skill methods.
Agent can call these directly when needed using the LarkAPIBase pattern.

## Message Management
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /im/v1/messages/:message_id | PUT | Edit (update content of) a sent message | tenant |
| /im/v1/messages/merge_forward | POST | Merge-forward multiple messages to a chat | tenant |
| /im/v1/threads/:thread_id/forward | POST | Forward an entire thread to another chat | tenant |
| /im/v1/messages/:message_id/resources/:file_key | GET | Download resource file embedded in a message | tenant |

## Batch Messages
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /im/v1/batch_messages/:batch_message_id | DELETE | Recall a batch message | tenant |
| /im/v1/batch_messages/:batch_message_id/get_progress | GET | Query overall send progress of a batch message | tenant |
| /im/v1/batch_messages/:batch_message_id/read_user | GET | Query pushers/readers of a batch message | tenant |

## Buzz (Urgent) Messages
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /im/v1/messages/:message_id/urgent_app | PATCH | Send an in-app buzz (urgent notification) | tenant |

## Ephemeral (Visible-to-one) Cards
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /ephemeral/v1/send | POST | Send a message card visible only to specific users | tenant |
| /ephemeral/v1/delete | POST | Delete an ephemeral card message | tenant |

## Delayed Card Update
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /interactive/v1/card/update | POST | Delay-update a message card (token-based, no message_id) | tenant |

## Message Reactions
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /im/v1/messages/:message_id/reactions/:reaction_id | DELETE | Remove a reaction from a message | tenant |

## Pins
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /im/v1/pins/:message_id | DELETE | Unpin a pinned message | tenant |
| /im/v1/pins | GET | List all pinned messages in a chat | tenant |

## Media Downloads
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /im/v1/images/:image_key | GET | Download an image by its key | tenant |
| /im/v1/files/:file_key | GET | Download a file by its key | tenant |

## Group Tabs
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /im/v1/chats/:chat_id/chat_tabs | POST | Add tabs to a group chat | tenant |
| /im/v1/chats/:chat_id/chat_tabs/delete_tabs | DELETE | Delete group chat tabs | tenant |
| /im/v1/chats/:chat_id/chat_tabs/list_tabs | GET | List all tabs in a group chat | tenant |
| /im/v1/chats/:chat_id/chat_tabs/update_tabs | POST | Update group chat tab info | tenant |
| /im/v1/chats/:chat_id/chat_tabs/sort_tabs | POST | Reorder group chat tabs | tenant |

## Group Menus
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /im/v1/chats/:chat_id/menu_tree | POST | Add menu items to a group chat | tenant |
| /im/v1/chats/:chat_id/menu_tree | DELETE | Delete group chat menu items | tenant |
| /im/v1/chats/:chat_id/menu_tree | GET | Get all menu items of a group chat | tenant |
| /im/v1/chats/:chat_id/menu_items/:menu_item_id | PATCH | Update a specific menu item | tenant |
| /im/v1/chats/:chat_id/menu_tree/sort | POST | Reorder group chat menu items | tenant |

## Group Announcements
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /im/v1/chats/:chat_id/announcement | GET | Get group announcement content | tenant |
| /im/v1/chats/:chat_id/announcement | PATCH | Update group announcement | tenant |

## Group Admins & Speech Moderation
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /im/v1/chats/:chat_id/managers/add_managers | POST | Set users as group admins | tenant |
| /im/v1/chats/:chat_id/managers/delete_managers | POST | Remove group admin role from users | tenant |
| /im/v1/chats/:chat_id/moderation | GET | Get group member speech scopes | tenant |
| /im/v1/chats/:chat_id/moderation | PUT | Update group member speech scopes | tenant |
| /im/v1/chats/:chat_id/link | POST | Get a shareable group invite link | tenant |
