from __future__ import annotations

from fastapi import HTTPException, status

not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found.",
)

conflict = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Resource already exists.",
)

forbidden = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You do not have permission to perform this action.",
)

unauthorized = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)

bad_request = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid request.",
)
