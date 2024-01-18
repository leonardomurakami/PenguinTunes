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

from sqlalchemy import String, BigInteger
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
