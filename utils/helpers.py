import random
import string


CHARSET = string.ascii_letters + string.digits


def generate_random_key(size: int) -> str:
    return ''.join(random.choice(CHARSET) for _ in range(size))
