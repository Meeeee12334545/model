from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, Float, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.session import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(255))
    owner: Mapped[str | None] = mapped_column(String(255))

    sites: Mapped[list["Site"]] = relationship(back_populates="project", cascade="all, delete")


class Site(Base, TimestampMixin):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(100))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    pipe_material: Mapped[str | None] = mapped_column(String(100))
    pipe_diameter_mm: Mapped[float | None] = mapped_column(Float)

    project: Mapped[Project] = relationship(back_populates="sites")
    raw_series: Mapped[list["TimeSeriesRaw"]] = relationship(back_populates="site", cascade="all, delete")
    processed_series: Mapped[list["TimeSeriesProcessed"]] = relationship(back_populates="site", cascade="all, delete")
    rating_curves: Mapped[list["RatingCurve"]] = relationship(back_populates="site", cascade="all, delete")


class TimeSeriesRaw(Base, TimestampMixin):
    __tablename__ = "time_series_raw"
    __table_args__ = (Index("ix_raw_site_timestamp", "site_id", "timestamp"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"))
    parameter: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    value: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(100))
    qc_flag: Mapped[str | None] = mapped_column(String(50))
    record_metadata: Mapped[dict | None] = mapped_column(JSON)

    site: Mapped[Site] = relationship(back_populates="raw_series")


class TimeSeriesProcessed(Base, TimestampMixin):
    __tablename__ = "time_series_processed"
    __table_args__ = (Index("ix_processed_site_timestamp", "site_id", "timestamp"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"))
    source_raw_id: Mapped[int | None] = mapped_column(ForeignKey("time_series_raw.id", ondelete="SET NULL"))
    parameter: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    value: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(50))
    qc_summary: Mapped[str | None] = mapped_column(String(255))
    record_metadata: Mapped[dict | None] = mapped_column(JSON)

    site: Mapped[Site] = relationship(back_populates="processed_series")
    source_raw: Mapped[TimeSeriesRaw | None] = relationship(foreign_keys=[source_raw_id])


class RatingCurve(Base, TimestampMixin):
    __tablename__ = "rating_curves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"))
    curve_type: Mapped[str] = mapped_column(String(100), default="depth-flow")
    coefficients: Mapped[dict] = mapped_column(JSON, default=dict)
    notes: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(100))

    site: Mapped[Site] = relationship(back_populates="rating_curves")
