import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from typing import cast
from langgraph.graph import START, END, StateGraph
from langchain_openai import ChatOpenAI
from src.states import GraphState, OutputState
from src.presentation import presentation_graph
from src.examiners import examiners_graph
from src.interviews import interview_graph
from src.prompts import report_prompt


def generate_report(state: GraphState):
    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2)
    chain = report_prompt | model
    response = chain.invoke({
        "script": state.script,
        "slides": state.outline,
        "examiners": "\n".join([examiner.persona for examiner in state.examiners]),
        "qas": "\n".join([qa.qa for qa in state.query_results]),
    })
    return {"report": response.content}

def generate_QA(state: GraphState):
    return {"QA": "\n\n---\n\n".join([qa.qa for qa in state.query_results])}

builder = StateGraph(state_schema=GraphState, output_schema=OutputState)
builder.add_node("presentation", presentation_graph)
builder.add_node("examiners", examiners_graph)
builder.add_node("interview", interview_graph)
builder.add_node("generate_report", generate_report)
builder.add_node("generate_QA", generate_QA)
builder.add_edge(START, "presentation")
builder.add_edge(START, "examiners")
builder.add_edge("examiners", "interview")
builder.add_edge("presentation", "interview")
builder.add_edge("interview", "generate_report")
builder.add_edge("interview", "generate_QA")
builder.add_edge("generate_QA", END)
builder.add_edge("generate_report", END)

defend_graph = builder.compile()
defend_graph.name = "DefendGraph"
