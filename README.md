# FastAPI Insurance Claims API POC

This repository demonstrates a production-friendly FastAPI project for managing insurance claims, with a Streamlit frontend for easy interaction. It uses Poetry for environment management, SQLite for storage, and SQLAlchemy for ORM. The project is modular and easy to extend.

## Project Structure

```
app/
  claims_api/
    ├── main.py          # FastAPI app, endpoints, async support
    ├── models.py        # SQLAlchemy models (define DB schema)
    ├── schemas.py       # Pydantic models (data validation)
    ├── database.py      # DB connection & session
    ├── initialize_agent.py # Agent tools and framework
frontend.py              # Streamlit UI for API interaction
claims.db                # SQLite database (auto-created)
log.txt                  # Claim creation logs
```



## Features
- **FastAPI** for building high-performance APIs
- **Streamlit** frontend for easy, interactive UI
- **SQLite** for lightweight, file-based database
- **SQLAlchemy** ORM for database schema and queries
- **Pydantic** for robust data validation
- **Async operations** for improved performance (see below)
- **Agent Framework** for natural language queries mapped to API tools
- Modular structure for scalability and maintainability



## Getting Started

### 1. Install Poetry
If you don't have Poetry:
```powershell
pip install poetry
```

### 2. Install dependencies (including Streamlit and requests)
```powershell
poetry install
poetry add streamlit requests
```


### 3. Run the FastAPI backend and Streamlit frontend

You need to run both the FastAPI server and the Streamlit app at the same time. Open **two terminals**:

**Terminal 1:** Start the FastAPI backend:
```powershell
poetry run uvicorn app.claims_api.main:app --reload
```

**Terminal 2:** Start the Streamlit frontend:
```powershell
poetry run streamlit run frontend.py
```

> Always start the FastAPI server first, then the Streamlit app. The Streamlit UI will call the API at http://localhost:8000.

### 4. API Docs
Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger UI.


## Endpoints
- `GET /` - Health check
- `POST /claims` - Create a new insurance claim
- `GET /claims` - List all claims (with optional status filter)
- `GET /claims/async` - Async example endpoint
- `GET /claims/{claim_identifier}` - Get a claim by ID or claim number
- `DELETE /claims/{claim_id}` - Delete a claim by ID
- `GET /logs` - View claim logs
- `GET /agent/check_fraud/{claim_id}` - Check if a claim is suspicious/fraudulent


## Streamlit Frontend Pages
- **Submit Claim:** Create a new insurance claim.
- **View All Claims:** View all claims in a table, with refresh.
- **View Logs:** View claim logs in a table, with refresh.
- **Fraud Checker:** Enter a claim ID to check if it is suspicious/fraudulent using an AI model. Displays prediction and probability.
- **Agent Query:** Use natural language to interact with the API tools (e.g., "What is the status of claim 123?").


## How the Setup Works
- **Schema Definition:** The database schema is defined in `models.py` using SQLAlchemy models. When the app starts, `Base.metadata.create_all(bind=engine)` creates the tables in SQLite if they don't exist. If you change the schema, delete `claims.db` and restart the app for changes to take effect (for dev only).
- **Validation:** All request/response data is validated using Pydantic models in `schemas.py`.
- **Async Operations:** FastAPI supports async endpoints for high concurrency. You can define endpoints with `async def` for non-blocking I/O. Example:

    @app.get("/claims/async", response_model=list[schemas.Claim], tags=["Claims"])
    async def get_claims_async(db: Session = Depends(get_db)):
        import asyncio
        await asyncio.sleep(0.1)
        return db.query(models.Claim).all()

- **Logging:** Claim creation events are logged to `log.txt` via a background task.
- **Frontend:** `frontend.py` provides a simple Streamlit UI for creating and viewing claims. Make sure the backend is running before starting Streamlit.
- **Agent Framework:** The `initialize_agent.py` file defines tools and a custom prompt for handling natural language queries mapped to API actions.
- **Modularity:** Each concern (API, models, schemas, DB, frontend) is separated for clarity and maintainability.



## About FastAPI & Pydantic

### What is FastAPI?
FastAPI is a modern, high-performance web framework for building APIs with Python 3.7+ based on standard Python type hints. It is designed for speed, developer productivity, and robust data validation. FastAPI automatically generates interactive API documentation (Swagger UI and ReDoc) and supports asynchronous programming for high concurrency.

**Key FastAPI features:**
- Automatic data validation and serialization using Pydantic models
- Dependency injection system for clean, testable code
- Async support for non-blocking endpoints
- Automatic OpenAPI schema and interactive docs
- Type hints for editor autocompletion and error checking

### Why use Pydantic models?
Pydantic is a data validation and settings management library used by FastAPI to define and validate request and response data. Pydantic models:
- Ensure all incoming and outgoing data matches the expected types and structure
- Provide automatic error messages for invalid data
- Support complex/nested data structures
- Enable code completion and static analysis in editors
- Make your API more robust, secure, and self-documenting

**Example:**
```python
from pydantic import BaseModel

class ClaimCreate(BaseModel):
    claim_number: str
    claimant_name: str
    amount: float
    status: str = "pending"
    # ... other fields ...
```
This model ensures that any data sent to your API for creating a claim is validated and well-structured.

## Benefits of FastAPI
- **Performance:** One of the fastest Python frameworks, on par with NodeJS and Go (thanks to Starlette and async support).
- **Type Safety:** Automatic request validation and editor autocompletion via type hints.
- **Interactive Docs:** Built-in Swagger UI and ReDoc for easy API exploration and testing.
- **Async Support:** Write `async def` endpoints for non-blocking I/O and high concurrency.
- **Easy Integration:** Works seamlessly with SQLAlchemy, Pydantic, and other modern Python tools.
- **Production Ready:** Used by many companies for real-world APIs.

## Troubleshooting
- If you get a 500 Internal Server Error when creating a claim, make sure your database schema matches your models. For dev, delete `claims.db` and restart the backend to recreate the schema.
- If Streamlit or requests are missing, run `poetry add streamlit requests`.
- If you have network issues installing dependencies, try again or check your connection.

---

**Poetry** makes dependency management and packaging easy. See [Poetry docs](https://python-poetry.org/docs/) for more info.
