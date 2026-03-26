# Secondary APIs (not implemented as tools)

Endpoints available via raw `_call_api()` but not wrapped as skill methods.
Agent can call these directly when needed using the LarkAPIBase pattern.

## Data Validation (Drop-down Lists)
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /sheets/v2/spreadsheets/:spreadsheetToken/dataValidation | POST | Set drop-down list validation on a range | tenant |
| /sheets/v2/spreadsheets/:spreadsheetToken/dataValidation | GET | Query drop-down list settings for a range | tenant |
| /sheets/v2/spreadsheets/:spreadsheetToken/dataValidation/:sheetId | PUT | Update drop-down list settings | tenant |
| /sheets/v2/spreadsheets/:spreadsheetToken/dataValidation | DELETE | Remove drop-down list from a range | tenant |

## Floating Images
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /sheets/v3/spreadsheets/:spreadsheet_token/sheets/:sheet_id/float_images | POST | Create a floating image on a sheet | tenant |
| /sheets/v3/spreadsheets/:spreadsheet_token/sheets/:sheet_id/float_images/query | GET | List all floating images on a sheet | tenant |
| /sheets/v3/spreadsheets/:spreadsheet_token/sheets/:sheet_id/float_images/:float_image_id | GET | Get a specific floating image | tenant |
| /sheets/v3/spreadsheets/:spreadsheet_token/sheets/:sheet_id/float_images/:float_image_id | PATCH | Update a floating image | tenant |
| /sheets/v3/spreadsheets/:spreadsheet_token/sheets/:sheet_id/float_images/:float_image_id | DELETE | Delete a floating image | tenant |

## Sheet Protection (Locked Ranges)
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /sheets/v2/spreadsheets/:spreadsheetToken/protected_dimension | POST | Lock rows/columns or ranges | tenant |
| /sheets/v2/spreadsheets/:spreadsheetToken/protected_range_batch_get | GET | List all protection scopes | tenant |
| /sheets/v2/spreadsheets/:spreadsheetToken/protected_range_batch_update | POST | Modify protection scopes | tenant |
| /sheets/v2/spreadsheets/:spreadsheetToken/protected_range_batch_del | DELETE | Delete protection scopes | tenant |

## Sheet Copy
| Endpoint | Method | Description | Token |
|---|---|---|---|
| /sheets/v2/spreadsheets/:spreadsheetToken/sheets_batch_update | POST | Copy a sheet within or across spreadsheets (via operate_sheets `copySheet` op) | tenant |
