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
