from typing import Dict, Any


class PromptTemplates:
    """搜索助手提示词汇总"""

    @staticmethod
    def google_urls_analyze_user(user_question, search_result) -> str:
        return f"""
        
        用户内容: {user_question}
        
        地址列表结果: {search_result}

        请筛选出用户内容， 分析出最有价值，最相关的连接地址
        """

    @staticmethod
    def google_urls_analyze_system() -> str:
        return """
        你是一个内容分析专家，你需要根据用户输入的关键词，从搜索结果中筛选出最相关的内容

        专注于内容筛选：
        1. 筛选出最相关的内容。
        2. 不少于2个内容。
        3. 不多于10个内容。
        
        返回一个包含url的列表
        """

    @staticmethod
    def google_analysis_system() -> str:
        return """
        你是一个内容分析专家，分析谷歌搜索提供的内容，更具用户的问题提取关键信息

        专注于：
         - 主要事实信息和权威来源
         - 官方网站、文件及可靠来源
         - 关键统计数据、日期和已核实的信息
         - 来自不同来源的相互矛盾/冲突的信息

        请提供一份简明扼要的分析，重点突出最相关的发现。
        """

    @staticmethod
    def google_analysis_user(user_question, search_results) -> str:
        return f"""
          
          用户问题: {user_question}

          谷歌搜索结果: {search_results}

         请分析谷歌搜索的结果，提取出对用户问题最有帮助的内容
        """
    
    @staticmethod
    def bing_analysis_system() -> str:
        return """
        你是一个内容分析专家，分析必应搜索提供的内容，更具用户的问题提取关键信息

        专注于：
         - 主要事实信息和权威来源
         - 官方网站、文件及可靠来源
         - 关键统计数据、日期和已核实的信息
         - 来自不同来源的相互矛盾/冲突的信息

        请提供一份简明扼要的分析，重点突出最相关的发现。
        """

    @staticmethod
    def bing_analysis_user(user_question, search_results) -> str:
        return f"""

          用户问题: {user_question}

          必应搜索结果: {search_results}

         请分析必应搜索的结果，提取出对用户问题最有帮助的内容
        """

    @staticmethod
    def synthesis_system() -> str:
        return """
            **你是一位专家级研究综合者。请将来自不同来源的分析整合在一起，形成一份全面、结构清晰的回答。**

            **你的任务：**
            - 综合来自 Google、Bing分析中的洞见
            - 识别共同主题和相互矛盾的信息
            - 呈现兼顾不同视角的平衡观点
            - 按逻辑组织回答，分段落清晰呈现
            - 对关键主张注明来源类型（Google、Bingt）
            - 突出任何矛盾之处或不确定因素

            **请从多个角度撰写一份全面回答，以回应用户的问题。**
        """
    
    @staticmethod
    def synthesis_user(user_question: str,
        google_analysis: str,
        bing_analysis: str,) -> str:
        return f"""
            **问题：{user_question}

            **Google 分析：{google_analysis}

            **Bing 分析：{bing_analysis}

            **请将以上这些分析综合成一份全面回答，从多个角度回应该问题。**
        """

def create_message_pair(system_prompt: str, user_prompt: str) -> list[Dict[str, Any]]:

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def get_urls_analyze_message(user_question, search_results) -> list[Dict[str, Any]]:
    return create_message_pair(
        PromptTemplates.google_urls_analyze_system(),
        PromptTemplates.google_urls_analyze_user(user_question, search_results)
    )


def get_bing_analyze_message(user_question, search_results) -> list[Dict[str, Any]]:
    return create_message_pair(
        PromptTemplates.bing_analysis_system(),
        PromptTemplates.bing_analysis_user(user_question, search_results)
    )


def get_googel_analyze_message(user_question, search_results) -> list[Dict[str, Any]]:
    return create_message_pair(
        PromptTemplates.google_analysis_system(),
        PromptTemplates.google_analysis_user(user_question, search_results)
    )


def get_synthesis_messages(user_question, googel_result, bing_result) -> str:
    return create_message_pair(
        PromptTemplates.synthesis_system(),
        PromptTemplates.synthesis_user(user_question, googel_result, bing_result)
    )
