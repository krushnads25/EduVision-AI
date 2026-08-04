"""
logger.py

Simple logger used by the parser engine.
"""

from __future__ import annotations

import sys
from datetime import datetime


class Logger:

    def __init__(self, verbose: bool = False):

        self.verbose = verbose

    # ---------------------------------------------------------

    def _write(self, level: str, message: str):

        now = datetime.now().strftime("%H:%M:%S")

        print(
            f"[{now}] {level:<7} {message}",
            file=sys.stdout,
        )

    # ---------------------------------------------------------

    def info(self, message: str):

        self._write("INFO", message)

    # ---------------------------------------------------------

    def warn(self, message: str):

        self._write("WARNING", message)

    # ---------------------------------------------------------

    def error(self, message: str):

        self._write("ERROR", message)

    # ---------------------------------------------------------

    def debug(self, message: str):

        if self.verbose:

            self._write("DEBUG", message)


# Default logger

logger = Logger()

def set_verbose(enabled: bool):

    global logger

    logger = Logger(verbose=enabled)