import random
import string



def get_reserved_short_names():
    return ['shortner', 'documentation']

def shortname_generator():
    allowed_chars = string.ascii_letters + string.digits
    short_name_length = 8
    return ''.join(random.choice(allowed_chars) for x in range(short_name_length + 1))
