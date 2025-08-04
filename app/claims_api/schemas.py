from pydantic import BaseModel
from typing import Optional
from datetime import date
import strawberry
from typing import List


@strawberry.type
class ClaimType:
    id: int
    claim_number: str
    claimant_name: str
    amount: float
    status: Optional[str]
    date_filed: Optional[date]
    description: Optional[str]
    is_approved: Optional[bool]


@strawberry.type
class ClaimLogType:
    id: int
    claim_id: Optional[int]
    action: str
    message: str
    timestamp: str


@strawberry.type
class Query:
    hello: str = "Hello from GraphQL!"


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


class AgentQuery(BaseModel):
    question: str
