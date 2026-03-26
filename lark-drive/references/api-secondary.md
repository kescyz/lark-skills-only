# Secondary APIs (not implemented as tools)

Endpoints available via raw `_call_api()` but not wrapped as skill methods.
Agent can call these directly when needed using the LarkAPIBase pattern.

## Document Versioning
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /drive/v1/files/:file_token/versions | POST | Create a named version of a document | both |
| /drive/v1/files/:file_token/versions | GET | List all versions of a document | both |
| /drive/v1/files/:file_token/versions/:version_id | GET | Get a specific document version | both |
| /drive/v1/files/:file_token/versions/:version_id | DELETE | Delete a document version | both |

## Import Tasks
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /drive/v1/import_tasks | POST | Create an import task (upload local file as Lark doc) | tenant |
| /drive/v1/import_tasks/:ticket | GET | Poll import task result | tenant |

## File Statistics
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /drive/v1/files/:file_token/statistics | GET | Get file view/edit statistics | tenant |

## Media & Thumbnails
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /drive/v1/medias/batch_get_tmp_download_url | GET | Get temporary download URLs for media files | both |

## Event Subscriptions
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /drive/v1/files/:file_token/subscriptions | POST | Subscribe to file change events | both |
| /drive/v1/files/:file_token/subscriptions/:subscription_id | GET | Get subscription status | both |
| /drive/v1/files/:file_token/subscriptions/:subscription_id | PATCH | Update subscription status | both |

## Online Document Creation
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /drive/explorer/v2/file/:folderToken | POST | Create a new online doc/sheet/bitable in a folder | tenant |
