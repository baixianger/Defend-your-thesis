# Create a LANGSMITH_API_KEY in Settings > API Keys
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from langsmith import Client
client = Client()
persona_prompt_with_input = client.pull_prompt("defend-your-thesis-persona", include_model=False)

    