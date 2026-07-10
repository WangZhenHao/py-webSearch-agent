from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
from typing import Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict

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
    select_google_url: list[str] | None
    google_post_data: list | None
    google_analyze: str | None

    bing_result: str | None
    select_bing_url: list[str] | None
    bing_post_data: list | None
    bing_analyze: str | None

    final_answer: str | None


def googel_search(state: State):
    return {"google_result": "google"}

def bing_search(state: State):
    return {"bing_result": "bing"}

def analyze_googel_urls(state: State):
    return {"select_google_url": "google_analyze"}

def retrieve_googel_post(state: State):
    return {"google_post_data": "google_urls"}

def analyze_googel_result(state: State):
    return {"google_analyze": "google_result"}

def analyze_bing_urls(state: State):
    return {"select_bing_url": "bing_analyze"}

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
            "select_google_url": None,
            "google_post_data": None,
            "google_analyze": None,
            "bing_result": None,
            "select_bing_url": None,
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
