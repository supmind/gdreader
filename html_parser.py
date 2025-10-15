# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from typing import List, Dict, Any, Literal, Union

# 根据SRS定义图片角色的类型
ImageType = Literal['formula', 'table', 'illustration', 'unknown']

# 为解析器将返回的结构化内容块定义精确的类型
TextBlock = Dict[Literal["type", "content"], Union[Literal["text"], str]]
ImageBlock = Dict[
    Literal["type", "image_type", "src", "title", "original_tag"],
    Union[Literal["image"], ImageType, str, None]
]
ContentBlock = Union[TextBlock, ImageBlock]


class HtmlParser:
    """
    将来自规范API的HTML内容解析成由文本和图片块组成的结构化序列。
    该类专门设计用于处理API响应中发现的特定HTML结构。
    """
    def __init__(self, html_content: str):
        """
        使用HTML内容初始化解析器。

        Args:
            html_content (str): 待解析的原始HTML字符串。
        """
        # 我们将内容包裹在一个单一的根元素中，以简化顶层迭代
        self.soup = BeautifulSoup(f"<body>{html_content}</body>", 'html.parser')

    def _get_image_type(self, img_tag: BeautifulSoup) -> ImageType:
        """
        根据SRS中的规定，基于<img>标签的'class'属性来确定其类型（'formula', 'table', 'illustration'）。
        """
        classes = img_tag.get('class', [])
        if 'role-1' in classes or 'role-3' in classes:
            return 'formula'
        if 'role-2' in classes:
            return 'table'
        if 'role-0' in classes:
            return 'illustration'
        return 'unknown'

    def _get_chart_title_for_tag(self, tag: BeautifulSoup) -> str | None:
        """
        查找与给定标签（例如<img>标签）关联的图表标题。
        SRS规定标题位于class为'.chart-title'的相邻元素中。
        """
        # 一种常见的HTML模式是，图片被包裹在一个容器（如<div>）中，
        # 而标题是该容器的兄弟节点。
        container = tag.find_parent()
        if not container:
            return None

        # 检查紧邻的前一个兄弟节点是否为标题元素
        prev_sibling = container.find_previous_sibling()
        if prev_sibling and 'chart-title' in prev_sibling.get('class', []):
            return prev_sibling.get_text(strip=True)

        # 检查紧邻的后一个兄弟节点是否为标题元素
        next_sibling = container.find_next_sibling()
        if next_sibling and 'chart-title' in next_sibling.get('class', []):
            return next_sibling.get_text(strip=True)

        return None

    def get_structured_content(self) -> List[ContentBlock]:
        """
        将HTML分解成一个由文本块和图片块组成的顺序列表。
        这是解析器的主要公共方法。
        """
        content_blocks: List[ContentBlock] = []

        # 处理我们添加的body标签内的所有顶级元素
        for element in self.soup.body.children:
            # 跳过顶层的非标签元素，如NavigableString
            if not hasattr(element, 'get'):
                continue

            # 显式跳过chart-title元素，因为它们的内容在处理图片时
            # 由_get_chart_title_for_tag方法处理。
            if 'chart-title' in element.get('class', []):
                continue

            # 查找此顶级元素内的所有图片
            images = element.find_all('img')
            if images:
                for img in images:
                    img_type = self._get_image_type(img)
                    img_src = img.get('src', '')
                    title = self._get_chart_title_for_tag(img)

                    content_blocks.append({
                        "type": "image",
                        "image_type": img_type,
                        "src": img_src,
                        "title": title,
                        "original_tag": str(img)
                    })
            # 如果没有图片，则将其视为一个文本块
            else:
                text = element.get_text(separator=' ', strip=True)
                if text:
                    content_blocks.append({"type": "text", "content": text})

        return self._merge_consecutive_text_blocks(content_blocks)

    @staticmethod
    def _merge_consecutive_text_blocks(blocks: List[ContentBlock]) -> List[ContentBlock]:
        """一个用于合并相邻文本块的工具方法，以获得更清晰的输出。"""
        if not blocks:
            return []

        merged_blocks: List[ContentBlock] = []
        text_buffer = []

        for block in blocks:
            if block['type'] == 'text':
                text_buffer.append(block['content'])
            else:
                if text_buffer:
                    merged_blocks.append({'type': 'text', 'content': ' '.join(text_buffer)})
                    text_buffer = []
                merged_blocks.append(block)

        if text_buffer:
            merged_blocks.append({'type': 'text', 'content': ' '.join(text_buffer)})

        return merged_blocks

if __name__ == '__main__':
    # 这个代码块提供了一个可运行的测试用例，以验证解析器的功能。
    print("正在运行HtmlParser的基本测试...")

    # 一个模拟SRS中描述的数据的示例HTML结构。
    sample_html = """
    <p>这是一些条文规定文本。下面是一个公式。</p>
    <div class="figure-wrapper">
        <img src="https://example.com/formula.png" class="role-1">
    </div>
    <p>这是更多文本，然后是一个表格。</p>
    <div class="chart-title">表 3.1.1 混凝土强度等级</div>
    <div class="table-wrapper">
        <img src="https://example.com/table.png" class="role-2">
    </div>
    <p>最后，这是一个示意图。</p>
    <p class="chart-title">图 5.2.1 框架结构示意图</p>
    <div class="figure-wrapper">
        <img src="https://example.com/illustration.png" class="role-0">
    </div>
    <p>这是结尾的文本。</p>
    """

    parser = HtmlParser(sample_html)
    structured_content = parser.get_structured_content()

    import json
    print("\n--- 提取的结构化内容 ---")
    print(json.dumps(structured_content, indent=2, ensure_ascii=False))
    print("--- 测试完成 ---")

    # 验证性检查 - 预期的输出是一个包含7个交错块的序列。
    assert len(structured_content) == 7
    assert structured_content[0]['type'] == 'text' and '公式' in structured_content[0]['content']
    assert structured_content[1]['type'] == 'image' and structured_content[1]['image_type'] == 'formula'
    assert structured_content[2]['type'] == 'text' and '表格' in structured_content[2]['content']
    assert structured_content[3]['type'] == 'image' and structured_content[3]['image_type'] == 'table'
    assert structured_content[3]['title'] == '表 3.1.1 混凝土强度等级'
    assert structured_content[4]['type'] == 'text' and '示意图' in structured_content[4]['content']
    assert structured_content[5]['type'] == 'image' and structured_content[5]['image_type'] == 'illustration'
    assert structured_content[5]['title'] == '图 5.2.1 框架结构示意图'
    assert structured_content[6]['type'] == 'text' and '结尾' in structured_content[6]['content']
    print("\n断言成功通过。")
