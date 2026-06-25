#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Timestamp Provider

This script can be imported by other Python scripts to generate date and time strings.

Usage as import:
    from timestamp_provider import generate_timestamp
    date_value = generate_timestamp(variant=4)

Usage for combined timestamps:
    from timestamp_provider import generate_combined_timestamp
    time_stamp = generate_combined_timestamp(variants=[4, 14])

Variants:
    1  = German date format
    2  = German date format for filenames, without spaces, using underscores
    3  = International date format
    4  = International date format for filenames, without spaces, using underscores
    5  = Time resolved to minutes, filename-safe, using underscores
    6  = Time resolved to minutes, filename-safe, using underscores
    7  = Time resolved to seconds, filename-safe, using underscores
    8  = Time resolved to tenths of a second, filename-safe, using underscores
    9  = Time resolved to hundredths of a second
    10 = Time resolved to minutes, filename-safe, using underscores
    11 = Time resolved to minutes, filename-safe, using underscores
    12 = Time resolved to seconds, filename-safe, using underscores
    13 = Time resolved to tenths of a second, filename-safe, using underscores
    14 = Time resolved to hundredths of a second, filename-safe, using underscores
"""

from __future__ import annotations

import argparse
from datetime import datetime


def get_current_datetime() -> datetime:
    return datetime.now()


def generate_timestamp(variant: int, moment: datetime | None = None) -> str:
    if not isinstance(variant, int):
        raise TypeError("variant must be an integer.")

    if moment is None:
        moment = get_current_datetime()

    hundredth = moment.microsecond // 10000
    tenth = moment.microsecond // 100000

    if variant == 1:
        return moment.strftime("%d.%m.%Y")

    if variant == 2:
        return moment.strftime("%d_%m_%Y")

    if variant == 3:
        return moment.strftime("%Y-%m-%d")

    if variant == 4:
        return moment.strftime("%Y_%m_%d")

    if variant in (5, 6, 10, 11):
        return moment.strftime("%H_%M")

    if variant in (7, 12):
        return moment.strftime("%H_%M_%S")

    if variant in (8, 13):
        return f"{moment.strftime('%H_%M_%S')}_{tenth}"

    if variant == 9:
        return f"{moment.strftime('%H:%M:%S')}.{hundredth:02d}"

    if variant == 14:
        return f"{moment.strftime('%H_%M_%S')}_{hundredth:02d}"

    raise ValueError("variant must be between 1 and 14.")


def generate_combined_timestamp(variants: list[int], separator: str = "_") -> str:
    moment = get_current_datetime()
    return separator.join(
        generate_timestamp(
            variant=variant,
            moment=moment,
        )
        for variant in variants
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("variant", type=int, nargs="*")
    parser.add_argument("--separator", default="_")
    args = parser.parse_args()

    if not args.variant:
        raise ValueError("At least one variant is required.")

    print(generate_combined_timestamp(variants=args.variant, separator=args.separator))


if __name__ == "__main__":
    main()