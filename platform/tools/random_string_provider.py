#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Random String Provider

This script can be imported by other Python scripts to generate random strings.

Usage as import:
    from random_string_provider import generate_string
    key = generate_string(length=18, variant=1)

Usage for multiple strings:
    from random_string_provider import generate_strings
    keys = generate_strings(count=2, length=35, variant=1)

Variants:
    1 = digits, lowercase letters and uppercase letters
    2 = digits, lowercase letters, uppercase letters and special characters

The generated strings do not contain whitespace.
"""

from __future__ import annotations

import secrets
import string


BASIC_CHARSET = string.digits + string.ascii_lowercase + string.ascii_uppercase
EXTENDED_CHARSET = BASIC_CHARSET + string.punctuation


def generate_string(length: int, variant: int = 1) -> str:
    if not isinstance(length, int):
        raise TypeError("length must be an integer.")

    if length <= 0:
        raise ValueError("length must be greater than zero.")

    if variant == 1:
        charset = BASIC_CHARSET
    elif variant == 2:
        charset = EXTENDED_CHARSET
    else:
        raise ValueError("variant must be 1 or 2.")

    return "".join(secrets.choice(charset) for _ in range(length))


def generate_strings(count: int, length: int, variant: int = 1) -> list[str]:
    if not isinstance(count, int):
        raise TypeError("count must be an integer.")

    if count <= 0:
        raise ValueError("count must be greater than zero.")

    return [
        generate_string(
            length=length,
            variant=variant,
        )
        for _ in range(count)
    ]