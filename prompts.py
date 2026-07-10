from typing import Dict, Any


class PromptTemplates:
    """搜索助手提示词汇总"""

    @staticmethod
    def urls_analyze_system(user_question, search_result) -> str:
        return """
        你是一个内容分析专家，你需要根据用户输入的关键词，从搜索结果中筛选出最相关的内容

        *****************************
        用户内容: {user_question}
        *****************************
        搜索结果: {search_result}
        *****************************

        专注于内容筛选：
        1. 筛选出最相关的内容。
        2. 不少于2个内容。
        3. 不多于10个内容。
        
        返回一个包含url的列表

        """

    @staticmethod
    def google_analyze_system() -> str:
        return """
        你是一个助手，你需要根据用户输入的关键词，从谷歌搜索结果中筛选出最相关的内容，并给出一个总结。
        请
        """

def create_message_pair(system_prompt: str, user_prompt: str) -> list[Dict[str, Any]]:

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
def get_urls_analyze_message(user_question, search_results) ->list[Dict[str, Any]]:
    return create_message_pair(
        PromptTemplates.urls_analyze_system(),
       

    )