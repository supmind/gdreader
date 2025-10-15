# -*- coding: utf-8 -*-

import requests
import json
import logging
from typing import Dict, Any

# Import configurations from the config file
from config import API_CONFIG, HEADERS, STANDARDS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ApiClient:
    """
    A client to interact with the structural design specification API.
    """
    def __init__(self):
        self.base_url = API_CONFIG['base_url']
        self.headers = HEADERS

    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to make a POST request to a given endpoint.

        Args:
            endpoint (str): The API endpoint to target (e.g., 'toc' or 'detail').
            payload (Dict[str, Any]): The JSON payload for the request.

        Returns:
            Dict[str, Any]: The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: For network-related errors.
            ValueError: If the response is not a valid JSON.
        """
        url = f"{self.base_url}{API_CONFIG['endpoints'][endpoint]}"
        logging.info(f"Making POST request to {url} with payload: {payload}")
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
            raise
        except requests.exceptions.RequestException as req_err:
            logging.error(f"A request error occurred: {req_err}")
            raise
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON from response: {response.text}")
            raise ValueError("Invalid JSON response received from the server.")

    def get_toc(self, standard_id: str) -> Dict[str, Any]:
        """
        Fetches the Table of Contents (TOC) for a given standard.

        Args:
            standard_id (str): The ID of the standard (e.g., "27" for concrete).

        Returns:
            Dict[str, Any]: The API response containing the TOC.
        """
        payload = {"standardId": standard_id}
        return self._make_request('toc', payload)

    def get_chapter_detail(self, standard_id: str, chapter_id: str) -> Dict[str, Any]:
        """
        Fetches the detailed content for a specific chapter of a standard.

        Args:
            standard_id (str): The ID of the standard.
            chapter_id (str): The ID of the chapter.

        Returns:
            Dict[str, Any]: The API response containing the chapter details.
        """
        payload = {"standardId": standard_id, "chapterId": chapter_id}
        return self._make_request('detail', payload)

if __name__ == '__main__':
    # This block is for demonstration and basic testing of the ApiClient.
    # It will be executed when the script is run directly.
    logging.info("Running basic tests for ApiClient...")
    client = ApiClient()

    try:
        # Test fetching TOC for the concrete standard
        concrete_std_id = STANDARDS['concrete']['id']
        logging.info(f"Fetching TOC for Concrete Standard (ID: {concrete_std_id})...")
        concrete_toc = client.get_toc(concrete_std_id)
        logging.info("Successfully fetched Concrete TOC.")
        # print(json.dumps(concrete_toc, indent=2, ensure_ascii=False))

        # Test fetching a specific chapter (e.g., the 'notice' chapter if it exists)
        if concrete_toc.get('result'):
            # Let's try to fetch the first chapter from the list as an example
            # Note: The actual chapter IDs need to be parsed from the TOC structure
            first_chapter_id = "notice" # A common starting point
            logging.info(f"Fetching details for Chapter '{first_chapter_id}' of Concrete Standard...")
            chapter_details = client.get_chapter_detail(concrete_std_id, first_chapter_id)
            logging.info(f"Successfully fetched details for Chapter '{first_chapter_id}'.")
            # print(json.dumps(chapter_details, indent=2, ensure_ascii=False))

        # Test fetching TOC for the steel standard
        steel_std_id = STANDARDS['steel']['id']
        logging.info(f"Fetching TOC for Steel Standard (ID: {steel_std_id})...")
        steel_toc = client.get_toc(steel_std_id)
        logging.info("Successfully fetched Steel TOC.")

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred during the test run: {e}")
    except ValueError as e:
        logging.error(f"A value error occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
