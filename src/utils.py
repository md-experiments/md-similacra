import datetime
import traceback
import itertools
from hashlib import md5

def hash_text(t):
    return md5(str(t).encode()).hexdigest()

def log_traceback():
    return traceback.format_exc()

def flatten_list(ls):
    return list(itertools.chain.from_iterable(ls))