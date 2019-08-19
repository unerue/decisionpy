from functools import wraps
import time


def timeit(*argv, *kargv):
    start_time = time.time()
    func(*argv, *kargv):
    return time.time() - start_time
