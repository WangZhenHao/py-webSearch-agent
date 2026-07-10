from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os
from datetime import datetime
from dotenv import load_dotenv
from typing import Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from web_operation import seach_web, retrieval_post

from prompts import get_urls_analyze_message, get_googel_analyze_message, get_synthesis_messages, get_bing_analyze_message

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
    google_post_data: list[str] | None
    google_analyze: str | None

    bing_result: str | None
    select_bing_urls: list[str] | None
    bing_post_data: list[str] | None
    bing_analyze: str | None

    final_answer: str | None


class PostUrlAnalyze(BaseModel):
    select_urls: list[str] = Field(description='和用户问题有很强关联的网页链接')


def googel_search(state: State):
    user_question = state["user_question"]
    print(f"谷歌搜索问题: {user_question}")

    google_result = seach_web(user_question, engine='google')

    if not google_result:
        google_result = "找不到结果"

    return {"google_result": google_result}


def bing_search(state: State):
    user_question = state["user_question"]
    print(f"必应搜索问题: {user_question}")

    bing_result = seach_web(user_question, engine='bing')

    if not bing_result:
        bing_result = "找不到结果"

    return {"bing_result": bing_result}


def analyze_googel_urls(state: State):
    user_question = state["user_question"]
    google_result = state["google_result"] or ''

    if not google_result:
        return []

    print(f"正在分析文章地址...")
    strctured_llm = llm.with_structured_output(PostUrlAnalyze)
    messages = get_urls_analyze_message(user_question, google_result)

    try:
        analyze_result = strctured_llm.invoke(messages)
        selected_urls = analyze_result.select_urls
        print(f"成功选择{len(selected_urls)}文章")
    except Exception as e:
        print(f"错误: {e}")
        selected_urls = []

    return {"select_google_urls": selected_urls}


def retrieve_googel_post(state: State):
    google_urls = state["select_google_urls"] or []

    if (len(google_urls)):
        print(f"正在谷歌处理{len(google_urls)} 个搜索内容...")
    google_post_data = retrieval_post(google_urls)

    if google_post_data:
        print(f"成功处理谷歌{len(google_post_data)}搜索内容")
    else:
        google_post_data = []

    return {"google_post_data": google_post_data}


def analyze_googel_result(state: State):
    print("正在分析谷歌搜索的结果...")
    user_question = state["user_question"]
    google_post_data = state["google_post_data"]

    messages = get_googel_analyze_message(user_question, google_post_data)
    reply = llm.invoke(messages)

    return {"google_analyze": reply.content}


def analyze_bing_urls(state: State):
    user_question = state["user_question"]
    bing_result = state["bing_result"] or ''

    if not bing_result:
        return []

    print(f"正在分析必应文章地址...")
    strctured_llm = llm.with_structured_output(PostUrlAnalyze)
    messages = get_urls_analyze_message(user_question, bing_result)

    try:
        analyze_result = strctured_llm.invoke(messages)
        selected_urls = analyze_result.select_urls
        print(f"成功选择{len(selected_urls)}文章")
    except Exception as e:
        print(f"必应分析错误: {e}")
        selected_urls = []

    return {"select_bing_urls": selected_urls}


def retrieve_bing_post(state: State):
    bing_urls = state["select_bing_urls"] or []

    if (len(bing_urls)):
        print(f"正在必应处理{len(bing_urls)} 个搜索内容...")
    bing_post_data = retrieval_post(bing_urls)

    if bing_post_data:
        print(f"成功处理必应{len(bing_post_data)}搜索内容")
    else:
        bing_post_data = []
    return {"bing_post_data": bing_post_data}


def analyze_bing_result(state: State):
    print("正在分析必应搜索的结果...")
    user_question = state["user_question"]
    bing_post_data = state["bing_post_data"]

    messages = get_bing_analyze_message(user_question, bing_post_data)
    reply = llm.invoke(messages)

    return {"bing_analyze": reply.content}


def generationMd(content: str):
    if not content: return

    dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
    os.makedirs(dist_dir, exist_ok=True)

    filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".md"
    filepath = os.path.join(dist_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"已生成文件: {filepath}")
    return filepath


def systhesize_analyze(state: State):
    print("整合所有搜索内容....")
    user_question = state["user_question"]
    google_analyze = state["google_analyze"] or ""
    bing_analyze = state["bing_analyze"] or ""

    messages = get_synthesis_messages(
        user_question, google_analyze, bing_analyze
    )

    reply = llm.invoke(messages)
    final_answer = reply.content
    generationMd(final_answer)
    return {"final_answer": final_answer, "messages": [{"role": "assistant", "content": final_answer}]}


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
