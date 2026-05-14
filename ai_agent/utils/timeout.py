import signal


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException()


def run_with_timeout(func, seconds=5):

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        result = func()
    finally:
        signal.alarm(0)

    return result