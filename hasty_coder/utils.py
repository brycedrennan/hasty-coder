import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import openai.error
import orjson
from langchain import OpenAI

logger = logging.getLogger(__name__)


def extract_json(text):
    text = text.strip().strip("`")
    return robust_json_loads(text)


class LoggedOpenAI(OpenAI):
    def __init__(self, *args, **kwargs):
        kwargs["request_timeout"] = 30
        kwargs.setdefault("max_tokens", 2000)
        super().__init__(*args, **kwargs)

    def __call__(self, prompt, stop=None, as_json=False, try_count=3):
        prompt = prompt.strip()
        total_response = ""
        for i in range(6):
            logger.debug("STARTPROMPT\n%s\nENDPROMPT", prompt)
            try:
                last_response = super().__call__(prompt + total_response, stop)
            except openai.error.RateLimitError:
                logger.warning("Rate limit error, pausing and then retrying")
                time.sleep(10)
                continue
            total_response += last_response
            logger.debug("STARTANSWER:\n%s\nENDANSWER", last_response)
            if not as_json:
                return total_response.strip()
            try:
                return extract_json(last_response)
            except orjson.JSONDecodeError:
                logger.exception("JSON DECODE ERROR: %s", last_response)
                continue
            except openai.error.Timeout:
                logger.error("TIMEOUT ERROR")
                continue

        raise Exception("Failed to get valid JSON")

    def multicall(self, prompts, stop=None, as_json=False, max_workers=2):
        return parallel_run(
            self.__call__,
            prompts,
            {"stop": stop, "as_json": as_json},
            max_workers=max_workers,
        )


def parallel_run(func, iterable, kwargs=None, max_workers=2):
    if kwargs is None:
        kwargs = {}
    f = partial(func, **kwargs)
    with ThreadPoolExecutor(max_workers=max_workers) as e:
        results = list(e.map(f, iterable))
    return results


def slugify(text):
    # camelcase to dash-separated
    text = re.sub(r"([A-Z])", r"-\1", text.strip())

    # replace any whitespace or punctuation with a dash
    text = re.sub(r"[\s_-]+", "-", text)

    # remove non-alphanumeric characters
    text = re.sub(r"[^a-zA-Z0-9-]", "", text)

    return text.lower().strip("-_ ")


def phraseify(text):
    # replace any whitespace or punctuation with a dash
    text = re.sub(r"[\s_-]+", " ", text)
    # remove non-alphanumeric characters
    text = re.sub(r"[^a-zA-Z0-9-]", "", text)
    return text.strip()


def remove_last_comma_before_index(text, start_index):
    # Find the index of the last comma before the start_index
    last_comma_index = -1
    for i in range(start_index - 1, -1, -1):
        if text[i] == ",":
            last_comma_index = i
            break

    if last_comma_index != -1:
        return text[:last_comma_index] + text[last_comma_index + 1 :]

    return text


def robust_json_loads(json_string):
    while True:
        try:
            return orjson.loads(json_string)
        except orjson.JSONDecodeError as e:
            if "trailing comma is not allowed" in str(e):
                json_string = remove_last_comma_before_index(json_string, e.pos)
                continue
            if "unexpected end of data" in str(e):
                json_string = remove_last_comma_before_index(json_string, e.pos)
                continue
            raise e
