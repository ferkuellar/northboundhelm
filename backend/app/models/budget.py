import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.types import GUID


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id"), nullable=False)
    period: Mapped[str] = mapped_column(String(20), nullable=False)
    amount_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    alert_at_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("80.00"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    project = relationship("Project", back_populates="budgets")

