from hashlib import md5


def clean_email(email):
    import re
    return re.sub(r'\s', '', email).lower()


def hash_email(email):
    return md5(email.encode('utf-8')).hexdigest()
