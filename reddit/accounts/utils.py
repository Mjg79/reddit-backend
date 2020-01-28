import random
import string


def generate_random_username(length: int = 16) -> str:
    """Generate random user name

    Generate a random username that conforms to User model's custom username field

    :return:
    """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))