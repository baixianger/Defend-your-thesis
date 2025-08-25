import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from typing import cast
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from src.prompts import questions_prompt, answer_prompt
from src.states import InterviewState, QueryState
from src.utils import format_docs
from src.store import get_store
    
def retrieve_document(state: QueryState):
    store = get_store(state.store_id)
    retriever = store.as_retriever(search_kwargs={'k': 2})
    response = retriever.invoke(input=state.query)
    return {"documents": response}

def web_search_openai(state: QueryState):
    # TODO: use openai web search tool, but it only give the text, not the original search result
    client = OpenAI()

    response = client.responses.create(
        model="gpt-4.1",
        tools=[{
            "type": "web_search_preview",
        "search_context_size": "low",
    }],
    input=state.query,
    )
    return {"documents": [Document(page_content=response.output_text, metadata={"type": "openai_web_search"})]} 


def web_search_tavily(state: QueryState):
    tavily_search = TavilySearchResults(max_results=2)
    search_docs = tavily_search.invoke(state.query) # 搜索网络

    # turn it into document
    documents = []
    for doc in search_docs:
        metadata = {
            "url": doc["url"],
            "title": doc["title"],
            "type": "tavily_web_search"
        }
        documents.append(Document(page_content=doc["content"], metadata=metadata))
    return {"documents": documents}

def answer_question(state: QueryState):
    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2)
    chain = answer_prompt | model
    response = chain.invoke({
        "language": state.language,
        "question": state.query,
        "documents": format_docs(state.documents),
    })
    result = {
        "name": state.name,
        "query": state.query,
        "documents": state.documents,
        "answer": response.content,
        "language": state.language,
    }
    return cast(QueryState, result)


builder = StateGraph(QueryState)
builder.add_node("retrieve_document", retrieve_document)
builder.add_node("web_search_tavily", web_search_tavily)
builder.add_node("answer_question", answer_question)
builder.add_edge(START, "retrieve_document")
builder.add_edge(START, "web_search_tavily")
builder.add_edge("retrieve_document", "answer_question")
builder.add_edge("web_search_tavily", "answer_question")
builder.add_edge("answer_question", END)
query_graph = builder.compile()
query_graph.name = "QueryGraph"



def call_query_graph(state: QueryState):
    query_result = query_graph.invoke(state)
    return {"query_results": [query_result]}

def generate_questions(state: InterviewState):
    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2)
    chain = questions_prompt | model
    question_sets = []
    for examiner in state.examiners:
        response = chain.invoke({
            "language": state.language,
            "max_questions": state.max_questions,
            "examiner": examiner,
            "script": state.script,
        }) 
        for question in response.get("questions", []):
            question_sets.append({"question": question, "questioner": examiner.name})
    return {"question_sets": question_sets}

def conduct_interview(state: InterviewState):
    return [
        Send(
            node="call_query_graph",
            arg={
                "name": question_set["questioner"],
                "query": question_set["question"],
                "language": state.language,
                "store_id": state.store_id,
            }
        )
        for question_set in state.question_sets
    ]


builder = StateGraph(InterviewState)
builder.add_node("generate_questions", generate_questions)
builder.add_node("call_query_graph", call_query_graph)
builder.add_edge(START, "generate_questions")
builder.add_conditional_edges("generate_questions", conduct_interview, ["call_query_graph"])
builder.add_edge("call_query_graph", END)
interview_graph = builder.compile()
interview_graph.name = "InterviewGraph"
