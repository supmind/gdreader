# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- Security Sensitive Configuration ---
# API Keys and Secrets are loaded from environment variables.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# COHERE_API_KEY is no longer needed as we are switching to a local reranker model.
# COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# --- API Endpoint Configuration ---
API_CONFIG = {
    "base_url": "https://www.kscecs.com/api/web/stdRead/",
    "endpoints": {
        "toc": "searchTocInfo",
        "detail": "searchStdReadDetail"
    }
}

# --- Request Headers Configuration ---
# This dictionary now includes the separate 'token' header as identified by the user.
HEADERS = {
    "accesstoken": os.getenv("ACCESS_TOKEN"),
    "cookie": os.getenv("COOKIE"),
    "token": "46a2f7762f9612349f0d8885a987e5a2",
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
    "Referer": "https://www.kscecs.com/reader-standard-3739",
    "Origin": "https://www.kscecs.com",
    "Plat": "2"
}

# --- Specification Standards Configuration ---
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

# --- ChromaDB Configuration ---
CHROMA_DB_CONFIG = {
    "path": "./chroma_db",
    "collection_name": "structural_design_specs"
}

# --- Model Configuration (Updated by user) ---
EMBEDDING_MODEL = "text-embedding-004"
# Using a single powerful multimodal model for both vision and text generation tasks.
MULTIMODAL_MODEL = "gemini-1.5-pro-latest"
# Switched from Cohere API to a local, open-source reranker model.
RERANK_MODEL = "BAAI/bge-reranker-large"

# --- Chunking Configuration ---
CHUNK_CONFIG = {
    "clause_max_tokens": 512
}

# --- Logging Configuration ---
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": "app.log"
}

# --- Sanity Check ---
if not all([HEADERS["accesstoken"], HEADERS["cookie"]]):
    print("CRITICAL WARNING: Not all required environment variables (Access Token, Cookie) are set.")
    print("Please check your .env file or environment settings.")
