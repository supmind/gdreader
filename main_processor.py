# -*- coding: utf-8 -*-

import json
import logging
import time
import os
from typing import List, Dict, Any
from urllib.parse import urljoin

# 导入我们自己开发的模块
from api_client import ApiClient
from html_parser import HtmlParser
from ai_processor import AiProcessor
from prompts import FORMULA_OCR_PROMPT, TABLE_TRANSCRIPTION_PROMPT, ILLUSTRATION_DESCRIPTION_PROMPT
from config import STANDARDS, PROCESSING_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='processing.log', filemode='w')


class MainProcessor:
    """
    负责编排整个数据处理流程的主类。
    它获取、解析、处理并保存规范数据，支持可配置和可恢复的处理。
    """
    def __init__(self):
        """初始化所有需要的客户端和处理器。"""
        self.api_client = ApiClient()
        self.ai_processor = AiProcessor()
        self.output_dir = PROCESSING_CONFIG['output_dir']
        self.base_url = "https://www.kscecs.com"
        os.makedirs(self.output_dir, exist_ok=True)
        logging.info("主处理器初始化完成。")

    def _process_html_content(self, html_content: str, chapter_title: str) -> str:
        """从HTML内容中解析、处理图片并返回纯文本。"""
        parser = HtmlParser(html_content)
        structured_content = parser.get_structured_content()
        processed_texts = []

        for block in structured_content:
            if block['type'] == 'text':
                processed_texts.append(block['content'])
            elif block['type'] == 'image':
                image_url = block['src']
                # --- 核心修复：处理相对URL ---
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(self.base_url, image_url)

                image_type = block['image_type']
                title = block['title']

                logging.info(f"检测到图片: 类型={image_type}, URL={image_url}")

                ai_result = None
                if image_type == 'formula':
                    ai_result = self.ai_processor.process_image_from_url(image_url, FORMULA_OCR_PROMPT)
                elif image_type == 'table':
                    ai_result = self.ai_processor.process_image_from_url(image_url, TABLE_TRANSCRIPTION_PROMPT)
                elif image_type == 'illustration':
                    prompt = ILLUSTRATION_DESCRIPTION_PROMPT.format(chart_title=title or chapter_title or "无标题")
                    ai_result = self.ai_processor.process_image_from_url(image_url, prompt)

                if ai_result:
                    processed_texts.append(f"\n[AI处理结果 - {image_type}]:\n{ai_result}\n")
                else:
                    processed_texts.append(f"\n[图片处理失败: {image_url}]\n")

                time.sleep(1) # 防止API调用过于频繁

        return "\n".join(processed_texts)

    def _recursive_process_chapter_data(self, chapter_data: Dict[str, Any]) -> str:
        """递归处理章节数据，提取所有层级的 content 文本。"""
        all_text = []
        # 1. 处理当前层级的 content
        if chapter_data.get('content'):
            all_text.append(self._process_html_content(chapter_data['content'], chapter_data.get('title')))

        # 2. 递归处理 twoChapter
        if 'twoChapter' in chapter_data and chapter_data['twoChapter']:
            for sub_chapter in chapter_data['twoChapter']:
                all_text.append(self._recursive_process_chapter_data(sub_chapter))

        # 3. 递归处理 threeChapter
        if 'threeChapter' in chapter_data and chapter_data['threeChapter']:
            for sub_sub_chapter in chapter_data['threeChapter']:
                all_text.append(self._recursive_process_chapter_data(sub_sub_chapter))

        return "\n\n".join(filter(None, all_text))


    def process_single_chapter(self, standard_key: str, standard_id: str, chapter: Dict[str, Any]):
        """处理单个章节的入口函数。"""
        chapter_id_raw = chapter.get('id')
        chapter_title = chapter.get('title')
        # 文件名处理，替换掉非法字符
        chapter_id_safe = str(chapter_id_raw).replace('.', '_').replace('/','_')

        standard_output_dir = os.path.join(self.output_dir, standard_key)
        output_filepath = os.path.join(standard_output_dir, f"chapter_{chapter_id_safe}.json")

        if os.path.exists(output_filepath):
            logging.info(f"章节 {chapter_title} (ID: {chapter_id_raw}) 已处理，跳过。")
            return

        logging.info(f"--- 开始处理章节: {chapter_title} (ID: {chapter_id_raw}) ---")

        chapter_details = self.api_client.get_chapter_detail(standard_id, chapter_id_raw)
        if not chapter_details or 'data' not in chapter_details:
            logging.error(f"无法获取或解析章节 {chapter_id_raw} 的内容。API响应: {chapter_details}")
            return

        # 使用递归函数来处理可能嵌套的内容
        final_text = self._recursive_process_chapter_data(chapter_details['data'])

        if not final_text.strip():
            logging.warning(f"章节 {chapter_title} (ID: {chapter_id_raw}) 未提取到任何文本内容。")
            return

        result_data = {
            "standard_id": standard_id,
            "standard_key": standard_key,
            "chapter_id": chapter_id_raw,
            "chapter_title": chapter_title,
            "processed_content": final_text
        }

        os.makedirs(standard_output_dir, exist_ok=True)
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        logging.info(f"成功处理并保存章节 {chapter_title} 到 {output_filepath}")

    def _flatten_chapters(self, chapters_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将嵌套的章节列表展平为一个简单的列表。"""
        flat_list = []
        for chapter in chapters_list:
            flat_list.append({"id": chapter.get("chapterId"), "title": chapter.get("title")})
            if "twoChapter" in chapter and chapter["twoChapter"]:
                for sub_chapter in chapter["twoChapter"]:
                    flat_list.append({"id": sub_chapter.get("chapterId"), "title": sub_chapter.get("title")})
                    # 也可以在这里继续递归展平三级、四级等，但当前API结构最多到三级，且我们的处理逻辑可以处理嵌套，所以展平到二级即可。
        return flat_list

    def run(self):
        """运行在config.py中定义的所有规范的完整处理流程。"""
        logging.info("====== 开始执行可恢复的数据处理流程 ======")

        for standard_key, standard_info in STANDARDS.items():
            standard_id = standard_info['id']
            standard_name = standard_info['name']
            logging.info(f"--- 开始处理规范: {standard_name} (ID: {standard_id}) ---")

            toc_data = self.api_client.get_toc(standard_id)
            if not toc_data or not toc_data.get('data') or not toc_data['data'].get('list'):
                logging.error(f"无法获取规范 {standard_name} 的目录，跳过此规范。")
                continue

            chapters_flat = self._flatten_chapters(toc_data['data']['list'])
            logging.info(f"规范 {standard_name} 共解析出 {len(chapters_flat)} 个章节。")

            for chapter in chapters_flat:
                if not chapter.get('id'):
                    logging.warning(f"发现一个没有ID的章节，跳过: {chapter.get('title')}")
                    continue
                try:
                    self.process_single_chapter(standard_key, standard_id, chapter)
                except Exception as e:
                    logging.error(f"处理章节 {chapter.get('title')} 时发生未知错误: {e}", exc_info=True)

            logging.info(f"--- 规范 {standard_name} 处理完成 ---")

        logging.info("====== 所有规范处理流程执行完毕 ======")

if __name__ == '__main__':
    processor = MainProcessor()
    processor.run()
    # 创建一个标记文件，表示所有处理已成功完成
    with open("processing_complete.flag", "w") as f:
        f.write("done")
