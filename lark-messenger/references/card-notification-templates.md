# Lark Card Notification Templates

Ready-to-use Card JSON 2.0 templates for common notification scenarios.
Replace `{{placeholder}}` values before sending.

Usage: `client.send_card(chat_id, card_dict)` or `send_webhook(url, "interactive", card_dict)`

---

## 1. Status Notification

**When to use:** System alerts, deployment results, job completion, health checks.
Change `template` to `"green"` (success), `"orange"` (warning), `"red"` (error), `"blue"` (info).

```json
{
  "schema": "2.0",
  "config": { "update_multi": true },
  "header": {
    "title": { "tag": "plain_text", "content": "{{title}}" },
    "template": "blue"
  },
  "body": {
    "elements": [
      { "tag": "markdown", "content": "**Status:** {{status}}" },
      { "tag": "markdown", "content": "**Details:** {{message}}" },
      { "tag": "hr" },
      { "tag": "markdown", "content": "Time: {{timestamp}} | Source: {{source}}" }
    ]
  }
}
```

---

## 2. Approval Request

**When to use:** Leave requests, expense claims, document reviews, access requests.
Buttons use `url` for simple link-based approvals (no callback required).

```json
{
  "schema": "2.0",
  "config": { "update_multi": true },
  "header": {
    "title": { "tag": "plain_text", "content": "Approval Request: {{request_type}}" },
    "template": "yellow"
  },
  "body": {
    "elements": [
      { "tag": "markdown", "content": "**Requester:** {{requester_name}}" },
      { "tag": "markdown", "content": "**Request:** {{request_summary}}" },
      { "tag": "markdown", "content": "**Submitted:** {{submit_time}}" },
      { "tag": "hr" },
      {
        "tag": "column_set",
        "flex_mode": "none",
        "columns": [
          {
            "tag": "column",
            "width": "weighted",
            "weight": 1,
            "elements": [
              {
                "tag": "button",
                "text": { "tag": "plain_text", "content": "Approve" },
                "type": "primary",
                "url": "{{approve_url}}"
              }
            ]
          },
          {
            "tag": "column",
            "width": "weighted",
            "weight": 1,
            "elements": [
              {
                "tag": "button",
                "text": { "tag": "plain_text", "content": "Reject" },
                "type": "danger",
                "url": "{{reject_url}}"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## 3. Alert Card

**When to use:** Incidents, outages, security events, urgent notifications.
Set `template` to `"red"` for critical, `"orange"` for warnings.

```json
{
  "schema": "2.0",
  "config": { "update_multi": true },
  "header": {
    "title": { "tag": "plain_text", "content": "ALERT: {{alert_title}}" },
    "template": "red"
  },
  "body": {
    "elements": [
      { "tag": "markdown", "content": "**Urgency:** {{urgency_level}}" },
      { "tag": "markdown", "content": "**Affected:** {{affected_service}}" },
      { "tag": "markdown", "content": "{{alert_details}}" },
      { "tag": "hr" },
      {
        "tag": "button",
        "text": { "tag": "plain_text", "content": "View Details" },
        "type": "primary",
        "url": "{{action_url}}"
      }
    ]
  }
}
```

---

## 4. Progress Update

**When to use:** Task status reports, project milestones, CI/CD pipeline updates.

```json
{
  "schema": "2.0",
  "config": { "update_multi": true },
  "header": {
    "title": { "tag": "plain_text", "content": "Progress: {{project_name}}" },
    "template": "turquoise"
  },
  "body": {
    "elements": [
      { "tag": "markdown", "content": "**Task:** {{task_name}}" },
      { "tag": "markdown", "content": "**Status:** {{status}}" },
      { "tag": "markdown", "content": "**Progress:** {{percent}}% complete" },
      { "tag": "hr" },
      {
        "tag": "column_set",
        "flex_mode": "bisect",
        "columns": [
          {
            "tag": "column",
            "width": "weighted",
            "weight": 1,
            "elements": [
              { "tag": "markdown", "content": "**Started:** {{start_time}}" }
            ]
          },
          {
            "tag": "column",
            "width": "weighted",
            "weight": 1,
            "elements": [
              { "tag": "markdown", "content": "**ETA:** {{eta}}" }
            ]
          }
        ]
      },
      { "tag": "markdown", "content": "**Notes:** {{notes}}" }
    ]
  }
}
```

---

## 5. Table Summary

**When to use:** Data reports, daily/weekly summaries, metric dashboards.
Each row is a `column_set` with 2 columns (label + value).

```json
{
  "schema": "2.0",
  "config": { "update_multi": true },
  "header": {
    "title": { "tag": "plain_text", "content": "{{report_title}}" },
    "template": "indigo"
  },
  "body": {
    "elements": [
      { "tag": "markdown", "content": "Period: **{{period}}**" },
      { "tag": "hr" },
      {
        "tag": "column_set",
        "flex_mode": "none",
        "columns": [
          {
            "tag": "column", "width": "weighted", "weight": 2,
            "elements": [{ "tag": "markdown", "content": "**Metric**" }]
          },
          {
            "tag": "column", "width": "weighted", "weight": 1,
            "elements": [{ "tag": "markdown", "content": "**Value**" }]
          }
        ]
      },
      { "tag": "hr" },
      { "tag": "column_set", "flex_mode": "none", "columns": [
          { "tag": "column", "width": "weighted", "weight": 2, "elements": [{ "tag": "markdown", "content": "{{row1_label}}" }] },
          { "tag": "column", "width": "weighted", "weight": 1, "elements": [{ "tag": "markdown", "content": "{{row1_value}}" }] }
      ]},
      { "tag": "column_set", "flex_mode": "none", "columns": [
          { "tag": "column", "width": "weighted", "weight": 2, "elements": [{ "tag": "markdown", "content": "{{row2_label}}" }] },
          { "tag": "column", "width": "weighted", "weight": 1, "elements": [{ "tag": "markdown", "content": "{{row2_value}}" }] }
      ]},
      { "tag": "column_set", "flex_mode": "none", "columns": [
          { "tag": "column", "width": "weighted", "weight": 2, "elements": [{ "tag": "markdown", "content": "{{row3_label}}" }] },
          { "tag": "column", "width": "weighted", "weight": 1, "elements": [{ "tag": "markdown", "content": "{{row3_value}}" }] }
      ]},
      { "tag": "hr" },
      { "tag": "markdown", "content": "Generated at {{generated_at}}" }
    ]
  }
}
```

---

> Header color reference: see `card-json-v2-building-guide.md` → Header Colors table.
