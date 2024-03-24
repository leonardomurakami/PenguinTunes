"""
Module Documentation: SQLAlchemy ORM Models

This module defines ORM (Object-Relational Mapping) models using SQLAlchemy for database operations.

Class Descriptions:
- The module uses SQLAlchemy's DeclarativeBase to define ORM classes that represent database tables. 
  These classes provide a high-level, object-oriented interface to interact with corresponding 
  tables in a database.

1. Base(DeclarativeBase)
   - A base class for all ORM models in this module. 
   - Inherits from `DeclarativeBase` provided by SQLAlchemy.
   - Serves as a foundation for defining SQLAlchemy ORM models.

2. Guild(Base)
   Represents a guild (server) in the context of a Discord bot.
   
   Attributes:
    - __tablename__: Specifies the name of the database table.
        - "guilds": Name of the table in the database.
    - id (Mapped[int]): A primary key column representing the guild's ID.
        - Uses BigInteger type for larger numerical capacity.
    - prefix (Mapped[str]): A column representing the command prefix for the guild.
        - Uses String type with a maximum length of 30 characters.
        - Defaults to "p!" if not specified.

    Methods:
    - __repr__(self) -> str
        - Overrides the default representation method.
        - Returns a formatted string representation of the Guild instance, including its id and prefix.
    
    Additional Notes:
    - The Guild class is mapped to the 'guilds' table in the database.
    - The `id` attribute is marked as the primary key, ensuring each Guild instance corresponds to a unique record in the table.
    - Default values can be set for certain columns, as demonstrated with the `prefix` attribute.
    - This structure allows for easy retrieval, update, and management of guild-related data in the context of a Discord bot using the SQLAlchemy ORM.
"""

import datetime
from sqlalchemy import DateTime, ForeignKey, String, BigInteger, Integer, BOOLEAN, JSON, BIGINT, TIMESTAMP, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class Guild(Base):
    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    prefix: Mapped[str] = mapped_column(String(30), default="p!")

    def __repr__(self) -> str:
        """
        - Overrides the default representation method.
        - Returns a formatted string representation of the Guild instance, including its id and prefix.
        """
        return f"User(id={self.id!r}, prefix={self.prefix!r})"

class Cassino(Base):
    __tablename__ = "cassino"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    balance: Mapped[int] = mapped_column(Integer, default=1000)
    slot_wins: Mapped[int] = mapped_column(Integer, default=0)
    blackjack_wins: Mapped[int] = mapped_column(Integer, default=0)
    roulette_wins: Mapped[int] = mapped_column(Integer, default=0)
    video_poker_wins: Mapped[int] = mapped_column(Integer, default=0)
    dig_trash_wins: Mapped[int] = mapped_column(Integer, default=0)
    money_won: Mapped[int] = mapped_column(Integer, default=0)
    money_lost: Mapped[int] = mapped_column(Integer, default=0)
    last_daily: Mapped[datetime.datetime] = mapped_column(DateTime, default=None)

    def __repr__(self) -> str:
        """
        - Overrides the default representation method.
        - Returns a formatted string representation of the Guild instance, including its id and prefix.
        """
        return f"User(id={self.id!r}, money={self.balance!r}, slot_wins={self.slot_wins!r}, blackjack_wins={self.blackjack_wins!r}, money_won={self.money_won!r}, money_lost={self.money_lost!r})"

class PersistentValues(Base):
    __tablename__ = "persistent_values"
    name: Mapped[str] = mapped_column(String(30), primary_key=True)
    value: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        """
        - Overrides the default representation method.
        - Returns a formatted string representation of the Guild instance, including its id and prefix.
        """
        return f"User(name={self.name!r}, value={self.value!r})"
    

class Job(Base):
    __tablename__ = 'jobs'

    job_id = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    job_name = mapped_column(String(255), nullable=False)
    interval_seconds = mapped_column(BIGINT, nullable=False)
    last_run = mapped_column(TIMESTAMP, default=text("CURRENT_TIMESTAMP"))
    config = mapped_column(JSON)
    enabled = mapped_column(BOOLEAN, nullable=False, default=text("TRUE"))

    def __repr__(self) -> str:
        return (f"Job(job_id={self.job_id!r}, job_name={self.job_name!r}, "
                f"interval_seconds={self.interval_seconds!r}, last_run={self.last_run!r}, "
                f"config={self.config!r}, enabled={self.enabled!r})")
    

class Command(Base):
    __tablename__ = 'commands'
    command_id = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    guild_id = mapped_column(BIGINT, nullable=False)
    command_name = mapped_column(String(255), nullable=False)
    __table_args__ = (UniqueConstraint('guild_id', 'command_name'),)


class CommandRestriction(Base):
    __tablename__ = 'command_restrictions'
    restriction_id = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    command_id = mapped_column(BIGINT, ForeignKey('commands.command_id'), nullable=False)
    restriction_type = mapped_column(String(50), nullable=False)
    restriction_target = mapped_column(BIGINT, nullable=False)
    __table_args__ = (UniqueConstraint('command_id', 'restriction_type', 'restriction_target'),)