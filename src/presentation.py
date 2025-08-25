import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from typing import cast
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from src.store import get_document
from src.prompts import presentation_prompt
from src.states import PresentationState


def presentation(state: PresentationState):
    thesis = get_document(thesis_path=state.thesis_path)
    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2)
    chain = presentation_prompt | model
    response = chain.invoke({
        "language": state.language,
        "max_time": state.max_time,
        "thesis": thesis.page_content,
    })
    result = {
        "script": response.get("script", ""),
        "outline": response.get("outline", ""),
    }
    return cast(PresentationState, result)
        
builder = StateGraph(PresentationState)
builder.add_node("presentation", presentation)
builder.add_edge(START, "presentation")
builder.add_edge("presentation", END)
presentation_graph = builder.compile()
presentation_graph.name = "PresentationGraph"