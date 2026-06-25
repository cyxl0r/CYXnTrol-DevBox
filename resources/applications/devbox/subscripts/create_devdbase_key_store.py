import sqlite3
import sys

from create_devdbase_crypto import (
    INTERNAL_KEY_ALGORITHM,
    b64d,
    encrypt_bytes_symmetric,
)
from create_devdbase_schema import (
    get_existing_columns,
    quote_identifier,
    sync_table_schema,
)


INTERNAL_KEY_ROW_ID = 0
INTERNAL_KEY_ROW_NAME = "__devbox_internal_key__"
INTERNAL_KEY_COLUMNS = [
    ("devbox_key_id", "TEXT"),
    ("devbox_key_payload", "BLOB"),
    ("devbox_key_created_at", "TEXT"),
    ("devbox_key_algorithm", "TEXT"),
]


def ensure_manufacturer_key_columns(
    connection: sqlite3.Connection,
    manufacturer_table_name: str,
) -> None:
    sync_table_schema(
        connection=connection,
        table_name=manufacturer_table_name,
        memory_table=INTERNAL_KEY_COLUMNS,
    )


def manufacturer_key_payload_exists(
    connection: sqlite3.Connection,
    manufacturer_table_name: str,
) -> bool:
    columns = get_existing_columns(
        connection=connection,
        table_name=manufacturer_table_name,
    )

    if "devbox_key_payload" not in columns:
        return False

    cursor = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM {quote_identifier(manufacturer_table_name)}
        WHERE {quote_identifier("devbox_key_payload")} IS NOT NULL
        """
    )

    row = cursor.fetchone()

    if row is None:
        return False

    return int(row[0]) > 0


def find_internal_manufacturer_rowid(
    connection: sqlite3.Connection,
    manufacturer_table_name: str,
) -> int | None:
    columns = get_existing_columns(
        connection=connection,
        table_name=manufacturer_table_name,
    )

    where_parts = []
    parameters = []

    if "manufacturer_id" in columns:
        where_parts.append(f"{quote_identifier('manufacturer_id')} = ?")
        parameters.append(INTERNAL_KEY_ROW_ID)

    if "manufacturer_name" in columns:
        where_parts.append(f"{quote_identifier('manufacturer_name')} = ?")
        parameters.append(INTERNAL_KEY_ROW_NAME)

    if not where_parts:
        return None

    where_sql = " OR ".join(where_parts)

    cursor = connection.execute(
        f"""
        SELECT rowid
        FROM {quote_identifier(manufacturer_table_name)}
        WHERE {where_sql}
        LIMIT 1
        """,
        parameters,
    )

    row = cursor.fetchone()

    if row is None:
        return None

    return int(row[0])


def build_internal_key_values(
    columns: dict[str, str],
    key_id: str,
    encrypted_payload: bytes,
    created_at: str,
) -> dict[str, object]:
    values = {}

    if "manufacturer_id" in columns:
        values["manufacturer_id"] = INTERNAL_KEY_ROW_ID

    if "manufacturer_name" in columns:
        values["manufacturer_name"] = INTERNAL_KEY_ROW_NAME

    if "manufacturer_display_name" in columns:
        values["manufacturer_display_name"] = "DevBox internal key storage"

    if "manufacturer_legal_name" in columns:
        values["manufacturer_legal_name"] = "DevBox internal key storage"

    if "manufacturer_brand_name" in columns:
        values["manufacturer_brand_name"] = "DevBox"

    if "active" in columns:
        values["active"] = 0

    if "notes" in columns:
        values["notes"] = "Internal DevBox key record."

    if "created_at" in columns:
        values["created_at"] = created_at

    if "updated_at" in columns:
        values["updated_at"] = created_at

    values["devbox_key_id"] = key_id
    values["devbox_key_payload"] = encrypted_payload
    values["devbox_key_created_at"] = created_at
    values["devbox_key_algorithm"] = INTERNAL_KEY_ALGORITHM

    return values


def update_internal_key_row(
    connection: sqlite3.Connection,
    manufacturer_table_name: str,
    rowid: int,
    values: dict[str, object],
) -> None:
    assignments = ", ".join(
        f"{quote_identifier(column_name)} = ?"
        for column_name in values
    )
    parameters = list(values.values())
    parameters.append(rowid)

    connection.execute(
        f"""
        UPDATE {quote_identifier(manufacturer_table_name)}
        SET {assignments}
        WHERE rowid = ?
        """,
        parameters,
    )
    print(f"Updated encrypted DevBox key in table: {manufacturer_table_name}")


def insert_internal_key_row(
    connection: sqlite3.Connection,
    manufacturer_table_name: str,
    values: dict[str, object],
) -> None:
    column_sql = ", ".join(
        quote_identifier(column_name)
        for column_name in values
    )
    placeholder_sql = ", ".join("?" for _ in values)

    connection.execute(
        f"""
        INSERT INTO {quote_identifier(manufacturer_table_name)}
        ({column_sql})
        VALUES ({placeholder_sql})
        """,
        list(values.values()),
    )
    print(f"Inserted encrypted DevBox key into table: {manufacturer_table_name}")


def insert_or_update_internal_key_row(
    connection: sqlite3.Connection,
    manufacturer_table_name: str,
    key_id: str,
    encrypted_payload: bytes,
    created_at: str,
) -> None:
    columns = get_existing_columns(
        connection=connection,
        table_name=manufacturer_table_name,
    )

    values = build_internal_key_values(
        columns=columns,
        key_id=key_id,
        encrypted_payload=encrypted_payload,
        created_at=created_at,
    )

    rowid = find_internal_manufacturer_rowid(
        connection=connection,
        manufacturer_table_name=manufacturer_table_name,
    )

    if rowid is not None:
        update_internal_key_row(
            connection=connection,
            manufacturer_table_name=manufacturer_table_name,
            rowid=rowid,
            values=values,
        )
        return

    insert_internal_key_row(
        connection=connection,
        manufacturer_table_name=manufacturer_table_name,
        values=values,
    )


def validate_key_record(key_record: dict) -> tuple[str, str, str]:
    required_keys = {"key_id", "key_material_b64", "created_at"}
    missing_keys = required_keys - set(key_record.keys())

    if missing_keys:
        print(f"Key generator returned incomplete data: {missing_keys}")
        sys.exit(1)

    key_id = str(key_record["key_id"]).strip()
    key_material_b64 = str(key_record["key_material_b64"]).strip()
    created_at = str(key_record["created_at"]).strip()

    if not key_id or not key_material_b64 or not created_at:
        print("Key generator returned empty values.")
        sys.exit(1)

    return key_id, key_material_b64, created_at


def generate_and_store_manufacturer_key(
    connection: sqlite3.Connection,
    manufacturer_table_name: str,
) -> None:
    ensure_manufacturer_key_columns(
        connection=connection,
        manufacturer_table_name=manufacturer_table_name,
    )

    if manufacturer_key_payload_exists(
        connection=connection,
        manufacturer_table_name=manufacturer_table_name,
    ):
        print(f"Encrypted DevBox key already exists in table: {manufacturer_table_name}")
        return

    import create_devdbase_kgen

    key_id, key_material_b64, created_at = validate_key_record(
        create_devdbase_kgen.generate_key_record()
    )

    encrypted_payload = encrypt_bytes_symmetric(
        plain_data=b64d(key_material_b64),
        key_id=key_id,
        created_at=created_at,
    )

    insert_or_update_internal_key_row(
        connection=connection,
        manufacturer_table_name=manufacturer_table_name,
        key_id=key_id,
        encrypted_payload=encrypted_payload,
        created_at=created_at,
    )
