from typing import TypedDict

from dotenv import load_dotenv
import os
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

load_dotenv()


def _make_api_request(url, **kwargs):
    api_key = os.getenv("PY_BRIGHTDATA_API_KEY")
    headers = {
        'Authorization': f'Bearer {api_key}',
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, headers=headers, **kwargs)
        response.raise_for_status()
        print(f"API response: {response.status_code}")
        print(f"Raw body: {response.text[:500]!r}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except Exception as e:
        print(f"Unknown error: {e}")
        return None


def seach_web(query, engine='bing'):
    if (engine == 'bing'):
        base_url = 'https://www.bing.com/search'
        spe = 'q'
    elif (engine == 'google'):
        base_url = 'https://www.google.com/search'
        spe = 'q'
    # elif (engine == 'baidu'):
    #     base_url = 'https://www.baidu.com/s'
    #     spe = 'wd'
    else:
        raise ValueError('Invalid search engine')

    url = 'https://api.brightdata.com/request'

    payload = {
        "zone": "learn_agent",
        "url": f"{base_url}?{spe}={quote_plus(query)}&brd_json=1",
        "format": "raw",
    }

    full_response = _make_api_request(url, json=payload)

    if not full_response:
        return None

    extract_data = {
        "knowledge": full_response.get("knowledge", {}),
        "organic": full_response.get("organic", [])
    }
    print(full_response.get("organic", []))
    return extract_data


def retrieval_post(urls: list[str]) -> list[PageData]:
    if not urls:
        return None

    posts = []

    for url in urls:
        post = fetch_title_and_body(url)
        if post:
            posts.append(post)

    return posts

class PageData(TypedDict):
    title: str
    content: str
def fetch_title_and_body(url: str) -> PageData | None:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    try:
           # 1. 发送请求获取页面
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding  # 自动检测编码，防止乱码
        response.raise_for_status()  # 如果状态码不是200，抛出异常

        # 2. 解析HTML
        soup = BeautifulSoup(response.text, 'lxml')  # 用lxml解析器，速度更快

        # 3. 提取标题
        title = soup.title.string.strip() if soup.title else "无标题"

        # 4. 提取正文文字（去除所有HTML标签）
        # 注意：这会拿到整个body的所有文本，包括导航栏、侧边栏等
        body_text = soup.body.get_text(
            separator='\n', strip=True) if soup.body else ""

        return {"title": title, "content": body_text}

    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


if __name__ == "__main__":
    # seach_web('深圳光明游玩攻略')
    result = fetch_title_and_body('https://zhuanlan.zhihu.com/p/644317130')
    print(result)
