from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
from typing import Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from web_operation import seach_web

load_dotenv()

llm = init_chat_model(
    model="gpt-5.4",
    api_key=os.getenv("PY_OPENAI_API_KEY"),
    base_url=os.getenv("PY_OPENAI_BEARER_URL")
)

class State(TypedDict):
    """State of the graph."""

    messages: Annotated[list, add_messages]
    user_question: str | None

    google_result: str | None
    select_google_urls: list[str] | None
    google_post_data: list | None
    google_analyze: str | None

    bing_result: str | None
    select_bing_urls: list[str] | None
    bing_post_data: list | None
    bing_analyze: str | None

    final_answer: str | None


class PostUrlAnalyze(BaseModel):
    select_urls: list[str] = Field(description='和用户问题有很强关联的网页链接')

def googel_search(state: State):
    user_question = state["user_question"]
    print(f"谷歌搜索问题: {user_question}")

    google_result = seach_web(user_question, engine='google')
    return {"google_result": google_result}

def bing_search(state: State):
    user_question = state["user_question"]
    print(f"必应搜索问题: {user_question}")

    bing_result = seach_web(user_question, engine='bing')
    return {"bing_result": bing_result}

def analyze_googel_urls(state: State):
    user_question = state["user_question"]
    google_result = state["google_result"] or ''

    if not google_result:
        return []

    strctured_llm = llm.with_structured_output(PostUrlAnalyze)

    return {"select_google_urls": "google_analyze"}

def retrieve_googel_post(state: State):
    return {"google_post_data": "google_urls"}

def analyze_googel_result(state: State):
    return {"google_analyze": "google_result"}

def analyze_bing_urls(state: State):
    return {"select_bing_urls": "bing_analyze"}

def retrieve_bing_post(state: State):
    return {"bing_post_data": "bing_urls"}

def analyze_bing_result(state: State):
    return {"bing_analyze": "bing_result"}

def systhesize_analyze(state: State):
    return {"final_answer": "final_answer"}


graph_builder = StateGraph(State)

graph_builder.add_node('google_search', googel_search)
graph_builder.add_node('bing_search', bing_search)

graph_builder.add_node('analyze_googel_urls', analyze_googel_urls)
graph_builder.add_node('retrieve_googel_post', retrieve_googel_post)
graph_builder.add_node('analyze_googel_result', analyze_googel_result)

graph_builder.add_node('analyze_bing_urls', analyze_bing_urls)
graph_builder.add_node('retrieve_bing_post', retrieve_bing_post)
graph_builder.add_node('analyze_bing_result', analyze_bing_result)

graph_builder.add_node('systhesize_analyze', systhesize_analyze)

graph_builder.add_edge(START, 'google_search')
graph_builder.add_edge(START, 'bing_search')

graph_builder.add_edge('google_search', 'analyze_googel_urls')
graph_builder.add_edge('analyze_googel_urls', 'retrieve_googel_post')
graph_builder.add_edge('retrieve_googel_post', 'analyze_googel_result')

graph_builder.add_edge('bing_search', 'analyze_bing_urls')
graph_builder.add_edge('analyze_bing_urls', 'retrieve_bing_post')
graph_builder.add_edge('retrieve_bing_post', 'analyze_bing_result')

graph_builder.add_edge('analyze_googel_result', 'systhesize_analyze')
graph_builder.add_edge('analyze_bing_result', 'systhesize_analyze')

graph_builder.add_edge('systhesize_analyze', END)

graph = graph_builder.compile()

def run_chatbot():
    print('网络搜索智能体')
    print("输入'exit' 退出\n")

    while True:
        user_input = input("请输入查询的问题: ")

        if user_input.lower() == "exit":
            print("退出程序")
            break

        state = {
            "messages": [{"role": "user", "content": user_input}],
            "user_question": user_input,
            "google_result": None,
            "select_google_urls": None,
            "google_post_data": None,
            "google_analyze": None,
            "bing_result": None,
            "select_bing_urls": None,
            "bing_post_data": None,
            "bing_analyze": None,
            "final_answer": None,
        }

        print('\n启动搜索程序...')
        print('启动谷歌，必应 搜索...')

        final_answer = graph.invoke(state)

        if final_answer.get("final_answer"):
            print(f"\n最终答案:\n {final_answer['final_answer']}\n")
            print("*" * 80)
            

def main():
    # 调用模型
     run_chatbot()


if __name__ == "__main__":
    main()
