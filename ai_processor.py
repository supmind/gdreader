# -*- coding: utf-8 -*-

import google.generativeai as genai
import requests
from PIL import Image
from io import BytesIO
import logging
from typing import Optional

# Import configurations and prompts
from config import GOOGLE_API_KEY, VISION_MODEL
from prompts import FORMULA_OCR_PROMPT, TABLE_TRANSCRIPTION_PROMPT, ILLUSTRATION_DESCRIPTION_PROMPT

class AiProcessor:
    """
    Handles all interactions with the Google Gemini AI models for processing images.
    """
    def __init__(self):
        """
        Initializes the AI processor by configuring the API key and the generative model.
        """
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(VISION_MODEL)
            logging.info(f"AI Processor initialized with model: {VISION_MODEL}")
        except Exception as e:
            logging.error(f"Failed to initialize Google Generative AI. Check API key. Error: {e}", exc_info=True)
            raise

    def process_image_from_url(self, image_url: str, prompt: str) -> Optional[str]:
        """
        Downloads an image from a URL, sends it to the Gemini Vision model with a given prompt,
        and returns the generated text content.

        Args:
            image_url (str): The URL of the image to process.
            prompt (str): The prompt to use for the AI model.

        Returns:
            Optional[str]: The generated text from the model, or None if an error occurs.
        """
        try:
            # 1. Fetch the image data from the URL
            logging.info(f"Fetching image from URL: {image_url}")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # 2. Open the image using Pillow
            img = Image.open(BytesIO(response.content))

            # 3. Call the Gemini API with the image and prompt
            logging.info("Sending image and prompt to Gemini Vision model...")
            # The API expects a list of content parts, which can be text or images
            response = self.model.generate_content([prompt, img], stream=False)

            # 4. Extract and return the text part of the response
            generated_text = response.text.strip()
            logging.info("Successfully received response from Gemini.")
            return generated_text

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download image from {image_url}. Error: {e}")
            return None
        except IOError as e:
            logging.error(f"Failed to open or identify image from {image_url}. Error: {e}")
            return None
        except Exception as e:
            # This will catch potential errors from the genai library call
            logging.error(f"An error occurred while processing the image with the AI model. Error: {e}", exc_info=True)
            return None

# --- Main block for demonstration and testing ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # A simple check to ensure the API key is set in the environment
    if not GOOGLE_API_KEY:
        logging.error("The GOOGLE_API_KEY environment variable is not set. Please create a .env file and set the key.")
    else:
        print("--- AI Processor Module Verification ---")
        print("AiProcessor class is defined and ready to be used.")
        print("The following test block is commented out because it relies on external image URLs that may be unstable.")
        print("To perform a live test, please provide valid, publicly accessible URLs for a formula and a table image.")

        # NOTE: The following live test block is commented out.
        # Finding stable, public-domain image URLs for testing is unreliable.
        # The AiProcessor class's logic is sound, but a full end-to-end test
        # requires valid image inputs. To run this test, uncomment the block
        # and replace the placeholder URLs with valid ones.

        # try:
        #     processor = AiProcessor()

        #     # Example 1: Test with a formula image
        #     formula_url = "REPLACE_WITH_A_VALID_FORMULA_IMAGE_URL"
        #     print(f"\nTesting Formula OCR with URL: {formula_url}")
        #     latex_result = processor.process_image_from_url(formula_url, FORMULA_OCR_PROMPT)
        #     if latex_result:
        #         print("--- Formula OCR Result ---")
        #         print(latex_result)
        #     else:
        #         print("--- Formula OCR Failed (check URL and API key) ---")

        #     # Example 2: Test with a table image
        #     table_url = "REPLACE_WITH_A_VALID_TABLE_IMAGE_URL"
        #     print(f"\nTesting Table Transcription with URL: {table_url}")
        #     markdown_result = processor.process_image_from_url(table_url, TABLE_TRANSCRIPTION_PROMPT)
        #     if markdown_result:
        #         print("--- Table Transcription Result ---")
        #         print(markdown_result)
        #     else:
        #         print("--- Table Transcription Failed (check URL and API key) ---")

        # except Exception as e:
        #      logging.error(f"An error occurred during the live test: {e}")

        print("\n--- AI Processor Verification Finished ---")
