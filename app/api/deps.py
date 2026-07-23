from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.blc.auth import AuthService
from app.api.blc.document import DocumentService
from app.api.blc.otp_delivery import EmailOtpDeliveryService, MailjetOtpDeliveryService, OtpDeliveryService
from app.api.blc.practice import PracticeService
from app.api.blc.task import TaskService
from app.api.blc.task_category import TaskCategoryService
from app.api.blc.task_priority import TaskPriorityService
from app.api.blc.user import UserService
from app.api.queries.document import DocumentRepository
from app.api.queries.password_reset_otp import PasswordResetOtpRepository
from app.api.queries.practice import PracticeRepository
from app.api.queries.task import TaskRepository
from app.api.queries.task_category import TaskCategoryRepository
from app.api.queries.task_priority import TaskPriorityRepository
from app.api.queries.user import UserRepository
from app.core.config import Settings, get_settings
from app.core.db_session import get_db

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_user_repository(session: DbSessionDep) -> UserRepository:
    return UserRepository(session)


def get_practice_repository(session: DbSessionDep) -> PracticeRepository:
    return PracticeRepository(session)


def get_password_reset_otp_repository(
    session: DbSessionDep,
) -> PasswordResetOtpRepository:
    return PasswordResetOtpRepository(session)


def get_otp_delivery_service(settings: SettingsDep) -> OtpDeliveryService:
    import structlog
    _log = structlog.get_logger(__name__)
    if settings.MJ_APIKEY_PUBLIC and settings.MJ_APIKEY_PRIVATE:
        _log.info("otp_delivery_service_selected", provider="mailjet", from_email=settings.MJ_FROM_EMAIL)
        return MailjetOtpDeliveryService(settings)
    _log.warning("otp_delivery_service_selected", provider="smtp", reason="mailjet_credentials_missing")
    return EmailOtpDeliveryService(settings)


def get_auth_service(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    password_reset_otps: Annotated[
        PasswordResetOtpRepository,
        Depends(get_password_reset_otp_repository),
    ],
    otp_delivery: Annotated[OtpDeliveryService, Depends(get_otp_delivery_service)],
    settings: SettingsDep,
) -> AuthService:
    return AuthService(
        users=users,
        password_reset_otps=password_reset_otps,
        otp_delivery=otp_delivery,
        settings=settings,
    )


def get_user_service(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    practices: Annotated[PracticeRepository, Depends(get_practice_repository)],
) -> UserService:
    return UserService(users=users, practices=practices)


def get_task_category_repository(session: DbSessionDep) -> TaskCategoryRepository:
    return TaskCategoryRepository(session)


def get_task_priority_repository(session: DbSessionDep) -> TaskPriorityRepository:
    return TaskPriorityRepository(session)


def get_practice_service(
    practices: Annotated[PracticeRepository, Depends(get_practice_repository)],
) -> PracticeService:
    return PracticeService(practices=practices)


def get_task_category_service(
    task_categories: Annotated[TaskCategoryRepository, Depends(get_task_category_repository)],
) -> TaskCategoryService:
    return TaskCategoryService(categories=task_categories)


def get_task_priority_service(
    task_priorities: Annotated[TaskPriorityRepository, Depends(get_task_priority_repository)],
) -> TaskPriorityService:
    return TaskPriorityService(priorities=task_priorities)


def get_document_repository(session: DbSessionDep) -> DocumentRepository:
    return DocumentRepository(session)


def get_document_service(
    documents: Annotated[DocumentRepository, Depends(get_document_repository)],
    practices: Annotated[PracticeRepository, Depends(get_practice_repository)],
    tasks: Annotated[TaskRepository, Depends(get_task_repository)],
) -> DocumentService:
    return DocumentService(documents=documents, practices=practices, tasks=tasks)


def get_task_repository(session: DbSessionDep) -> TaskRepository:
    return TaskRepository(session)


def get_task_service(
    tasks: Annotated[TaskRepository, Depends(get_task_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
    task_categories: Annotated[TaskCategoryRepository, Depends(get_task_category_repository)],
    task_priorities: Annotated[TaskPriorityRepository, Depends(get_task_priority_repository)],
    documents: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> TaskService:
    return TaskService(
        tasks=tasks,
        users=users,
        task_categories=task_categories,
        task_priorities=task_priorities,
        documents=documents,
    )
