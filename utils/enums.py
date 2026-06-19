from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    PRACTICE_ADMIN = "practice_admin"
    CODER = "coder"
    RECEPTIONIST = "receptionist"
    STAFF = "staff"


class DocumentCategory(str, enum.Enum):
    CLINICAL_LETTERS = "clinical_letters"
    REFERRALS = "referrals"
    LAB_RESULTS = "lab_results"
    PRESCRIPTIONS = "prescriptions"
    DISCHARGE_SUMMARIES = "discharge_summaries"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskCategory(str, enum.Enum):
    ADMINISTRATIVE = "administrative"
    CLINICAL = "clinical"
    BILLING = "billing"
    FOLLOW_UP = "follow_up"
    REFERRAL = "referral"
    OTHER = "other"
