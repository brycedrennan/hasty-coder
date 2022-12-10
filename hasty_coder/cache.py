import tempfile
from functools import lru_cache

import diskcache as dc

CACHE_PATH = tempfile.gettempdir() + "/resolute-coder-prompt-cache"


@lru_cache()
def cache_instance():
    return dc.Cache(CACHE_PATH)
