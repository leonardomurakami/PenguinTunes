from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class Guild(Base):
    __tablename__ = "guilds"

    guild_id: Mapped[int] = mapped_column(primary_key=True)
    prefix: Mapped[str] = mapped_column(String(30), default="p!")

    def __repr__(self) -> str:
        return f"User(guild_id={self.guild_id!r}, prefix={self.prefix!r})"