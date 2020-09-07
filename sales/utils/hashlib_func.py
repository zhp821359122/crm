import hashlib


def set_md5(values):
    salt = 'username'
    md5_value = hashlib.md5(salt.encode('utf-8'))
    md5_value.update(values.encode('utf-8'))
    return md5_value.hexdigest()
