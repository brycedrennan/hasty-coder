import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import openai.error
from langchain import OpenAI

logger = logging.getLogger(__name__)


def extract_json(text):
    text = text.strip().strip("`")
    return json.loads(text)


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
            last_response = super().__call__(prompt + total_response, stop)
            total_response += last_response
            logger.debug("STARTANSWER:\n%s\nENDANSWER", last_response)
            if not as_json:
                return total_response.strip()
            try:
                return extract_json(last_response)
            except json.JSONDecodeError:
                logger.exception("JSON DECODE ERROR: %s", last_response)
                continue
            except openai.error.Timeout:
                logger.error("TIMEOUT ERROR")
                continue

        raise Exception("Failed to get valid JSON")

    def multicall(self, prompts, stop=None, as_json=False, max_workers=10):
        return parallel_run(
            self.__call__,
            prompts,
            {"stop": stop, "as_json": as_json},
            max_workers=max_workers,
        )

    @staticmethod
    def cached_call(prompt, stop=None, as_json=False):
        pass


def parallel_run(func, iterable, kwargs=None, max_workers=10):
    if kwargs is None:
        kwargs = {}
    f = partial(func, **kwargs)
    with ThreadPoolExecutor(max_workers=max_workers) as e:
        results = list(e.map(f, iterable))
    return results


def slugify(text):
    # camelcase to dash-separated
    text = re.sub(r"([a-zA-Z])([A-Z])", r"\1-\2", text.strip())

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
