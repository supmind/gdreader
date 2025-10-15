# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- Security Sensitive Configuration ---
# API Keys and Secrets are loaded from environment variables.
# Please create a .env file in the root directory and add your keys there.
# See .env.example for the required format.

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# --- API Endpoint Configuration ---
API_CONFIG = {
    "base_url": "https://www.kscecs.com/api/web/stdRead/",
    "endpoints": {
        "toc": "searchTocInfo",
        "detail": "searchStdReadDetail"
    }
}

# --- Request Headers Configuration ---
# Sensitive parts of the headers are loaded from environment variables.
HEADERS = {
    "accesstoken": os.getenv("ACCESS_TOKEN"),
    "cookie": os.getenv("COOKIE"),
    "Content-Type": "application/json",
    "Cache-Control": "no-cache"
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

# --- Model Configuration ---
EMBEDDING_MODEL = "text-embedding-004"
GENERATION_MODEL = "gemini-pro"
VISION_MODEL = "gemini-pro-vision"
RERANK_MODEL = "rerank-english-v2.0" # Note: Please verify the correct model name for Cohere's reranker.

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
# A simple check to ensure that critical environment variables are loaded.
if not all([GOOGLE_API_KEY, COHERE_API_KEY, HEADERS["accesstoken"], HEADERS["cookie"]]):
    print("CRITICAL WARNING: Not all required environment variables (API Keys, Access Token, Cookie) are set.")
    print("Please check your .env file or environment settings.")
