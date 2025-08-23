import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from typing import cast
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send, interrupt, Command
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from src.states import ExaminerState, ExaminersState, Examiner, ExaminersOutput
from src.prompts import persona_prompt_with_input

def create_examiner(state: ExaminerState):
    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2)
    chain = persona_prompt_with_input | model
    
    if state.human_feedback and state.examiner:
        response = chain.invoke({
            "language": state.language, 
            "user_input": state.user_input, 
            "human_feedback": state.human_feedback,
            "previous_version": state.examiner
        })
    else:
        response = chain.invoke({
            "language": state.language, 
            "user_input": state.user_input,
            "human_feedback": "",
            "previous_version": ""
        })
    
    return {"examiner": cast(Examiner, response)}


def human_feedback(state: ExaminerState):
    print("---human_feedback---")
    # TODO: implement human feedback in a map-reduce
    feedback = interrupt("Please provide feedback, if not, leave blank:")
    return {"human_feedback": feedback}

def should_continue(state: ExaminerState):
    if state.human_feedback == "":
        return END
    return "create_examiner"


builder = StateGraph(ExaminerState)
builder.add_node("create_examiner", create_examiner)
builder.add_node("human_feedback", human_feedback)
builder.add_edge(START, "create_examiner")
builder.add_edge("create_examiner", "human_feedback")
builder.add_conditional_edges("human_feedback", should_continue, ["create_examiner", END])
examiner_graph = builder.compile()
examiner_graph.name = "ExaminerGenerationGraph"

def call_examiner_graph(state: ExaminerState):
    examiner = examiner_graph.invoke(state).get("examiner", None)
    return {"examiners": [examiner]}

def create_examiner_in_parallel(state: ExaminersState):
    return [
      Send(
        node = "call_examiner_graph",
        arg={
          "user_input": user_input,
          "language": state.language,
        }
      )
      for user_input in state.user_inputs
    ]


builder = StateGraph(ExaminersState, output_schema=ExaminersOutput)
builder.add_node("call_examiner_graph", call_examiner_graph)
builder.add_conditional_edges(START, create_examiner_in_parallel, ["call_examiner_graph"])
builder.add_edge("call_examiner_graph", END)
examiners_graph = builder.compile()
examiners_graph.name = "ExaminersGenerationGraph"
