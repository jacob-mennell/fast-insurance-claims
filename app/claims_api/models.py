from sqlalchemy import Column, Integer, String, Float, Date, Boolean, Text
from datetime import date
from .database import Base


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_number = Column(String, unique=True, index=True, nullable=False)
    claimant_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    date_filed = Column(Date, default=date.today)
    description = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=False)


# Verbose logging table
class ClaimLog(Base):
    __tablename__ = "claim_logs"
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(Date, default=date.today)
