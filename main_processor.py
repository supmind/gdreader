# -*- coding: utf-8 -*-

import json
import logging
import time
from typing import List, Dict, Any

# 导入我们自己开发的模块
from api_client import ApiClient
from html_parser import HtmlParser, ContentBlock
from ai_processor import AiProcessor
from prompts import FORMULA_OCR_PROMPT, TABLE_TRANSCRIPTION_PROMPT, ILLUSTRATION_DESCRIPTION_PROMPT
from config import STANDARDS

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='processing.log', filemode='w')

class MainProcessor:
    """
    负责编排整个数据处理流程的主类。
    它获取、解析、处理并保存规范数据。
    """
    def __init__(self):
        """初始化所有需要的客户端和处理器。"""
        self.api_client = ApiClient()
        self.ai_processor = AiProcessor()
        logging.info("主处理器初始化完成。")

    def process_single_chapter(self, standard_id: str, chapter: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个章节：获取内容 -> 解析 -> AI处理图片。"""
        chapter_id = chapter.get('id')
        chapter_title = chapter.get('title')
        logging.info(f"--- 开始处理章节: {chapter_title} (ID: {chapter_id}) ---")

        # 1. 获取章节的详细HTML内容
        chapter_details = self.api_client.get_chapter_detail(standard_id, chapter_id)
        if not chapter_details or 'data' not in chapter_details or not chapter_details['data'].get('content'):
            logging.error(f"无法获取或解析章节 {chapter_id} 的内容。")
            return None

        # 2. 解析HTML
        html_content = chapter_details['data']['content']
        parser = HtmlParser(html_content)
        structured_content = parser.get_structured_content()

        # 3. 遍历内容块并进行AI处理
        processed_texts = []
        for block in structured_content:
            if block['type'] == 'text':
                processed_texts.append(block['content'])
            elif block['type'] == 'image':
                image_url = block['src']
                image_type = block['image_type']
                title = block['title']

                logging.info(f"检测到图片: 类型={image_type}, URL={image_url}")

                ai_result = None
                if image_type == 'formula':
                    ai_result = self.ai_processor.process_image_from_url(image_url, FORMULA_OCR_PROMPT)
                elif image_type == 'table':
                    ai_result = self.ai_processor.process_image_from_url(image_url, TABLE_TRANSCRIPTION_PROMPT)
                elif image_type == 'illustration':
                    # 动态填充prompt中的标题
                    prompt = ILLUSTRATION_DESCRIPTION_PROMPT.format(chart_title=title or "无标题")
                    ai_result = self.ai_processor.process_image_from_url(image_url, prompt)

                if ai_result:
                    processed_texts.append(f"\n[AI处理结果 - {image_type}]:\n{ai_result}\n")
                else:
                    processed_texts.append(f"\n[图片处理失败: {image_url}]\n")

                # 防止API调用过于频繁
                time.sleep(1) # 增加1秒延迟

        # 4. 组合结果
        final_text = "\n".join(processed_texts)
        return {
            "standard_id": standard_id,
            "chapter_id": chapter_id,
            "chapter_title": chapter_title,
            "processed_content": final_text
        }

    def _flatten_chapters(self, chapters_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将嵌套的章节列表展平为一个简单的列表。"""
        flat_list = []
        for chapter in chapters_list:
            # 添加一级章节
            flat_list.append({
                "id": chapter.get("chapterId"),
                "title": chapter.get("title")
            })
            # 如果有二级章节，也添加进来
            if "twoChapter" in chapter and chapter["twoChapter"]:
                for sub_chapter in chapter["twoChapter"]:
                    flat_list.append({
                        "id": sub_chapter.get("chapterId"),
                        "title": sub_chapter.get("title")
                    })
        return flat_list

    def run(self, standard_key: str = 'concrete', chapter_limit: int = 3):
        """
        运行指定规范的完整处理流程。

        Args:
            standard_key (str): 'concrete' 或 'steel'。
            chapter_limit (int): 为了演示和测试，限制处理的章节数量。
        """
        standard_info = STANDARDS.get(standard_key)
        if not standard_info:
            logging.error(f"未知的规范密钥: {standard_key}")
            return

        standard_id = standard_info['id']
        standard_name = standard_info['name']
        logging.info(f"====== 开始处理规范: {standard_name} (ID: {standard_id}) ======")

        # 1. 获取规范的完整目录
        toc_data = self.api_client.get_toc(standard_id)
        # 根据之前的经验，成功的数据应该在'data'键下
        if not toc_data or not toc_data.get('data'):
            logging.error(f"无法获取规范 {standard_name} 的目录，或返回的数据格式不正确。")
            logging.error(f"API响应: {json.dumps(toc_data, indent=2, ensure_ascii=False)}")
            return

        # 2. 展平目录结构
        chapters_raw = toc_data['data']['list']
        chapters_flat = self._flatten_chapters(chapters_raw)
        logging.info(f"成功解析并展平了 {len(chapters_flat)} 个章节。")

        # 3. 遍历并处理每一个章节
        all_processed_data = []
        for i, chapter in enumerate(chapters_flat):
            if i >= chapter_limit:
                logging.info(f"演示限制：已处理 {chapter_limit} 个章节，停止处理。")
                break

            processed_chapter = self.process_single_chapter(standard_id, chapter)
            if processed_chapter:
                all_processed_data.append(processed_chapter)

        # 4. 保存结果到文件
        output_filename = f"processed_{standard_key}_data.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_processed_data, f, ensure_ascii=False, indent=2)

        logging.info(f"====== 规范处理完成: {standard_name} ======")
        logging.info(f"结果已保存到文件: {output_filename}")


if __name__ == '__main__':
    processor = MainProcessor()
    # 运行混凝土规范的处理流程
    processor.run('concrete')
