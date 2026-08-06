import csv
from datetime import date, datetime
from io import StringIO

from app.models import Project, Task


def _format_datetime(value: datetime | None) -> str:
    return value.isoformat() if value else ""


def _format_date(value: date | None) -> str:
    return value.isoformat() if value else ""


def export_tasks_to_csv(tasks: list[Task]) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Title", "Description", "Status", "Priority",
        "Project ID", "Assignee ID", "Created By ID",
        "Due Date", "Estimated Hours", "Completed At",
        "Created At", "Updated At",
    ])
    for task in tasks:
        writer.writerow([
            str(task.id),
            task.title,
            task.description or "",
            task.status,
            task.priority,
            str(task.project_id),
            str(task.assignee_id) if task.assignee_id else "",
            str(task.created_by_id),
            _format_date(task.due_date),
            task.estimated_hours or "",
            _format_datetime(task.completed_at),
            _format_datetime(task.created_at),
            _format_datetime(task.updated_at),
        ])
    return output.getvalue()


def export_projects_to_csv(projects: list[Project]) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Name", "Description", "Status", "Archived",
        "Owner ID", "Deadline", "Created At", "Updated At",
    ])
    for project in projects:
        writer.writerow([
            str(project.id),
            project.name,
            project.description or "",
            project.status,
            project.is_archived,
            str(project.owner_id),
            _format_date(project.deadline),
            _format_datetime(project.created_at),
            _format_datetime(project.updated_at),
        ])
    return output.getvalue()
