"""User database model."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, DateTime
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.report import Report
    from app.models.schedule import Schedule


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    reports: Mapped[List["Report"]] = relationship(
        "Report", back_populates="user", cascade="all, delete-orphan"
    )
    schedules: Mapped[List["Schedule"]] = relationship(
        "Schedule", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
