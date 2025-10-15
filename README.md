# 专业级结构设计规范查询RAG系统

本项目是一个基于检索增强生成（RAG）技术构建的智能问答系统，旨在为结构工程师提供快速、准确的规范条文查询服务。系统能够深度解析《混凝土结构设计规范》和《钢结构设计规范》，并理解涉及文本、公式、表格及示意图的复杂查询。

## 功能特点

- **多模态理解**: 利用Google Gemini 1.5 Pro模型，能够识别规范中的公式、表格和示意图，并将其转换为结构化文本。
- **高精度检索**: 通过向量嵌入和本地重排序模型（BAAI/bge-reranker-large），确保检索结果与用户查询高度相关。
- **可追溯答案**: 所有回答均基于规范原文，并提供明确的条款来源，保证信息的准确性和权威性。
- **跨规范查询**: 支持同时对混凝土和钢结构两本规范进行联合查询和信息整合。
- **模块化设计**: 项目代码结构清晰，分为数据获取、内容解析、AI处理等多个独立模块，易于维护和扩展。

## 技术架构

| 组件类别 | 选用工具 | 备注 |
| :--- | :--- | :--- |
| **数据源** | **专用API接口** | `searchTocInfo`, `searchStdReadDetail` |
| **核心编排框架** | **LangChain** | 管理整个RAG流程（未来集成） |
| **HTML解析** | **BeautifulSoup4** | 用于解析API返回的HTML内容 |
| **多模态AI引擎** | **Google Gemini 1.5 Pro** | 用于公式OCR、表格转录、插图描述 |
| **嵌入式向量数据库** | **ChromaDB** | 存储知识库 |
| **嵌入模型** | **Google `text-embedding-004`** | 生成文本嵌入 |
| **检索精度增强** | **BAAI/bge-reranker-large** | 本地运行的重排序模型 |

## 安装与设置

### 1. 克隆仓库

```bash
git clone <your-repository-url>
cd <repository-directory>
```

### 2. 创建并配置环境

首先，创建一个`.env`文件，用于存放敏感的API密钥和身份凭证。可以将`.env.example`文件复制一份并重命名为`.env`：

```bash
cp .env.example .env
```

然后，编辑`.env`文件，填入以下信息：

- `GOOGLE_API_KEY`: 您的Google AI API密钥。
- `ACCESS_TOKEN`: 用于访问规范数据API的访问令牌。
- `COOKIE`: 与访问令牌配套的Cookie字符串。

**注意**: `ACCESS_TOKEN` 和 `COOKIE` 可能有有效期，如果遇到“未授权”错误，请更新这些值。

### 3. 安装依赖

项目所需的所有Python库都记录在`requirements.txt`文件中。运行以下命令进行安装：

```bash
pip install -r requirements.txt
```

## 使用说明

(此部分将在后续开发中完善)

当前项目包含了数据获取和内容解析的核心模块，可以运行以下脚本来测试与真实API的数据交互和解析流程：

```bash
python data_explorer.py
```

该脚本会获取一个示例章节，并将其HTML内容解析为结构化的JSON格式打印在控制台中。
