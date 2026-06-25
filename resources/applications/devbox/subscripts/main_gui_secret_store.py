from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import base64
import getpass
import hashlib
import hmac
import json
import os
import socket
import sqlite3


LOCAL_KEY_ALGORITHM = "CYXNTROL_DEVBOX_LOCAL_SYMMETRIC_V1"
SECRET_ALGORITHM = "CYXNTROL_MANUFACTURER_SECRET_V1"
INTERNAL_NAME = "__devbox_internal_key__"


def b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii")


def b64d(data: str) -> bytes:
    return base64.urlsafe_b64decode(str(data).encode("ascii"))


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def local_material() -> bytes:
    material = "|".join(
        [
            "CYXnTrol",
            "DevBox",
            "create_devdbase",
            getpass.getuser(),
            socket.gethostname(),
            os.environ.get("USERDOMAIN", ""),
            os.environ.get("COMPUTERNAME", ""),
        ]
    )
    return material.encode("utf-8")


def make_hmac_stream(key: bytes, nonce: bytes, length: int) -> bytes:
    output = bytearray()
    counter = 0
    while len(output) < length:
        output.extend(
            hmac.new(
                key,
                nonce + counter.to_bytes(8, "big"),
                hashlib.sha256,
            ).digest()
        )
        counter += 1
    return bytes(output[:length])


def xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def parse_payload(payload: bytes | str) -> dict:
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    return json.loads(str(payload))


def decrypt_internal_key_payload(payload: bytes) -> bytes:
    data = parse_payload(payload)
    if data.get("algorithm") != LOCAL_KEY_ALGORITHM:
        raise ValueError("Unsupported internal key algorithm.")

    salt = b64d(data["salt"])
    nonce = b64d(data["nonce"])
    cipher_data = b64d(data["ciphertext"])
    tag = b64d(data["tag"])
    iterations = int(data["iterations"])
    key_id = str(data["key_id"])
    created_at = str(data["created_at"])

    key = hashlib.pbkdf2_hmac(
        "sha256",
        local_material(),
        salt,
        iterations,
        dklen=32,
    )
    expected_tag = hmac.new(
        key,
        b"CYXNTROL_DEVBOX_KEY_V1"
        + salt
        + nonce
        + cipher_data
        + key_id.encode("utf-8")
        + created_at.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError("Internal key payload authentication failed.")

    return xor_bytes(cipher_data, make_hmac_stream(key, nonce, len(cipher_data)))


def load_secret_key(connection: sqlite3.Connection, table_name: str) -> bytes:
    cursor = connection.execute(
        f"""
        SELECT {quote_identifier('devbox_key_payload')}
        FROM {quote_identifier(table_name)}
        WHERE {quote_identifier('devbox_key_payload')} IS NOT NULL
        ORDER BY CASE
            WHEN {quote_identifier('manufacturer_name')} = ? THEN 0
            ELSE 1
        END, rowid ASC
        LIMIT 1
        """,
        (INTERNAL_NAME,),
    )
    row = cursor.fetchone()
    if row is None or row[0] is None:
        raise ValueError("DevBox-Schlüssel nicht gefunden.")
    return decrypt_internal_key_payload(row[0])


def derive_secret_key(secret_key: bytes, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        secret_key,
        salt,
        180000,
        dklen=32,
    )


def encrypt_secret_text(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    plain_text: str,
) -> bytes:
    secret_key = load_secret_key(connection, table_name)
    plain_data = plain_text.encode("utf-8")
    salt = os.urandom(32)
    nonce = os.urandom(16)
    key = derive_secret_key(secret_key, salt)
    cipher_data = xor_bytes(plain_data, make_hmac_stream(key, nonce, len(plain_data)))
    tag = hmac.new(
        key,
        b"CYXNTROL_MANUFACTURER_SECRET_V1"
        + column_name.encode("utf-8")
        + salt
        + nonce
        + cipher_data,
        hashlib.sha256,
    ).digest()
    payload = {
        "version": 1,
        "algorithm": SECRET_ALGORITHM,
        "column": column_name,
        "salt": b64e(salt),
        "nonce": b64e(nonce),
        "ciphertext": b64e(cipher_data),
        "tag": b64e(tag),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def decrypt_secret_text(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    payload: bytes,
) -> str:
    data = parse_payload(payload)
    if data.get("algorithm") != SECRET_ALGORITHM:
        raise ValueError("Unsupported secret payload algorithm.")
    if str(data.get("column")) != column_name:
        raise ValueError("Secret payload belongs to another column.")

    secret_key = load_secret_key(connection, table_name)
    salt = b64d(data["salt"])
    nonce = b64d(data["nonce"])
    cipher_data = b64d(data["ciphertext"])
    tag = b64d(data["tag"])
    key = derive_secret_key(secret_key, salt)
    expected_tag = hmac.new(
        key,
        b"CYXNTROL_MANUFACTURER_SECRET_V1"
        + column_name.encode("utf-8")
        + salt
        + nonce
        + cipher_data,
        hashlib.sha256,
    ).digest()

    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError("Secret payload authentication failed.")

    plain_data = xor_bytes(cipher_data, make_hmac_stream(key, nonce, len(cipher_data)))
    return plain_data.decode("utf-8")


def read_encrypted_column_value(
    connection: sqlite3.Connection,
    table_name: str,
    rowid: int | None,
    column_name: str,
) -> bytes | None:
    if rowid is None:
        return None
    cursor = connection.execute(
        f"""
        SELECT {quote_identifier(column_name)}
        FROM {quote_identifier(table_name)}
        WHERE rowid = ?
        """,
        (rowid,),
    )
    row = cursor.fetchone()
    if row is None or row[0] is None:
        return None
    return bytes(row[0]) if isinstance(row[0], memoryview) else row[0]
