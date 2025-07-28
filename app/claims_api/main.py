"""
main.py - FastAPI entry point for Insurance Claims API

Features:
- CRUD endpoints for insurance claims
- Async endpoint example
- Query parameter filtering
- Custom exception handler
- Background and verbose logging (file and DB)
- Health check and logs endpoints
"""

# --- Imports ---
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    BackgroundTasks,
    Query,
    Request,
    Security,
)
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from transformers import pipeline
import threading
import toml
import os
from . import models, schemas
from .database import SessionLocal, engine, Base
from .initialize_agent import agent


# --- App and Database Setup ---
Base.metadata.create_all(bind=engine)


# Load API key from environment variable (for Azure) or secrets.toml (for local dev)
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    SECRETS_PATH = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "..", ".streamlit", "secrets.toml"
        )
    )
    if os.path.exists(SECRETS_PATH):
        secrets = toml.load(SECRETS_PATH)
        API_KEY = secrets["api"]["API_KEY"]
    else:
        raise FileNotFoundError(
            f"API_KEY not found in environment and .streamlit/secrets.toml not found at {SECRETS_PATH}. Please set one."
        )

# Define API key header for security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# API Key dependency
def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")


# Create FastAPI app with title and version
app = FastAPI(
    title="Insurance Claims API with SQLite",
    version="2.0.0",
    dependencies=[Depends(get_api_key)],
)


@app.post("/agent/query", tags=["Agent"])
def query_agent(request: schemas.AgentQuery):
    """Handle natural language queries and map them to API tools."""
    try:
        response = agent.run(request.question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Utility Classes & Functions ---


# Custom exception for not found claims
class ClaimNotFound(Exception):
    """Custom exception for missing claims."""

    def __init__(self, claim_id: int):
        self.claim_id = claim_id


@app.exception_handler(ClaimNotFound)
async def claim_not_found_handler(request: Request, exc: ClaimNotFound):
    """Return a custom 404 error for missing claims."""
    return JSONResponse(
        status_code=404,
        content={"detail": f"Claim with id {exc.claim_id} not found (custom handler)"},
    )


# Dependency to get DB session
def get_db():
    """Yield a SQLAlchemy session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Logging functions
def log_claim_creation(claim_number: str, db: Session = None):
    """Log claim creation to file and (optionally) to the claim_logs DB table."""
    # Log to file
    with open("log.txt", mode="a") as log:
        log.write(f"Claim created: {claim_number}\n")
    # Verbose log to DB
    if db is not None:
        claim = (
            db.query(models.Claim)
            .filter(models.Claim.claim_number == claim_number)
            .first()
        )
        log_entry = models.ClaimLog(
            claim_id=claim.id if claim else None,
            action="create",
            message=f"Claim created: {claim_number}",
        )
        db.add(log_entry)
        db.commit()


# --- Fraud Detection Model Setup ---
# This uses a free local model for fraud detection.
# Hugging Face zero-shot classification pipeline
# None at start to load only when needed
_fraud_classifier = None

# This ensures that the model is loaded only once and is thread-safe.
_fraud_lock = threading.Lock()


def get_fraud_classifier():
    """Get the zero-shot classification model for fraud detection."""
    """This function initialises the model only once and is thread-safe."""
    global _fraud_classifier
    with _fraud_lock:
        if _fraud_classifier is None:
            _fraud_classifier = pipeline(
                "zero-shot-classification", model="facebook/bart-large-mnli"
            )
        return _fraud_classifier


# --- API Endpoints ---


@app.get("/", tags=["Health"])
def root():
    return {"message": "SQLite-backed Insurance Claims API is running!"}


@app.post("/claims", response_model=schemas.Claim, status_code=201, tags=["Claims"])
def create_claim(
    claim: schemas.ClaimCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    db_claim = models.Claim(**claim.dict())
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    # Log to file and DB
    background_tasks.add_task(log_claim_creation, db_claim.claim_number, db)
    return db_claim


@app.get("/claims", response_model=list[schemas.Claim], tags=["Claims"])
def get_claims(
    status: str = Query(
        None, description="Filter by claim status (e.g. pending, approved)"
    ),
    db: Session = Depends(get_db),
):
    query = db.query(models.Claim)
    if status:
        query = query.filter(models.Claim.status == status)
    return query.all()


@app.get("/claims/async", response_model=list[schemas.Claim], tags=["Claims"])
async def get_claims_async(
    db: Session = Depends(get_db),
):
    import asyncio

    await asyncio.sleep(0.1)  # Simulate async work
    return db.query(models.Claim).all()


@app.get("/claims/{claim_identifier}", response_model=schemas.Claim, tags=["Claims"])
def get_claim(claim_identifier: str, db: Session = Depends(get_db)):
    """
    Fetch a claim by its ID (integer) or claim number (string).

    Args:
        claim_identifier (str): The unique identifier of the claim, either an integer ID or a string claim number.

    Returns:
        schemas.Claim: The claim details or a 404 error if not found.
    """
    # Try to interpret the identifier as an integer (claim_id)
    try:
        claim_id = int(claim_identifier)
        claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    except ValueError:
        # If not an integer, treat it as a claim_number
        claim = (
            db.query(models.Claim)
            .filter(models.Claim.claim_number == claim_identifier)
            .first()
        )

    if claim is None:
        raise ClaimNotFound(claim_identifier)

    return claim


@app.get("/logs", tags=["Logs"])
def get_logs(db: Session = Depends(get_db)):
    """Return all claim logs as a list of dicts for the frontend."""
    logs = db.query(models.ClaimLog).all()
    # Convert SQLAlchemy objects to dicts for JSON serialization
    return [
        {
            "id": log.id,
            "claim_id": log.claim_id,
            "action": log.action,
            "message": log.message,
            "timestamp": str(log.timestamp),
        }
        for log in logs
    ]


@app.get(
    "/agent/check_fraud/{claim_id}",
    tags=["Agent"],
    summary="Check if a claim is suspicious/fraudulent using a free local model.",
)
def check_fraudulent_claim(
    claim_id: int,
    db: Session = Depends(get_db),
):
    """
    Uses a zero-shot classification model to check if a claim is suspicious/fraudulent.
    Returns a probability score and label.
    """
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Prepare claim text (customize as needed)
    claim_text = f"Claimant: {claim.claimant_name}, Amount: {claim.amount}, Status: {claim.status}, Description: {getattr(claim, 'description', '')}"
    classifier = get_fraud_classifier()
    labels = ["fraudulent", "not fraudulent"]
    result = classifier(claim_text, labels)
    # Return the result with scores
    return {
        "claim_id": claim_id,
        "claim_text": claim_text,
        "labels": result["labels"],
        "scores": result["scores"],
        "predicted_label": result["labels"][0],
        "fraud_probability": result["scores"][0],
    }
