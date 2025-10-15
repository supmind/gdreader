# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from typing import List, Dict, Any, Literal, Union

# Define a type for the image roles based on the SRS
ImageType = Literal['formula', 'table', 'illustration', 'unknown']

# Define precise types for the structured content blocks that the parser will return
TextBlock = Dict[Literal["type", "content"], Union[Literal["text"], str]]
ImageBlock = Dict[
    Literal["type", "image_type", "src", "title", "original_tag"],
    Union[Literal["image"], ImageType, str, None]
]
ContentBlock = Union[TextBlock, ImageBlock]


class HtmlParser:
    """
    Parses HTML content from the specification API into a structured sequence of text and image blocks.
    This class is designed to handle the specific HTML structure found in the API responses.
    """
    def __init__(self, html_content: str):
        """
        Initializes the parser with the HTML content.

        Args:
            html_content (str): The raw HTML string to be parsed.
        """
        # We wrap the content in a single root element to simplify top-level iteration
        self.soup = BeautifulSoup(f"<body>{html_content}</body>", 'html.parser')

    def _get_image_type(self, img_tag: BeautifulSoup) -> ImageType:
        """
        Determines the type of an image ('formula', 'table', 'illustration')
        based on its 'class' attribute as specified in the SRS.
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
        Finds a chart title associated with a given tag (e.g., an <img> tag).
        The SRS specifies that the title is in an adjacent element with class '.chart-title'.
        """
        # A common HTML pattern is that the image is wrapped in a container (e.g., <div>),
        # and the title is a sibling of that container.
        container = tag.find_parent()
        if not container:
            return None

        # Check the immediate previous sibling for a title element
        prev_sibling = container.find_previous_sibling()
        if prev_sibling and 'chart-title' in prev_sibling.get('class', []):
            return prev_sibling.get_text(strip=True)

        # Check the immediate next sibling for a title element
        next_sibling = container.find_next_sibling()
        if next_sibling and 'chart-title' in next_sibling.get('class', []):
            return next_sibling.get_text(strip=True)

        return None

    def get_structured_content(self) -> List[ContentBlock]:
        """
        Decomposes the HTML into a sequential list of text and image blocks.
        This is the main public method of the parser.
        """
        content_blocks: List[ContentBlock] = []

        # Process all top-level elements within the body tag we added
        for element in self.soup.body.children:
            # Skip over non-tag elements like NavigableString at the top level
            if not hasattr(element, 'get'):
                continue

            # Explicitly skip chart-title elements as their content is handled
            # by the _get_chart_title_for_tag method when processing an image.
            if 'chart-title' in element.get('class', []):
                continue

            # Find all images within this top-level element
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
            # If no images, treat it as a text block
            else:
                text = element.get_text(separator=' ', strip=True)
                if text:
                    content_blocks.append({"type": "text", "content": text})

        return self._merge_consecutive_text_blocks(content_blocks)

    @staticmethod
    def _merge_consecutive_text_blocks(blocks: List[ContentBlock]) -> List[ContentBlock]:
        """A utility to merge adjacent text blocks for cleaner output."""
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
    # This block provides a runnable test case to verify the parser's functionality.
    print("Running basic tests for HtmlParser...")

    # A sample HTML structure that mimics the data described in the SRS.
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
    print("\n--- Extracted Structured Content ---")
    print(json.dumps(structured_content, indent=2, ensure_ascii=False))
    print("--- Test Complete ---")

    # Verification checks - The expected output is a sequence of 7 alternating blocks.
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
    print("\nAssertions passed successfully.")
