from functools import wraps
import time


def timeit(func):
    @wraps(func)
    def func(*args, **kwargs)
        start_time = time.time()
        func(*argv, *kargv):
        print(time.time() - start_time)
        return 
    return 
