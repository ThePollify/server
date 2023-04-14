from sqlalchemy import JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, Poll, User


class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    poll_id: Mapped[int] = mapped_column(ForeignKey(Poll.id, ondelete="CASCADE"))
    answerer_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            User.id,
            ondelete="CASCADE",
        )
    )
    answer: Mapped[dict] = mapped_column(JSON)

    poll: Mapped[Poll] = relationship(Poll, lazy="joined")
    answerer: Mapped[User | None] = relationship(User, lazy="joined")

    __table_args__ = (UniqueConstraint(poll_id, answerer_id),)
