from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.models.base import Base


class AnalyticsCache(Base):
    __tablename__ = "analytics_caches"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(256), nullable=False, unique=True, index=True)
    query_hash = Column(String(128), nullable=True, index=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
