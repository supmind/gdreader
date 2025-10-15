# -*- coding: utf-8 -*-

import json
import logging

from api_client import ApiClient
from html_parser import HtmlParser
from config import STANDARDS

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def explore_real_data():
    """
    Fetches a real chapter from the API, parses it, and prints the structured output.
    This serves as an integration test to validate the parser against real-world data.
    """
    logging.info("--- Starting Real Data Exploration ---")

    try:
        # 1. Initialize the API client
        client = ApiClient()

        # 2. Define the target: Concrete standard, 'notice' chapter
        # We use the 'notice' chapter as it's a common and usually simple starting point.
        standard_id = STANDARDS['concrete']['id']
        chapter_id = "notice"

        logging.info(f"Attempting to fetch chapter '{chapter_id}' from standard '{standard_id}'...")

        # 3. Fetch the detailed chapter data from the API
        chapter_data = client.get_chapter_detail(standard_id, chapter_id)

        # 4. Extract the HTML content.
        # Based on typical API responses, the content is likely in a nested structure.
        # Based on the successful API response, the content is under the 'data' key.
        html_content = chapter_data.get('data', {}).get('content')

        if not html_content:
            logging.error("Could not find 'content' in the API response's 'data' object.")
            logging.error(f"API Response: {json.dumps(chapter_data, indent=2, ensure_ascii=False)}")
            return

        logging.info("Successfully fetched real HTML content.")
        # Optional: print the raw HTML for debugging
        # print("\n--- Raw HTML ---")
        # print(html_content)

        # 5. Parse the real HTML content
        logging.info("Parsing HTML content with HtmlParser...")
        parser = HtmlParser(html_content)
        structured_content = parser.get_structured_content()

        # 6. Print the structured output
        logging.info("--- Structured Content from Real Data ---")
        print(json.dumps(structured_content, indent=2, ensure_ascii=False))

    except Exception as e:
        logging.error(f"An error occurred during the data exploration process: {e}", exc_info=True)
    finally:
        logging.info("--- Real Data Exploration Finished ---")

if __name__ == '__main__':
    explore_real_data()
