"""Formatting helpers for lark-contacts output."""

from typing import Dict, Any, List, Optional


def format_user_summary(user: Dict[str, Any]) -> str:
    """One-line summary: Name (dept_count depts) - job_title - email"""
    name = user.get("name") or user.get("en_name") or user.get("open_id", "Unknown")
    dept_ids = user.get("department_ids", [])
    dept_str = f"({len(dept_ids)} dept{'s' if len(dept_ids) != 1 else ''})" if dept_ids else ""
    job_title = user.get("job_title", "")
    email = user.get("enterprise_email") or user.get("email", "")

    parts = [name]
    if dept_str:
        parts[0] = f"{name} {dept_str}"
    if job_title:
        parts.append(job_title)
    if email:
        parts.append(email)
    return " - ".join(parts)


def format_department_tree(departments: List[Dict[str, Any]], indent: int = 0) -> str:
    """Flat department list → indented tree string for display.

    Builds tree by parent_department_id linkage.
    Departments without a parent in the list are treated as roots.
    """
    if not departments:
        return "(no departments)"

    # Index by open_department_id
    by_id: Dict[str, Dict] = {}
    for d in departments:
        did = d.get("open_department_id") or d.get("department_id", "")
        by_id[did] = d

    # Build children map
    children: Dict[str, List[str]] = {k: [] for k in by_id}
    roots: List[str] = []

    for did, dept in by_id.items():
        parent = dept.get("parent_department_id", "")
        if parent and parent in by_id:
            children[parent].append(did)
        else:
            roots.append(did)

    lines: List[str] = []

    def _render(dept_id: str, level: int) -> None:
        dept = by_id[dept_id]
        prefix = "  " * level + ("- " if level > 0 else "")
        name = dept.get("name", dept_id)
        member_count = dept.get("member_count")
        count_str = f" [{member_count} members]" if member_count is not None else ""
        lines.append(f"{prefix}{name}{count_str}")
        for child_id in sorted(children.get(dept_id, [])):
            _render(child_id, level + 1)

    for root_id in roots:
        _render(root_id, indent)

    return "\n".join(lines)


def format_org_chart(dept_members_map: Dict[str, List[Dict[str, Any]]]) -> str:
    """Department → users map → formatted org chart string.

    dept_members_map: {dept_name: [user_dict, ...]}
    """
    if not dept_members_map:
        return "(empty org chart)"

    lines: List[str] = []
    for dept_name, members in dept_members_map.items():
        lines.append(f"[{dept_name}] ({len(members)} members)")
        for user in members:
            summary = format_user_summary(user)
            lines.append(f"  - {summary}")
        lines.append("")

    return "\n".join(lines).rstrip()
