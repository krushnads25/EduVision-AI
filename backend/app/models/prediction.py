from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.models.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(128), nullable=False)
    target = Column(String(128), nullable=False)
    target_year = Column(Integer, nullable=True, index=True)
    features = Column(JSON, nullable=True)
    predicted_value = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
