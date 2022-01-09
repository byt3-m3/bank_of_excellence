import base64
import os
import hashlib
import uuid
from base64 import b64encode, b64decode


def hash_password(password, salt_size: int = 32, iterations: int = 100000) -> (bytes, bytes):
    # Example generation
    salt = os.urandom(salt_size)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)

    # Store them as:
    storage = salt + key

    # Getting the values back out
    # salt_from_storage = storage[:32]  # 32 is the length of the salt
    # key_from_storage = storage[32:]
    # return key_from_storage, salt_from_storage
    return storage


def verify_password_hash(password: str, old_key: bytes, salt: bytes, iterations: int = 100000):
    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),  # Convert the password to bytes
        salt,
        iterations
    )
    if new_key == old_key:
        return True
    else:
        return False


def get_key_salt_from_value(stored_key: bytes):
    salt = stored_key[:32]
    key = stored_key[32:]
    return key, salt


# stored_key = base64.b64encode(hash_password("TEST_PASSWORD"))
# key, salt = get_key_salt_from_value(stored_key=base64.b64decode(b'LOHDYFJPwWreg8K2lJCcPlL9S75fcj4X4epT2GGxFAavkZsYgSjkDJEArlRBHoxbuvO9aoigTAMEXx8Z89Otbg=='))
#
# new_key = verify_password_hash(password="TEST_PASSWORD", salt=salt, old_key=key)
#
# print(new_key)