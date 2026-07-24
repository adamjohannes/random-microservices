from datetime import datetime
from uuid import UUID
from sqlalchemy import String, ForeignKey, DateTime, Integer, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import List, Optional


class Base(AsyncAttrs, DeclarativeBase):
    pass


# Association table for the Many-to-Many relationship between Courses and Assignees
course_assignees = Table(
    "course_assignees",
    Base.metadata,
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CourseChapterModel(Base):
    __tablename__ = "course_chapters"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    index: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(String(10000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class CourseModel(Base):
    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    author: Mapped[UserModel] = relationship(lazy="joined")
    chapters: Mapped[List[CourseChapterModel]] = relationship(
        cascade="all, delete-orphan",
        order_by="CourseChapterModel.index",
        lazy="selectin",
    )
    assignees: Mapped[List[UserModel]] = relationship(
        secondary=course_assignees,
        lazy="selectin",
    )
