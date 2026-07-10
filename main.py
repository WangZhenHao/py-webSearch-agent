from dotenv import load_dotenv
import os

load_dotenv()

def main():
    print(f"Hello from py-websearch-agent! {os.getenv('PY_OPENAI_API_KEY')}")


if __name__ == "__main__":
    main()
