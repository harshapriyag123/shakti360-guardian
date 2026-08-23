import jwt
import pytest
from app.auth import create_access_token, decode_access_token, hash_password, new_refresh_token, token_hash, verify_password

def test_argon2_hashes_are_salted():
    first = hash_password("StrongPassword42")
    second = hash_password("StrongPassword42")
    assert first != second

def test_password_verification_accepts_correct_password():
    hashed = hash_password("StrongPassword42")
    assert verify_password(hashed, "StrongPassword42") is True

def test_password_verification_rejects_wrong_password():
    hashed = hash_password("StrongPassword42")
    assert verify_password(hashed, "WrongPassword42") is False

def test_password_verification_rejects_invalid_hash():
    assert verify_password("not-a-hash", "StrongPassword42") is False

def test_access_token_round_trip():
    token = create_access_token("user-123")
    assert decode_access_token(token) == "user-123"

def test_invalid_access_token_is_rejected():
    with pytest.raises(jwt.PyJWTError):
        decode_access_token("invalid.token.value")

def test_refresh_tokens_are_unique_and_high_entropy():
    first, second = new_refresh_token(), new_refresh_token()
    assert first != second
    assert len(first) >= 60 and len(second) >= 60

def test_refresh_token_hash_is_deterministic_and_non_reversible_representation():
    token = new_refresh_token()
    assert token_hash(token) == token_hash(token)
    assert token not in token_hash(token)
    assert len(token_hash(token)) == 64
