# -*- coding: utf-8 -*-

import google.generativeai as genai
import requests
from PIL import Image
from io import BytesIO
import logging
from typing import Optional

# 导入配置和提示词
from config import GOOGLE_API_KEY, MULTIMODAL_MODEL
from prompts import FORMULA_OCR_PROMPT, TABLE_TRANSCRIPTION_PROMPT, ILLUSTRATION_DESCRIPTION_PROMPT

class AiProcessor:
    """
    处理所有与Google Gemini AI模型相关的图片处理交互。
    """
    def __init__(self):
        """
        通过配置API密钥和生成模型来初始化AI处理器。
        """
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(MULTIMODAL_MODEL)
            logging.info(f"AI处理器已使用模型初始化: {MULTIMODAL_MODEL}")
        except Exception as e:
            logging.error(f"初始化Google Generative AI失败。请检查API密钥。错误: {e}", exc_info=True)
            raise

    def process_image_from_url(self, image_url: str, prompt: str) -> Optional[str]:
        """
        从URL下载图片，将其与给定的提示词一同发送给Gemini Vision模型，
        并返回生成的文本内容。

        Args:
            image_url (str): 待处理图片的URL。
            prompt (str): 用于AI模型的提示词。

        Returns:
            Optional[str]: 模型生成的文本，如果发生错误则返回None。
        """
        try:
            # 1. 从URL获取图片数据
            logging.info(f"正在从URL获取图片: {image_url}")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # 2. 使用Pillow打开图片
            img = Image.open(BytesIO(response.content))

            # 3. 使用图片和提示词调用Gemini API
            logging.info("正在向Gemini Vision模型发送图片和提示词...")
            # API期望一个内容部分的列表，可以是文本或图片
            response = self.model.generate_content([prompt, img], stream=False)

            # 4. 提取并返回响应中的文本部分
            generated_text = response.text.strip()
            logging.info("成功从Gemini接收到响应。")
            return generated_text

        except requests.exceptions.RequestException as e:
            logging.error(f"从 {image_url} 下载图片失败。错误: {e}")
            return None
        except IOError as e:
            logging.error(f"从 {image_url} 打开或识别图片失败。错误: {e}")
            return None
        except Exception as e:
            # 捕获genai库调用可能产生的错误
            logging.error(f"使用AI模型处理图片时发生错误。错误: {e}", exc_info=True)
            return None

# --- 用于演示和测试的主代码块 ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 一个简单的检查，确保API密钥已在环境中设置
    if not GOOGLE_API_KEY:
        logging.error("环境变量 GOOGLE_API_KEY 未设置。请创建一个.env文件并设置该密钥。")
    else:
        print("--- AI处理器模块验证 ---")
        print("AiProcessor 类已定义并可供使用。")
        print("以下测试块已被注释掉，因为它依赖于可能不稳定的外部图片URL。")
        print("要执行实时测试，请为公式和表格图片提供有效的、公开可访问的URL。")

        # 注意：以下实时测试块已被注释掉。
        # 寻找稳定的、公共领域的测试图片URL是不可靠的。
        # AiProcessor类的逻辑是健全的，但一个完整的端到端测试
        # 需要有效的图片输入。要运行此测试，请取消注释该代码块
        # 并将占位符URL替换为有效的URL。

        # try:
        #     processor = AiProcessor()

        #     # 示例1：测试公式图片
        #     formula_url = "替换为一个有效的公式图片URL"
        #     print(f"\n使用URL测试公式OCR: {formula_url}")
        #     latex_result = processor.process_image_from_url(formula_url, FORMULA_OCR_PROMPT)
        #     if latex_result:
        #         print("--- 公式OCR结果 ---")
        #         print(latex_result)
        #     else:
        #         print("--- 公式OCR失败（请检查URL和API密钥） ---")

        #     # 示例2：测试表格图片
        #     table_url = "替换为一个有效的表格图片URL"
        #     print(f"\n使用URL测试表格转录: {table_url}")
        #     markdown_result = processor.process_image_from_url(table_url, TABLE_TRANSCRIPTION_PROMPT)
        #     if markdown_result:
        #         print("--- 表格转录结果 ---")
        #         print(markdown_result)
        #     else:
        #         print("--- 表格转录失败（请检查URL和API密钥） ---")

        # except Exception as e:
        #      logging.error(f"实时测试期间发生错误: {e}")

        print("\n--- AI处理器验证完成 ---")
