from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os

load_dotenv()

llm = init_chat_model(
    model="gpt-5.4",
    api_key=os.getenv("PY_OPENAI_API_KEY"),
    base_url=os.getenv("PY_OPENAI_BEARER_URL")
)


def main():
    # 调用模型
    response = llm.invoke("你好，请介绍一下自己,是什么模型")
    print(response.content)


if __name__ == "__main__":
    main()
