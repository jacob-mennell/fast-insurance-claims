from pydantic import BaseModel
from typing import Optional
from datetime import date
import strawberry
from typing import List


@strawberry.type
class ClaimType:
    """
    Strawberry GraphQL type for a claim.
    Used to expose claim data in GraphQL queries and mutations.
    Mirrors the fields in the Claim Pydantic schema and SQLAlchemy model.
    """

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
    """
    Strawberry GraphQL type for a claim log entry.
    Used to expose claim log data in GraphQL queries.
    Mirrors the fields in the ClaimLog SQLAlchemy model.
    """

    id: int
    claim_id: Optional[int]
    action: str
    message: str
    timestamp: str


@strawberry.type
class Query:
    """
    Root GraphQL query type.
    Used to define top-level query fields for the GraphQL API.
    """

    hello: str = "Hello from GraphQL!"


class ClaimCreate(BaseModel):
    """
    Pydantic schema for creating a new claim.
    Used for request validation when a client submits a new claim.
    Does not include the database-assigned id field.
    """

    claim_number: str
    claimant_name: str
    amount: float
    status: Optional[str] = "pending"
    date_filed: Optional[date] = None
    description: Optional[str] = None
    is_approved: Optional[bool] = False


class Claim(ClaimCreate):
    """
    Pydantic schema for a claim record returned from the database.
    Inherits all fields from ClaimCreate and adds the id field.
    Used for response serialization and validation.
    """

    id: int

    class Config:
        orm_mode = True


class FraudCheckResult(BaseModel):
    """
    Pydantic schema for the fraud check result returned by /agent/check_fraud/{claim_id}.
    """

    claim_id: int
    claim_text: str
    labels: list[str]
    scores: list[float]
    predicted_label: str
    fraud_probability: float


class ClaimLog(BaseModel):
    """
    Pydantic schema for a claim log entry returned by /logs.
    Mirrors the fields in the ClaimLog SQLAlchemy model.
    """

    id: int
    claim_id: Optional[int]
    action: str
    message: str
    timestamp: str


class AgentQuery(BaseModel):
    """
    Pydantic schema for agent natural language queries.
    Used for validating requests to the /agent/query endpoint.
    """

    question: str
