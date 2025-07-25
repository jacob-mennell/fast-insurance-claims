from pydantic import BaseModel
from typing import Optional


from datetime import date


class ClaimCreate(BaseModel):
    claim_number: str
    claimant_name: str
    amount: float
    status: Optional[str] = "pending"
    date_filed: Optional[date] = None
    description: Optional[str] = None
    is_approved: Optional[bool] = False


class Claim(ClaimCreate):
    id: int

    class Config:
        orm_mode = True
