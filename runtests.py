#!/usr/bin/env python

from __future__ import unicode_literals

import logging
import os
import sys


logging.disable(logging.CRITICAL)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], "test", "tests"])
