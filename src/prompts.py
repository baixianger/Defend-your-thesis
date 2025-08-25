# Create a LANGSMITH_API_KEY in Settings > API Keys
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from langsmith import Client
client = Client()
persona_prompt_with_input = client.pull_prompt("defend-your-thesis-persona", include_model=False)
presentation_prompt = client.pull_prompt("defend-your-thesis-presentation", include_model=False)

questions_prompt = client.pull_prompt("defend-your-thesis-questions", include_model=False)

answer_prompt = client.pull_prompt("defend-your-thesis-answer", include_model=False)

report_prompt = client.pull_prompt("defend-your-thesis-report", include_model=False)
