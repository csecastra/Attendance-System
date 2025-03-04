import random
import string

def generate_token(length=3):
    return ''.join(random.choices(string.digits, k=length))