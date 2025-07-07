import time
import requests

from itertools import cycle
from tenacity import RetryError


class GPT4O1InferEngine:
    """Class for processing text inputs using GPT-4 API via Azure with controlled key & URL rotation."""
    _url_cycle = cycle([""])
    _api_key_cycle = cycle([""])
    _current_url = next(_url_cycle)  # Store the current URL
    _current_api_key = next(_api_key_cycle)  # Store the current API key

    @classmethod
    def _call_azure_gpt_api(cls, prompt: str) -> str:
        """
        Make an API call to the Azure GPT API with retries on 429 Too Many Requests errors.
        Rotates API key & URL only when hitting 429 errors.
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "api-key": cls._current_api_key
            }

            data = {
                "model": "gpt-4.1",
                "messages": [{"role": "system", "content": prompt}],
                "temperature": 0, "top_p": 0.95
            }

            print(f"Calling Azure GPT API using URL: {cls._current_url}")

            response = requests.post(cls._current_url, json=data, headers=headers, timeout=int(300))

            if response.status_code == 429:  # Handle Rate Limit
                retry_after = int(response.headers.get("Retry-After", 10))  # Default to 10 seconds if header missing
                print(f"Rate limit hit. Retrying after {retry_after} seconds with a new API key and URL...")

                # Rotate URL & API key **only on 429**
                cls._current_url = next(cls._url_cycle)
                cls._current_api_key = next(cls._api_key_cycle)

                time.sleep(retry_after)  # Wait before retrying
                raise requests.exceptions.HTTPError(response=response)  # Trigger retry

            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        except Exception as e:
            print(f"API call failed with error: {e}")

    @classmethod
    def create_extraction_prompt(cls, search_query: str, system_prompt: str = '') -> str:
        prompt = f"""
        {system_prompt}

        I have the following text:

        "{search_query}"

        Please extract the relevant information based on the above informatio provided.
        Provide the information clearly and concisely.
        """
        return prompt


    @classmethod
    def process_text_input(cls, prompt: str, system_template: str='', *args, **kwargs) -> str:
        """
        Process the raw text input using the GPT-4 API.
        """
        gpt_prompt = GPT4O1InferEngine.create_extraction_prompt(prompt, system_prompt=system_template)
        try:
            print("Generating prompt and calling API...")
            result = cls._call_azure_gpt_api(gpt_prompt)
            print(f"LLM Response: {result}")
            return result
        except RetryError as e:
            print(f"Failed after {5} retries: {e}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise


GPT4O1InferEngine()
