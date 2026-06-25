import base64
import getpass
import hashlib
import hmac
import json
import os
import socket


INTERNAL_KEY_ALGORITHM = "CYXNTROL_DEVBOX_LOCAL_SYMMETRIC_V1"


def b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii")


def b64d(data: str) -> bytes:
    return base64.urlsafe_b64decode(data.encode("ascii"))


def get_local_encryption_material() -> bytes:
    user_name = getpass.getuser()
    computer_name = socket.gethostname()
    user_domain = os.environ.get("USERDOMAIN", "")
    computer_env = os.environ.get("COMPUTERNAME", "")

    material = "|".join(
        [
            "CYXnTrol",
            "DevBox",
            "create_devdbase",
            user_name,
            computer_name,
            user_domain,
            computer_env,
        ]
    )

    return material.encode("utf-8")


def derive_symmetric_key(
    salt: bytes,
    iterations: int,
) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        get_local_encryption_material(),
        salt,
        iterations,
        dklen=32,
    )


def make_hmac_stream(
    key: bytes,
    nonce: bytes,
    length: int,
) -> bytes:
    output = bytearray()
    counter = 0

    while len(output) < length:
        counter_bytes = counter.to_bytes(8, "big")
        block = hmac.new(
            key,
            nonce + counter_bytes,
            hashlib.sha256,
        ).digest()
        output.extend(block)
        counter += 1

    return bytes(output[:length])


def xor_bytes(
    left: bytes,
    right: bytes,
) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def encrypt_bytes_symmetric(
    plain_data: bytes,
    key_id: str,
    created_at: str,
) -> bytes:
    iterations = 250000
    salt = os.urandom(32)
    nonce = os.urandom(16)

    encryption_key = derive_symmetric_key(
        salt=salt,
        iterations=iterations,
    )

    key_stream = make_hmac_stream(
        key=encryption_key,
        nonce=nonce,
        length=len(plain_data),
    )

    cipher_data = xor_bytes(
        plain_data,
        key_stream,
    )

    tag = hmac.new(
        encryption_key,
        b"CYXNTROL_DEVBOX_KEY_V1"
        + salt
        + nonce
        + cipher_data
        + key_id.encode("utf-8")
        + created_at.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    payload = {
        "version": 1,
        "algorithm": INTERNAL_KEY_ALGORITHM,
        "kdf": "PBKDF2-HMAC-SHA256",
        "iterations": iterations,
        "salt": b64e(salt),
        "nonce": b64e(nonce),
        "ciphertext": b64e(cipher_data),
        "tag": b64e(tag),
        "key_id": key_id,
        "created_at": created_at,
    }

    return json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")
