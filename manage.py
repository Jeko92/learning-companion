#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    # Imported late so the settings module is set before Django loads.
    from django.core.management import execute_from_command_line  # noqa: PLC0415

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
