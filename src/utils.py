import datetime, os
import traceback
import itertools
from hashlib import md5

def hash_text(t):
    return md5(str(t).encode()).hexdigest()

def log_traceback():
    return traceback.format_exc()

def flatten_list(ls):
    return list(itertools.chain.from_iterable(ls))

def pad_integer(i):
    return str(i) if len(str(i))==2 else f'0{i}'

def makedirs(paths):
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


def files_in_dir(path, filters = []):
    fls = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
    fls = [os.path.join(path,f) for f in fls]
    if len(filters) > 0:
        if not isinstance(filters,list):
            filters = [filters]
        for filter in filters:
            fls = [f for f in fls if filter in f]
    return fls