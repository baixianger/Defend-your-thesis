import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.store import get_document, get_store
from src.prompts import presentation_prompt
from src.states import PresentationState
from langchain_openai import ChatOpenAI

def presentation(state: PresentationState):
    doc = get_document()
    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2)
    chain = presentation_prompt | model
    response = chain.invoke({
        "language": state.language,
        "max_time": state.max_time,
        "thesis": state.thesis.page_content,
    })
    return {
      "script": response.script,
      "outline": response.outline
    }
        
builder = StateGraph(PresentationState)
builder.add_node("presentation", presentation)
builder.add_edge(START, "presentation")
presentation_graph = builder.compile()
presentation_graph.name = "PresentationGraph"