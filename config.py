# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# --- 安全敏感配置 ---
# API密钥和机密信息从环境变量加载。
# 请在项目根目录下创建一个.env文件，并在其中添加您的密钥。
# 具体格式请参照.env.example文件。
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# 由于我们切换到本地重排序模型，因此不再需要COHERE_API_KEY。
# COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# --- API端点配置 ---
API_CONFIG = {
    "base_url": "https://www.kscecs.com/api/web/stdRead/",
    "endpoints": {
        "toc": "searchTocInfo",       # 获取目录信息的端点
        "detail": "searchStdReadDetail" # 获取章节详细内容的端点
    }
}

# --- 请求头配置 ---
# 该字典现在包含了用户指出的独立的'token'头信息。
HEADERS = {
    "accesstoken": os.getenv("ACCESS_TOKEN"),
    "cookie": os.getenv("COOKIE"),
    "token": "46a2f7762f9612349f0d8885a987e5a2", # 添加了缺失的token字段
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
    "Referer": "https://www.kscecs.com/reader-standard-3739",
    "Origin": "https://www.kscecs.com",
    "Plat": "2"
}

# --- 规范标准配置 ---
STANDARDS = {
    "concrete": {
        "name": "混凝土结构设计规范",
        "id": "27"
    },
    "steel": {
        "name": "钢结构设计规范",
        "id": "3739"
    }
}

# --- ChromaDB数据库配置 ---
CHROMA_DB_CONFIG = {
    "path": "./chroma_db", # 数据库文件存储路径
    "collection_name": "structural_design_specs" # 集合名称
}

# --- 模型配置 (由用户更新) ---
EMBEDDING_MODEL = "text-embedding-004" # 文本嵌入模型
# 使用一个强大的多模态模型来同时处理视觉和文本生成任务。
MULTIMODAL_MODEL = "gemini-1.5-pro-latest"
# 从Cohere API切换到一个本地的、开源的重排序模型。
RERANK_MODEL = "BAAI/bge-reranker-large"

# --- 文本分块配置 ---
CHUNK_CONFIG = {
    "clause_max_tokens": 512 # “说明”文本块的最大token数
}

# --- 日志配置 ---
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": "app.log"
}

# --- 数据处理配置 ---
PROCESSING_CONFIG = {
    "output_dir": "./processed_data" # 指定处理结果的输出目录
}

# --- 完整性检查 ---
# 一个简单的检查，确保关键的环境变量已被加载。
if not all([HEADERS["accesstoken"], HEADERS["cookie"]]):
    print("严重警告: 所需的环境变量（访问令牌、Cookie）未完全设置。")
    print("请检查您的.env文件或环境设置。")
