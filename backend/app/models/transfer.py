import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TransferStatus(str, enum.Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sender_wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    receiver_wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sent_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    received_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    source_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    target_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(18, 8), nullable=False, default=Decimal("1.00000000")
    )
    status: Mapped[TransferStatus] = mapped_column(
        Enum(TransferStatus),
        nullable=False,
        default=TransferStatus.COMPLETED,
        index=True,
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    sender_wallet = relationship("Wallet", foreign_keys=[sender_wallet_id])
    receiver_wallet = relationship("Wallet", foreign_keys=[receiver_wallet_id])

    def __repr__(self) -> str:
        return f"<Transfer {self.sent_amount} {self.source_currency} -> {self.received_amount} {self.target_currency}>"
