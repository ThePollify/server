from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, User


class Poll(Base):
    __tablename__ = "polls"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    name: Mapped[str]
    poll: Mapped[dict] = mapped_column(JSON)

    owner: Mapped[User] = relationship(User)
