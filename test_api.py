import requests
import json
import os
from dotenv import load_dotenv

API_URL = "http://localhost:8000"
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY not found in .env file.")
HEADERS = {"X-API-Key": API_KEY}


def test_health():
    resp = requests.get(f"{API_URL}/", headers=HEADERS)
    print("Health:", resp.status_code, resp.json())


def test_graphql_claims():
    # Query all claims
    query = """
    query {
      claims {
        id
        claimNumber
        claimantName
        amount
        status
      }
    }
    """
    resp = requests.post(
        f"{API_URL}/graphql",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"query": query},
    )
    print("GraphQL Claims:", resp.status_code, resp.json())


def test_graphql_claim_by_id(claim_id):
    query = f"""
    query {{
      claims(id: {claim_id}) {{
        id
        claimNumber
        claimantName
        amount
        status
      }}
    }}
    """
    resp = requests.post(
        f"{API_URL}/graphql",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"query": query},
    )
    print(f"GraphQL Claims Filtered By ID {claim_id}:", resp.status_code, resp.json())


def test_graphql_invalid_query():
    query = """
    query {
      nonExistentField {
        id
      }
    }
    """
    resp = requests.post(
        f"{API_URL}/graphql",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"query": query},
    )
    print("GraphQL Invalid Query:", resp.status_code, resp.text)


def main():
    test_health()
    test_graphql_claims()
    test_graphql_claim_by_id(6)
    test_graphql_invalid_query()


if __name__ == "__main__":
    main()
