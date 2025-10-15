# -*- coding: utf-8 -*-

import json
import logging

from api_client import ApiClient
from html_parser import HtmlParser
from config import STANDARDS

# 配置基本的日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def explore_real_data():
    """
    从API获取一个真实的章节，对其进行解析，并打印出结构化的输出。
    这作为一个集成测试，用以验证解析器在处理真实世界数据时的表现。
    """
    logging.info("--- 开始真实数据探索 ---")

    try:
        # 1. 初始化API客户端
        client = ApiClient()

        # 2. 定义目标：混凝土规范的 'notice' 章节
        # 我们使用 'notice' 章节，因为它通常是一个常见且结构简单的起点。
        standard_id = STANDARDS['concrete']['id']
        chapter_id = "notice"

        logging.info(f"尝试获取规范 '{standard_id}' 的章节 '{chapter_id}'...")

        # 3. 从API获取详细的章节数据
        chapter_data = client.get_chapter_detail(standard_id, chapter_id)

        # 4. 提取HTML内容。
        # 根据成功的API响应，内容位于'data'键下。
        html_content = chapter_data.get('data', {}).get('content')

        if not html_content:
            logging.error("在API响应的'data'对象中找不到'content'。")
            logging.error(f"API响应: {json.dumps(chapter_data, indent=2, ensure_ascii=False)}")
            return

        logging.info("成功获取到真实的HTML内容。")
        # 可选：打印原始HTML用于调试
        # print("\n--- 原始HTML ---")
        # print(html_content)

        # 5. 解析真实的HTML内容
        logging.info("使用HtmlParser解析HTML内容...")
        parser = HtmlParser(html_content)
        structured_content = parser.get_structured_content()

        # 6. 打印结构化输出
        logging.info("--- 来自真实数据的结构化内容 ---")
        print(json.dumps(structured_content, indent=2, ensure_ascii=False))

    except Exception as e:
        logging.error(f"在数据探索过程中发生错误: {e}", exc_info=True)
    finally:
        logging.info("--- 真实数据探索结束 ---")

if __name__ == '__main__':
    explore_real_data()
