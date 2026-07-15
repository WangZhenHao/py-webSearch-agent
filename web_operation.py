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
        # print(f"API response: {response.status_code}")
        # print(f"Raw body: {response.text[:500]!r}")
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
    # print(full_response.get("organic", []))
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
        "Cookie": '__snaker__id=gn88a72rq0EuAEjD; SESSIONID=PUPKPdQVyGef8aMeVoNzSkhoagGgFLWnVSpxuMLhyu4; JOID=UlkQBEysnpB9iUtxEz6qjeBQUfEK1MrTFMEwDUTBruFJ4S0yfeygxRCPTncRq7g2G-jx0fZ9auzi4F9ppLB-Fho=; osd=W1oRA0qlnZF6j0JyEjmshONRVvcD18vUEsgzDEPHp-JI5is7fu2nwxmMT3AXors3HO740vd6bOXh4VhvrbN_ERw=; _xsrf=ZqExGqEcx52EY78lTvGDigV5RibeXvY3; _zap=5b503055-3368-490f-8198-0448a5b3f0a3; d_c0=_KWVckGkFByPTj3InPllXxRZYKKsJ5GhgG4=|1775201573; HMACCOUNT=C890BE31151146F5; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1781699140,1782441163,1782816748; DATE=1775201583011; crystal=U2FsdGVkX1+lOKJNVnfsJd6oKDFUmL9nNNHmQcWWHvmUiF6mix2CCFdoJN6ivj7kMzzTZMqgRjdZwJG8W9L2MQo59fn3/Dvc7T+EqUvjnJYwDo9hsZ6fL+ibrjbseNBulQ8mQhOZ4vyq5mOKHfUVjP2wkCN/YkbUKSgJEshg2QgL/8WOG5u8UDpQsWgTzY56cl7dvE9xCIETxje0j3ml6QzNn29/IvJFkKwb2M2xmTm98BvARfHAXyuV9lZLaqyg; __zse_ck=005_=IF1GD6vuMtsS0lhg9q4riBeW1yuUNI6N6po0zD6Oqo9w6idahXOqbaOCmPONoI5TPJsUGuNSHXG=IwzdD2imqF4mGrcbuuF8dAcyF2Op0dkiAcWb5l4eyvNmhFtqO7X-KGhzhsI03vUN/OenjKCTAglztprtH94k24gEKlfMzAwJwMPktqafvRhKnbJXTHAq2kywE+AyHaNNCPsaUjm6pjI/6lhgr9giBODfh5feUJU4Cx6GdXoAKv4xI/ZqduAuLhlD1HY5r6KWQUr4k8mY1pZpRKSFheSYkmPMz32bEoI=; BEC=63a638605a4496c28946ef33c98c124a; captcha_session_v2=2|1:0|10:1784100929|18:captcha_session_v2|88:Q1lmVnhuejF5ajgrNlczSGUvMVc1V0srb1crQmlnSzEwU1o1a2NqUjZ1ellBaEVDSXBJaGRENXBBU0hSbUNKNA==|254b482d9660decf6b3085c8422104d8edd591beee411d94aff2f3c53b7684b1; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1784100931; assva6=U2FsdGVkX1+YJQkwVvGnACiNJbzWe9LAW2SgD64Ol2g=; assva5=U2FsdGVkX19u9isEb0DCFSMvLkqo2via35eJ/XodYT2risqmiYWGZXzCNbnnyx8xpJBKCioQWFeNoMxjLWKmfg==; gdxidpyhxdE=k247Zo10A%2FRX1Rp5vsy5MuAoQVHYT00vjlpO1%2BgKVWs%5CWCzdgNRQgN16fq%5CgLQOVNLKNVV6RUrI5gSKdaBbsgRNXnovE44NVVI4y%5C83V%5CKNMgtNZ6VORbDueItIJC5K%5CBgJys4OElGqobiwV4soo4qfWhxsXEqVwbAj03xlDxZj7w9PH%3A1784101833871; cmci9xde=U2FsdGVkX19mQP1dY3vkkMDfjWC8gP8EzIWlqpaDAYKYSqq3hxz7+z1QNIkbAqJ7MxQl8Yy332y5DXhO7XDGLQ==; pmck9xge=U2FsdGVkX1/TIBN0WyHuTGhJAQWY2RGdTuAEQz6JhOc=; vmce9xdq=U2FsdGVkX1+suT1eaaKvLD+uSu0PiM9dj7iJofb6acEL+Wzmmr8A36k7ekcrOKRUf2PqBFOc0KKq73UDLGh0jzTFXz86oKTKs/nF71LwM39HqgM025loKyWFP8ryycukqmkw6jHPrTv9o34jx6Rikop/SUhfuhiCMpZ8oTmt/fo='
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
        print(f"请求失败: {url}")
        return None


if __name__ == "__main__":
    seach_web('深圳光明游玩攻略')
    # result = fetch_title_and_body('https://zhuanlan.zhihu.com/p/644317130')
    # print(result)
