# Secondary APIs (not implemented as tools)

Endpoints available via raw `_call_api()` but not wrapped as skill methods.
Agent can call these directly when needed using the LarkAPIBase pattern.

## Comments
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /task/v2/comments/:comment_id | DELETE | Delete a task comment | user |
| /task/v2/comments/:comment_id | PATCH | Update a task comment | user |
| /task/v2/comments/:comment_id | GET | Get a single comment by ID | user |

## Task Members & Reminders
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /task/v2/tasks/:task_guid/add_members | POST | Add members to a task | user |
| /task/v2/tasks/:task_guid/remove_members | POST | Remove members from a task | user |
| /task/v2/tasks/:task_guid/remove_reminders | POST | Remove reminders from a task | user |
| /task/v2/tasks/:task_guid/tasklists | GET | List all tasklists a task belongs to | user |

## Task ↔ Tasklist
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /task/v2/tasks/:task_guid/add_tasklist | POST | Add task to a tasklist | user |
| /task/v2/tasks/:task_guid/remove_tasklist | POST | Remove task from a tasklist | user |

## Tasklist Activity Subscriptions
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /task/v2/tasklists/:tasklist_guid/activity_subscriptions | POST | Create activity subscription for a tasklist | user |
| /task/v2/tasklists/:tasklist_guid/activity_subscriptions/:guid | GET | Get an activity subscription | user |
| /task/v2/tasklists/:tasklist_guid/activity_subscriptions/:guid | PATCH | Update an activity subscription | user |
| /task/v2/tasklists/:tasklist_guid/activity_subscriptions/:guid | DELETE | Delete an activity subscription | user |

## Custom Field Options
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /task/v2/custom_fields/:custom_field_guid/options | POST | Create an option for a custom field | user |
| /task/v2/custom_fields/:custom_field_guid/options/:option_guid | PATCH | Update a custom field option | user |
