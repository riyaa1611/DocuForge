"""Template database model."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime
from sqlalchemy import Uuid, JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.report import Report
    from app.models.schedule import Schedule


class Template(Base):
    """Report template model."""
    
    __tablename__ = "templates"
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    html_path: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    schema: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Expected data structure for template"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="template"
    )
    schedules: Mapped[List["Schedule"]] = relationship(
        "Schedule",
        back_populates="template"
    )
    
    def __repr__(self) -> str:
        return f"<Template(id={self.id}, name={self.name})>"
