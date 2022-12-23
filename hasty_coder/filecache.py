import os.path
import tempfile
import time
from hashlib import md5

import requests


def get_cached_url_contents(url, cache_duration_seconds=60 * 60 * 24 * 7):
    """
    Return the contents of a url

    Cache responses for `cache_duration_seconds` in files in the os-appropriate temp dir in
    a subfolder `hasty-coder/filecache/`. They key should be an md5 of the url.

    If the cached file is older than cache_duration_seconds it should be replaced with a new one in
    an atomic fashion.
    """
    key = md5(url.encode("utf-8")).hexdigest()
    cache_dir = os.path.join(tempfile.gettempdir(), "hasty-coder/filecache/")
    cache_file = os.path.join(cache_dir, key)

    # Ensure the cache folder exists
    os.makedirs(cache_dir, exist_ok=True)

    if (
        os.path.exists(cache_file)
        and os.path.getmtime(cache_file) > time.time() - cache_duration_seconds
    ):
        with open(cache_file, "rb") as f:
            contents = f.read()
    else:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        contents = response.content

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp_file:
            tmp_file.write(contents)

        # Atomically rename the temporary file to the cache file
        os.replace(tmp_file.name, cache_file)

    return contents
