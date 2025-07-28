from langchain.agents import initialize_agent, Tool
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from app.claims_api.agent_tools import (
    get_claim_status,
    create_claim,
    check_claim_fraud,
    get_claim,
)
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the language model
llm = ChatOpenAI(
    temperature=0.7, model="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Define tools for the agent
tools = [
    Tool(
        name="GetClaimStatus",
        func=get_claim_status,
        description="Get the status of a claim by ID.",
    ),
    Tool(
        name="CreateClaim",
        func=create_claim,
        description="Create a new insurance claim.",
    ),
    Tool(
        name="CheckClaimFraud",
        func=check_claim_fraud,
        description="Check if a claim is fraudulent.",
    ),
    Tool(
        name="GetClaim",
        func=get_claim,
        description="Fetch a claim by its ID.",
    ),
]

# Custom prompt with few-shot examples
custom_prompt = PromptTemplate(
    input_variables=["input", "agent_scratchpad"],
    template="""
You are an insurance claims assistant. You can use the tools provided to answer questions about insurance claims. Here are some examples:

Note any ID needs to be a valid integer and therefore the input should not be in quotes.

1. Question: "What is the status of claim ID 123?"
   Response: Use the GetClaimStatus tool with claim_id=123 (ensure claim_id is an integer).

2. Question: "Create a new claim for John Doe with an amount of $500."
   Response: Use the CreateClaim tool with data={"claim_number": "123456", "claimant_name": "John Doe", "amount": 500}.

3. Question: "Is claim 456 fraudulent?"
   Response: Use the CheckClaimFraud tool with claim_id=456 (ensure claim_id is an integer). Provide reasoning for the decision.

4. Question: "Fetch the details of claim ID 789."
   Response: Use the GetClaim tool with claim_id=789 (ensure claim_id is an integer).

Now handle the user's question: {input}
{agent_scratchpad}
""",
)

# Initialize the agent with the custom prompt
agent = initialize_agent(
    tools, llm, agent="zero-shot-react-description", verbose=True, prompt=custom_prompt
)
