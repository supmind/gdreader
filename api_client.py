# -*- coding: utf-8 -*-

import requests
import json
import logging
from typing import Dict, Any

# 从配置文件导入配置信息
from config import API_CONFIG, HEADERS, STANDARDS

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ApiClient:
    """
    一个用于与结构设计规范API进行交互的客户端。
    """
    def __init__(self):
        """
        初始化ApiClient。
        """
        self.base_url = API_CONFIG['base_url']
        self.headers = HEADERS

    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        内部方法，用于向指定的端点发送POST请求。

        Args:
            endpoint (str): 目标API端点（例如, 'toc' 或 'detail'）。
            payload (Dict[str, Any]): 请求的JSON负载。

        Returns:
            Dict[str, Any]: 来自API的JSON响应。

        Raises:
            requests.exceptions.RequestException: 处理网络相关的错误。
            ValueError: 如果响应不是有效的JSON。
        """
        url = f"{self.base_url}{API_CONFIG['endpoints'][endpoint]}"
        logging.info(f"正在向 {url} 发送POST请求, 负载: {payload}")
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()  # 如果状态码是4xx或5xx，则抛出异常
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"发生HTTP错误: {http_err} - 响应内容: {response.text}")
            raise
        except requests.exceptions.RequestException as req_err:
            logging.error(f"发生请求错误: {req_err}")
            raise
        except json.JSONDecodeError:
            logging.error(f"解码JSON响应失败: {response.text}")
            raise ValueError("从服务器收到了无效的JSON响应。")

    def get_toc(self, standard_id: str) -> Dict[str, Any]:
        """
        获取指定规范的目录（Table of Contents, TOC）。

        Args:
            standard_id (str): 规范的ID (例如, "27" 代表混凝土规范)。

        Returns:
            Dict[str, Any]: 包含目录信息的API响应。
        """
        payload = {"standardId": standard_id}
        return self._make_request('toc', payload)

    def get_chapter_detail(self, standard_id: str, chapter_id: str) -> Dict[str, Any]:
        """
        获取规范特定章节的详细内容。

        Args:
            standard_id (str): 规范的ID。
            chapter_id (str): 章节的ID。

        Returns:
            Dict[str, Any]: 包含章节详细信息的API响应。
        """
        payload = {"standardId": standard_id, "chapterId": chapter_id}
        return self._make_request('detail', payload)

if __name__ == '__main__':
    # 这个代码块用于演示和对ApiClient进行基本测试。
    # 当直接运行此脚本时，它将被执行。
    logging.info("正在运行ApiClient的基本测试...")
    client = ApiClient()

    try:
        # 测试获取混凝土规范的目录
        concrete_std_id = STANDARDS['concrete']['id']
        logging.info(f"正在获取混凝土规范 (ID: {concrete_std_id}) 的目录...")
        concrete_toc = client.get_toc(concrete_std_id)
        logging.info("成功获取混凝土规范的目录。")
        # print(json.dumps(concrete_toc, indent=2, ensure_ascii=False))

        # 测试获取一个特定章节 (例如, 'notice' 章节)
        if concrete_toc.get('result'):
            # 注意：实际的章节ID需要从目录结构中解析得出
            first_chapter_id = "notice" # 一个常见的起始点
            logging.info(f"正在获取混凝土规范 '{first_chapter_id}' 章节的详细内容...")
            chapter_details = client.get_chapter_detail(concrete_std_id, first_chapter_id)
            logging.info(f"成功获取 '{first_chapter_id}' 章节的详细内容。")
            # print(json.dumps(chapter_details, indent=2, ensure_ascii=False))

        # 测试获取钢结构规范的目录
        steel_std_id = STANDARDS['steel']['id']
        logging.info(f"正在获取钢结构规范 (ID: {steel_std_id}) 的目录...")
        steel_toc = client.get_toc(steel_std_id)
        logging.info("成功获取钢结构规范的目录。")

    except requests.exceptions.RequestException as e:
        logging.error(f"测试运行期间发生错误: {e}")
    except ValueError as e:
        logging.error(f"发生值错误: {e}")
    except Exception as e:
        logging.error(f"发生意外错误: {e}")
