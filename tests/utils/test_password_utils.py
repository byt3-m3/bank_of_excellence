from boe.utils.password_utils import hash_password, verify_password_hash, get_key_salt_from_value

from pytest import fixture


@fixture
def password_text():
    return 'TEST_PASSWORD'


def test_hash_password(password_text):
    stored_key = hash_password(password_text)
    assert isinstance(stored_key, bytes)
    assert len(stored_key) == 64


def test_get_key_salt_from_stored_key(password_text):
    stored_key = hash_password(password_text)
    key, salt = get_key_salt_from_value(stored_key=stored_key)
    assert isinstance(key, bytes)
    assert len(key) == 32
    assert isinstance(salt, bytes)
    assert len(salt, ) == 32


def test_verify_password_hash(password_text):
    stored_key = hash_password(password_text)
    key, salt = get_key_salt_from_value(stored_key=stored_key)
    assert verify_password_hash(password=password_text, salt=salt, old_key=key) is True


def test_verify_password_hash_bad_password(password_text):
    stored_key = hash_password(password_text)
    key, salt = get_key_salt_from_value(stored_key=stored_key)
    assert verify_password_hash(password='BAD_PASS', salt=salt, old_key=key) is False
