import logging
import os
import time

import openai
from orjson import orjson

from hasty_coder.utils import extract_json

logger = logging.getLogger(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


def completion(
    prompt,
    *,
    max_tokens=2000,
    temperature=0.0,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=None,
    timeout=30,
    as_json=False,
    model="text-davinci-003",
):
    """Use OpenAI's API to auto-complete a prompt."""
    prompt = prompt.strip()

    total_response = ""
    for i in range(6):
        logger.debug("STARTPROMPT\n%s\nENDPROMPT", prompt)
        try:
            response = openai.Completion.create(
                model=model,
                prompt=prompt + total_response,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                timeout=timeout,
            )
        except openai.error.RateLimitError:
            logger.warning("Rate limit error, pausing and then retrying")
            time.sleep(15)
            continue
        except openai.error.Timeout:
            logger.error("TIMEOUT ERROR")
            continue
        logger.debug("OPEANAI RESPONSE: %s", response)
        response_text = response.choices[0].text
        total_response += response_text

        logger.debug("STARTANSWER:\n%s\nENDANSWER", response_text)
        if not as_json:
            return total_response.strip()
        try:
            return extract_json(total_response)
        except orjson.JSONDecodeError:
            logger.exception("JSON DECODE ERROR: %s", total_response)
            continue

    raise Exception("Failed to get valid response")
