from pathlib import Path
import base64
import json
import os
import sys
import time
import uuid


def find_project_root() -> Path:
    home_path = Path(__file__).resolve().parent
    os.chdir(home_path)

    current_path = home_path

    while True:
        root_file = current_path / ".root"

        if root_file.is_file():
            content = root_file.read_text(encoding="utf-8").strip()

            if content == "project-root":
                return current_path

        parent_path = current_path.parent

        if parent_path == current_path:
            print("No project root found.")
            sys.exit(0)

        current_path = parent_path
        os.chdir(current_path)


def utc_timestamp() -> str:
    return time.strftime(
        "%Y-%m-%dT%H:%M:%SZ",
        time.gmtime(),
    )


def b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii")


def generate_key_record(
    key_length: int = 32,
) -> dict[str, str | int]:
    if key_length < 32:
        print("Key length must be at least 32 bytes.")
        sys.exit(1)

    key_material = os.urandom(key_length)

    return {
        "key_id": str(uuid.uuid4()),
        "key_material_b64": b64e(key_material),
        "key_length": key_length,
        "created_at": utc_timestamp(),
        "generator": "create_devdbase_kgen.py",
        "algorithm": "random-os-urandom",
    }


def main() -> int:
    find_project_root()
    key_record = generate_key_record()

    print(
        json.dumps(
            key_record,
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
