from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.models.base import Base


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
