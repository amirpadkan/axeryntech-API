import uuid

from sqlmodel import Session

from app.crud.notification import create_notification
from app.models import NotificationCreate, NotificationType


def notify_task_assigned(session: Session, *, recipient_id: uuid.UUID, task_title: str, task_id: uuid.UUID) -> None:
    create_notification(
        session,
        NotificationCreate(
            recipient_id=recipient_id,
            type=NotificationType.TASK_ASSIGNED,
            title="New task assigned",
            body=f"You have been assigned to task: {task_title}",
            resource_type="task",
            resource_id=task_id,
        ),
    )


def notify_mention(session: Session, *, recipient_id: uuid.UUID, mentioned_by: str, task_title: str, task_id: uuid.UUID) -> None:
    create_notification(
        session,
        NotificationCreate(
            recipient_id=recipient_id,
            type=NotificationType.MENTION,
            title="You were mentioned",
            body=f"{mentioned_by} mentioned you in task: {task_title}",
            resource_type="task",
            resource_id=task_id,
        ),
    )


def notify_deadline_near(session: Session, *, recipient_id: uuid.UUID, task_title: str, task_id: uuid.UUID) -> None:
    create_notification(
        session,
        NotificationCreate(
            recipient_id=recipient_id,
            type=NotificationType.DEADLINE_NEAR,
            title="Deadline approaching",
            body=f"Task \"{task_title}\" is due soon",
            resource_type="task",
            resource_id=task_id,
        ),
    )


def notify_project_invitation(
    session: Session,
    *,
    recipient_id: uuid.UUID,
    project_name: str,
    project_id: uuid.UUID,
    invited_by: str,
) -> None:
    create_notification(
        session,
        NotificationCreate(
            recipient_id=recipient_id,
            type=NotificationType.PROJECT_INVITATION,
            title="Project invitation",
            body=f"{invited_by} invited you to project: {project_name}",
            resource_type="project",
            resource_id=project_id,
        ),
    )
