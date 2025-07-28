from langchain.agents import tool
import requests
import os
import toml
from fastapi.security import APIKeyHeader


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
API_BASE_URL = "http://localhost:8000"


@tool
def get_claim_status(claim_id: int | str) -> str:
    """Fetches the status of a claim by its ID.

    Args:
        claim_id (int | str): The unique identifier of the claim. Can be an integer or a string that can be converted to an integer.

    Returns:
        str: The status of the claim or an error message if the claim is not found or the ID is invalid.
    """
    try:
        claim_id = int(claim_id)  # Ensure claim_id is an integer
    except ValueError:
        return "Invalid claim ID. Please provide a valid integer."

    headers = {API_KEY_NAME: API_KEY}
    response = requests.get(f"{API_BASE_URL}/claims/{claim_id}", headers=headers)
    if response.status_code == 404:
        return f"Claim {claim_id} not found."
    return response.json()


@tool
def create_claim(data: dict | str) -> str:
    """Creates a new insurance claim.

    Args:
        data (dict | str): The claim details as a dictionary or a JSON string. The dictionary should include fields like 'claim_number', 'claimant_name', 'amount', etc.

    Returns:
        str: A success message with the created claim details or an error message if the creation fails.
    """
    if isinstance(data, str):
        try:
            import json

            data = json.loads(data)  # Parse the string into a dictionary
        except json.JSONDecodeError:
            return "Invalid data format. Please provide a valid dictionary."

    # Validate required fields
    required_fields = ["claim_number", "claimant_name", "amount"]
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"

    # Ensure 'amount' is a valid number
    try:
        data["amount"] = float(data["amount"])
    except ValueError:
        return "Invalid amount. Please provide a valid number."

    headers = {API_KEY_NAME: API_KEY}
    response = requests.post(f"{API_BASE_URL}/claims", json=data, headers=headers)
    if response.status_code != 201:
        return f"Failed to create claim: {response.text}"
    return response.json()


@tool
def check_claim_fraud(claim_id: int) -> str:
    """Checks if a claim is fraudulent.

    Args:
        claim_id (int): The unique identifier of the claim to check for fraud.

    Returns:
        str: The fraud analysis result or an error message if the claim is not found.
    """
    headers = {API_KEY_NAME: API_KEY}
    response = requests.get(
        f"{API_BASE_URL}/agent/check_fraud/{claim_id}", headers=headers
    )
    if response.status_code == 404:
        return f"Claim {claim_id} not found."
    return response.json()


@tool
def get_claim(claim_id: int | str) -> str:
    """Fetches a claim by its ID.

    Args:
        claim_id (int | str): The unique identifier of the claim. Can be an integer or a string that can be converted to an integer.

    Returns:
        str: The claim details or an error message if the claim is not found.
    """
    try:
        claim_id = int(claim_id)  # Ensure claim_id is an integer
    except ValueError:
        return "Invalid claim ID. Please provide a valid integer."

    headers = {API_KEY_NAME: API_KEY}
    response = requests.get(f"{API_BASE_URL}/claims/{claim_id}", headers=headers)
    if response.status_code == 404:
        return f"Claim {claim_id} not found."
    return response.json()
